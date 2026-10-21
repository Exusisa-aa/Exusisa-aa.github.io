#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
逐屏截图 —— 用来快速检查每一屏的视觉效果。

用法：
    python scripts/shoot.py                  # 截全部屏
    python scripts/shoot.py --scene 3        # 只截第 3 屏
    python scripts/shoot.py --prefix after   # 输出文件名加前缀
    python scripts/shoot.py --width 420      # 用手机宽度截（检查响应式）

依赖：
    pip install websocket-client
    本机装了 Chrome。需要先把 dev server 跑起来（npm run dev:web）。

为什么用 CDP 而不是 chrome --screenshot：
    --screenshot 配合 --virtual-time-budget 时，页面里用 JS 做的滚动
    不会反映到最终渲染的帧上 —— 截出来的永远是滚动前那一屏。
    走 DevTools Protocol 就能自己控制：导航 → 等网络空闲 → 执行滚动
    → 等一帧 → 截图，每一步都踩实。
"""

import argparse
import base64
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import websocket  # websocket-client

BASE_URL = "http://127.0.0.1:5173/"
OUT_DIR = Path(__file__).resolve().parent.parent / ".shots"
DEBUG_PORT = 9222

# 分镜顺序与 content/site.yaml 的 stage.sections 对应
# 顺序要与 content/site.yaml 的 stage.sections 一致。
# 首屏 / 关于我 / 核心能力 三屏已隐藏，所以现在从项目开始。
SCENES = [
    ("00-microservice-mall", "微服务商城"),
    ("01-mycat", "Mycat 集群"),
    ("02-works", "更多作品"),
    ("03-honors", "荣誉资质"),
    ("04-selfeval", "自我评价"),
    ("05-contact", "联系"),
]

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


# ---------------------------------------------------------------- CDP 客户端


class CDP:
    """极简 DevTools Protocol 客户端 —— 只用到导航、执行 JS 和截图。"""

    def __init__(self, ws_url: str):
        # suppress_origin：不带 Origin 头，避免 Chrome 直接 403 掉握手
        self.ws = websocket.create_connection(ws_url, timeout=40, suppress_origin=True)
        self._id = 0

    def call(self, method: str, **params):
        self._id += 1
        msg_id = self._id
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params}))
        while True:
            data = json.loads(self.ws.recv())
            if data.get("id") == msg_id:
                if "error" in data:
                    raise RuntimeError(f"{method} 失败: {data['error']}")
                return data.get("result", {})

    def eval(self, expression: str):
        result = self.call(
            "Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True
        )
        return result.get("result", {}).get("value")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


# ---------------------------------------------------------------- 浏览器


def find_browser() -> str:
    for path in CHROME_CANDIDATES:
        if Path(path).exists():
            return path
    found = shutil.which("chrome") or shutil.which("msedge")
    if not found:
        raise SystemExit("没找到 Chrome / Edge，请把路径加进 CHROME_CANDIDATES")
    return found


def launch(browser: str, width: int, height: int) -> subprocess.Popen:
    profile = Path(__file__).resolve().parent.parent / ".chrome-profile"
    return subprocess.Popen(
        [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-first-run",
            "--no-default-browser-check",
            f"--remote-debugging-port={DEBUG_PORT}",
            "--remote-allow-origins=*",
            f"--user-data-dir={profile}",
            f"--window-size={width},{height}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_target(timeout: float = 25.0) -> str:
    """等 Chrome 起来并返回一个 page target 的 websocket 地址。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{DEBUG_PORT}/json", timeout=2) as resp:
                targets = json.load(resp)
            for t in targets:
                if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                    return t["webSocketDebuggerUrl"]
        except (urllib.error.URLError, ConnectionError, TimeoutError, json.JSONDecodeError):
            pass
        time.sleep(0.4)
    raise SystemExit("等不到 Chrome 的调试端口，可能被占用或浏览器启动失败")


# ---------------------------------------------------------------- 截图


def navigate(cdp: CDP, url: str) -> None:
    cdp.call("Page.enable")
    cdp.call("Runtime.enable")
    cdp.call("Page.navigate", url=url)

    # 等真正的 load 事件，而不是猜时间
    deadline = time.time() + 30
    cdp.ws.settimeout(30)
    while time.time() < deadline:
        try:
            msg = json.loads(cdp.ws.recv())
        except websocket.WebSocketTimeoutException:
            break
        if msg.get("method") == "Page.loadEventFired":
            break

    # 再给 Vue 挂载 + 内容拉取 + 字体渲染留点时间
    time.sleep(2.0)


def capture(cdp: CDP, out_path: Path) -> bool:
    # 确认页面确实有内容再截
    ready = cdp.eval("!!document.querySelector('.scene')")
    if not ready:
        print("    ! 页面还没渲染出分镜")
        return False

    result = cdp.call("Page.captureScreenshot", format="png", captureBeyondViewport=False)
    data = result.get("data")
    if not data:
        print("    ! 截图返回空")
        return False
    out_path.write_bytes(base64.b64decode(data))
    return True


def scroll_to_scene(cdp: CDP, index: int) -> None:
    """滚到第 N 屏，并确认真的滚过去了。"""
    cdp.eval(
        f"""
        (() => {{
          const scroller = document.getElementById('scroller');
          const scenes = [...document.querySelectorAll('[data-scene-index]')]
            .sort((a, b) => Number(a.dataset.sceneIndex) - Number(b.dataset.sceneIndex));
          const target = scenes[{index}];
          if (!target || !scroller) return null;
          scroller.style.scrollBehavior = 'auto';
          scroller.scrollTop = target.offsetTop;
          return scroller.scrollTop;
        }})()
        """
    )
    # 等一帧让渲染跟上
    cdp.eval("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


def main() -> int:
    ap = argparse.ArgumentParser(description="逐屏截图检查视觉效果")
    ap.add_argument("--scene", type=int, default=None, help="只截第 N 屏（从 0 数）")
    ap.add_argument("--prefix", default="", help="输出文件名前缀")
    ap.add_argument("--width", type=int, default=1440, help="视口宽度")
    ap.add_argument("--height", type=int, default=900, help="视口高度")
    ap.add_argument("--keep-open", action="store_true", help="截完不关浏览器（调试用）")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    browser = find_browser()
    print(f"浏览器: {browser}")
    print(f"视口:   {args.width}x{args.height}")
    print(f"输出到: {OUT_DIR}\n")

    targets = (
        [(SCENES[args.scene][0], args.scene, SCENES[args.scene][1])]
        if args.scene is not None
        else [(name, i, label) for i, (name, label) in enumerate(SCENES)]
    )

    proc = launch(browser, args.width, args.height)
    ok = 0
    try:
        cdp = CDP(wait_for_target())
        for name, index, label in targets:
            prefix = f"{args.prefix}-" if args.prefix else ""
            out = OUT_DIR / f"{prefix}{name}.png"

            # 每一屏都从干净的导航开始，避免上一屏的滚动状态残留
            navigate(cdp, f"{BASE_URL}?noanim")
            scroll_to_scene(cdp, index)

            print(f"[{index}] {label} -> {out.name}")
            if capture(cdp, out):
                ok += 1

        cdp.close()
    finally:
        if not args.keep_open:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()

    print(f"\n完成 {ok}/{len(targets)} 张")
    return 0 if ok == len(targets) else 1


if __name__ == "__main__":
    sys.exit(main())
