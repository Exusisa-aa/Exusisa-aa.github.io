#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成项目作品集 PDF —— 从 content/ 的数据直接生成，不是把网页打印下来。

为什么走「HTML + Chrome 打印」而不是直接写 PDF：
  中文字体、分页、图片等比缩放这些事，浏览器已经做得很好；
  用库手动排版，光字体嵌入就要折腾半天。代价是依赖本机装了 Chrome。

排版跟着网站走：
  · featured 的项目（网站上是独立分镜）→ 整页展开，文字在上、截图在下
  · 其余项目（网站上是「更多作品」轮播）→ 左图右文的紧凑卡片

项目顺序不在这里写死，而是从 site.yaml 推导，和网站保持一致。

用法：
    python scripts/build-portfolio-pdf.py
    python scripts/build-portfolio-pdf.py --out ../../作品集.pdf
"""

import argparse
import hashlib
import html
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent          # portfolio/
PUBLIC = ROOT / "web" / "public"
CONTENT = ROOT / "content"

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

# 图片嵌进 PDF 前先降一档。原始 webp 是 1920 宽，按原样嵌进去整份十几 MB；
# PDF 版面上图片最多 182mm 宽，1400px 已经足够清晰。
IMG_MAX_EDGE = 1400
IMG_QUALITY = 82


def esc(s) -> str:
    return html.escape(str(s or ""))


def find_chrome() -> str:
    for p in CHROME_CANDIDATES:
        if Path(p).exists():
            return p
    raise SystemExit("没找到 Chrome / Edge，请把路径加进 CHROME_CANDIDATES")


# ---------------------------------------------------------------- 数据


def load_data():
    profile = yaml.safe_load((CONTENT / "profile.yaml").read_text(encoding="utf-8"))
    projects = [
        yaml.safe_load(f.read_text(encoding="utf-8"))
        for f in sorted((CONTENT / "projects").glob("*.yaml"))
    ]
    return profile, ordered_like_site(projects)


def ordered_like_site(projects: list[dict]) -> list[dict]:
    """
    按网站上的展示顺序排。

    网站的顺序由 site.yaml 的 stage.sections 决定：
      · type: project  → 该项目单独一屏，顺序就是 sections 里的顺序
      · type: carousel → 「更多作品」轮播，里面按项目的 order 排

    直接读同一份配置推导，而不是再写一遍顺序 ——
    以后调分镜顺序，PDF 会自动跟上。
    """
    site = yaml.safe_load((CONTENT / "site.yaml").read_text(encoding="utf-8"))
    sections = (site.get("stage") or {}).get("sections") or []
    by_id = {p.get("id"): p for p in projects}
    by_order = sorted(projects, key=lambda p: (p.get("order", 0), p.get("id", "")))

    ordered: list[dict] = []
    seen: set[str] = set()

    def push(p):
        if not p:
            return
        pid = p.get("id")
        if pid in by_id and pid not in seen:
            ordered.append(p)
            seen.add(pid)

    for sec in sections:
        kind = sec.get("type")
        if kind == "project" and sec.get("projectId"):
            push(by_id.get(sec["projectId"]))
        elif kind == "carousel":
            for p in by_order:
                if not p.get("featured"):
                    push(p)

    # 兜底：site.yaml 里没提到的项目，按 order 追加到末尾
    for p in by_order:
        push(p)

    return ordered


# ---------------------------------------------------------------- 图片


def optimize_image(src: Path, cache_dir: Path) -> Path:
    """把一张图压成 JPEG 放进缓存目录。同一张图只转一次。"""
    from PIL import Image

    # 文件名带上源路径的哈希 —— 不同项目都有叫 cover.webp 的封面，
    # 只用 stem 会让它们互相覆盖，最后几张图变成同一张。
    key = hashlib.md5(str(src.resolve()).encode()).hexdigest()[:8]
    dst = cache_dir / f"{src.stem}-{key}.jpg"
    if dst.exists():
        return dst

    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        if max(w, h) > IMG_MAX_EDGE:
            r = IMG_MAX_EDGE / max(w, h)
            im = im.resize((int(w * r), int(h * r)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=IMG_QUALITY, optimize=True, progressive=True)
    return dst


def images_of(project, cache_dir: Path) -> list[dict]:
    """封面 + 图集，去重后返回 [{src, caption}]，src 已是压缩后的文件 URI。"""
    out, seen = [], set()

    def add(src, caption=""):
        if not src or src in seen:
            return
        path = PUBLIC / src.lstrip("/")
        if not path.exists():
            return
        seen.add(src)
        out.append({"src": optimize_image(path, cache_dir).as_uri(), "caption": caption})

    add(project.get("cover"))
    for g in (project.get("images") or []) + (project.get("gallery") or []):
        add(g.get("src"), g.get("caption") or g.get("alt") or "")
    return out


# ---------------------------------------------------------------- 样式

CSS = """
@page { size: A4; margin: 15mm 14mm 16mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Microsoft YaHei", "PingFang SC", "SimHei", sans-serif;
  font-size: 10pt; line-height: 1.75; color: #1c1f2a;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.serif { font-family: "SimSun", "Songti SC", "Noto Serif SC", serif; }
.mono  { font-family: "JetBrains Mono", Consolas, "Courier New", monospace; }

/* ---------- 封面 ---------- */
.cover { height: 262mm; display: flex; flex-direction: column; justify-content: center; }
.cover .kicker { font-family: Consolas, monospace; font-size: 8.5pt; letter-spacing: .3em;
  color: #6a7080; text-transform: uppercase; }
.cover h1 { font-family: "SimSun", "Songti SC", serif; font-size: 44pt; font-weight: 700;
  letter-spacing: .04em; margin: 10mm 0 4mm; color: #12141c; }
.cover .headline { font-size: 13pt; font-weight: 600; color: #2b3147; margin-bottom: 3mm; }
.cover .meta { font-family: Consolas, monospace; font-size: 9pt; color: #6a7080; letter-spacing: .04em; }
.cover .url { margin-top: 9mm; font-family: Consolas, monospace; font-size: 10pt;
  color: #4a55b8; border-bottom: 1px solid #c9cdf0; padding-bottom: 1mm; display: inline-block; }
.cover .rule { width: 26mm; height: 2px; background: #4a55b8; margin: 8mm 0; }

/* ---------- 整页展开的项目 ---------- */
.project { break-before: page; }
.pnum { font-family: Consolas, monospace; font-size: 8.5pt; letter-spacing: .3em;
  color: #4a55b8; font-weight: 700; }
.ptitle { font-family: "SimSun", "Songti SC", serif; font-size: 21pt; font-weight: 700;
  color: #12141c; margin: 2mm 0 1.5mm; line-height: 1.25; }
.psub { font-family: Consolas, monospace; font-size: 9pt; color: #5b6274; letter-spacing: .03em;
  margin-bottom: 4mm; }
.pdivider { height: 1px; background: #e2e4ee; margin: 4mm 0 5mm; }

.psection-label { font-family: Consolas, monospace; font-size: 8pt; letter-spacing: .18em;
  color: #8a90a4; margin-bottom: 2mm; }

.summary { font-size: 10.5pt; color: #2b3147; line-height: 1.85; margin-bottom: 5mm; }

.tags { list-style: none; display: flex; flex-wrap: wrap; gap: 1.6mm; margin-bottom: 5mm; }
.tags li { font-family: Consolas, monospace; font-size: 7.6pt; color: #3d4460;
  border: 1px solid #d6d9e6; border-radius: 99px; padding: 1mm 2.6mm; background: #f7f8fc; }

.highlights { list-style: none; margin-bottom: 5mm; }
.highlights li { position: relative; padding-left: 5mm; margin-bottom: 1.8mm;
  font-size: 9.6pt; color: #2b3147; }
.highlights li::before { content: ""; position: absolute; left: 0; top: 2.4mm;
  width: 2mm; height: 2mm; background: #4a55b8; }

.desc { font-size: 9.6pt; color: #3a4055; white-space: pre-line; margin-bottom: 5mm; }

.tech { font-family: Consolas, monospace; font-size: 8.4pt; color: #5b6274;
  background: #f5f6fa; border-left: 2px solid #4a55b8; padding: 2.4mm 3.4mm; margin-bottom: 6mm; }

/* ---------- 截图 ---------- */
figure { margin-bottom: 5mm; break-inside: avoid; }
figure img { width: 100%; border: 1px solid #d6d9e6; border-radius: 2mm; display: block; }
figcaption { font-family: Consolas, monospace; font-size: 7.6pt; color: #7b8195;
  margin-top: 1.4mm; letter-spacing: .02em; }

.footer { font-family: Consolas, monospace; font-size: 7.5pt; color: #9aa0b2;
  margin-top: 6mm; padding-top: 2.5mm; border-top: 1px solid #e2e4ee; letter-spacing: .04em; }

/* ---------- 紧凑卡片（轮播里的项目）----------
   左图右文。整宽图会把卡片撑到一页一张，又回到浪费空间的老问题。 */
.card { break-inside: avoid; padding: 6mm 0 7mm; border-top: 1px solid #e2e4ee; }
.card:first-of-type { border-top: none; }
.cnum { font-family: Consolas, monospace; font-size: 8pt; letter-spacing: .3em;
  color: #4a55b8; font-weight: 700; }
.ctitle { font-family: "SimSun", "Songti SC", serif; font-size: 15pt; font-weight: 700;
  color: #12141c; margin: 1.2mm 0 1mm; line-height: 1.3; }
.csub { font-family: Consolas, monospace; font-size: 8pt; color: #5b6274;
  letter-spacing: .03em; margin-bottom: 3.5mm; }
.cgrid { display: grid; grid-template-columns: 1.05fr 1fr; gap: 6mm; align-items: start; }
.ctext .summary { font-size: 9.4pt; line-height: 1.75; margin-bottom: 3.5mm; }
.ctext .tags { margin-bottom: 3.5mm; }
.ctext .tags li { font-size: 7pt; padding: .7mm 2.2mm; }
.ctext .tech { font-size: 7.8pt; padding: 1.8mm 2.6mm; margin-bottom: 0; }
.cmedia figure { margin-bottom: 3mm; }
.cmedia figcaption { font-size: 7pt; }

"""


# ---------------------------------------------------------------- 渲染


def _body(p, cache_dir) -> tuple[list[str], list[str]]:
    """
    渲染一个项目的正文，分成两块返回：(文字, 图片)。

    分开是因为两种版式要的排法不同：
      · 整页展开 —— 文字在上、图在下，顺序拼接
      · 紧凑卡片 —— 左图右文并排，需要各自放进一个格子
    """
    text: list[str] = []
    media: list[str] = []

    if p.get("summary"):
        text.append("<div class='psection-label'>概述</div>")
        text.append(f"<p class='summary'>{esc(p['summary'])}</p>")

    tags = p.get("tags") or []
    if tags:
        text.append("<ul class='tags'>" + "".join(f"<li>{esc(t)}</li>" for t in tags) + "</ul>")

    # 「项目要点」「技术栈」两段按需求去掉：
    # 要点内容在网站上能看，技术栈已由上面的标签药丸表达。

    desc = (p.get("description") or "").strip()
    if desc and "【待填】" not in desc:
        text.append("<div class='psection-label'>说明</div>")
        text.append(f"<div class='desc'>{esc(desc)}</div>")

    for img in images_of(p, cache_dir):
        cap = f"<figcaption>{esc(img['caption'])}</figcaption>" if img["caption"] else ""
        media.append(f"<figure><img src='{img['src']}'>{cap}</figure>")

    return text, media


def render(profile, projects, cache_dir: Path) -> str:
    name = profile.get("name", "")
    headline = profile.get("headline", "")
    location = profile.get("location", "")
    status = profile.get("status_text") or profile.get("statusText") or ""
    site = "exusisa-aa.github.io"

    parts = [
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>",
        f"<title>{esc(name)} · 项目作品集</title><style>{CSS}</style></head><body>",
        "<section class='cover'>",
        "<div class='kicker'>// 项目作品集 · Portfolio</div>",
        f"<h1 class='serif'>{esc(name)}</h1>",
        "<div class='rule'></div>",
        f"<div class='headline'>{esc(headline)}</div>",
        f"<div class='meta'>{esc(location)} · {esc(status)}</div>",
        f"<div class='url mono'>{esc(site)}</div>",
        "</section>",
    ]

    for i, p in enumerate(projects, 1):
        text, media = _body(p, cache_dir)

        if p.get("featured"):
            parts.append("<section class='project'>")
            parts.append(f"<div class='pnum'>{i:02d}</div>")
            parts.append(f"<h2 class='ptitle'>{esc(p.get('title', ''))}</h2>")
            if p.get("subtitle"):
                parts.append(f"<div class='psub'>{esc(p['subtitle'])}</div>")
            parts.append("<div class='pdivider'></div>")
            parts.extend(text)
            parts.extend(media)
            parts.append(f"<div class='footer'>{esc(name)} · 项目作品集 · {esc(site)}</div>")
            parts.append("</section>")
        else:
            parts.append("<article class='card'>")
            parts.append(f"<div class='cnum'>{i:02d}</div>")
            parts.append(f"<h3 class='ctitle'>{esc(p.get('title', ''))}</h3>")
            if p.get("subtitle"):
                parts.append(f"<div class='csub'>{esc(p['subtitle'])}</div>")
            parts.append("<div class='cgrid'>")
            parts.append("<div class='ctext'>" + "".join(text) + "</div>")
            parts.append("<div class='cmedia'>" + "".join(media) + "</div>")
            parts.append("</div>")
            parts.append("</article>")

    # 不再单独加结尾页脚 —— 整页项目的 footer 已经带过了，
    # 单独一行会独占最后一页，白费一页纸。
    parts.append("</body></html>")
    return "".join(parts)


# ---------------------------------------------------------------- 主流程


def main() -> int:
    ap = argparse.ArgumentParser(description="从 content/ 生成项目作品集 PDF")
    ap.add_argument("--out", default=str(ROOT.parent / "陈明辉-项目作品集.pdf"),
                    help="输出路径，默认放在 portfolio 的上一级目录")
    args = ap.parse_args()

    profile, projects = load_data()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome()
    print(f"浏览器: {chrome}")
    print(f"项目数: {len(projects)}")
    for i, p in enumerate(projects, 1):
        mark = "整页" if p.get("featured") else "卡片"
        print(f"  {i:02d} [{mark}] {p.get('title', '')}")

    # ⚠️ 整个流程都得在这个 with 里：压缩后的图片和 HTML 都在临时目录中，
    #    一旦提前退出，Chrome 打开 HTML 时图片已经没了 ——
    #    表现是 PDF 里图片大量缺失，而且不报错（静默丢图）。
    with tempfile.TemporaryDirectory(prefix="pdf-build-") as tmp:
        tmp_dir = Path(tmp)
        page = render(profile, projects, tmp_dir)
        tmp_html = tmp_dir / "portfolio.html"
        tmp_html.write_text(page, encoding="utf-8")

        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={out}", tmp_html.as_uri()],
            capture_output=True, timeout=180,
        )

    if not out.exists():
        print("生成失败：没有产出 PDF")
        return 1

    size = out.stat().st_size
    print(f"\n已生成: {out}  ({size / 1024 / 1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
