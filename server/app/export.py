# -*- coding: utf-8 -*-
"""
静态快照导出 —— ★ 让 GitHub Pages 能跑的引擎。

GitHub Pages 是纯静态托管，跑不了 FastAPI。所以构建时把 content/ 下的 YAML
渲染成 JSON 快照放进 web/public/data/，前端在没有后端时直接读这些文件。

关键点：这里不自己解析 YAML，而是 import content_loader —— 和 API 用的是
同一份加载逻辑，所以静态快照与 /api/v1/bundle 的返回**结构完全一致**。

用法：
    python -m app.export --out ../web/public/data
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .content_loader import load_all
from .models import dump


def _write(path: Path, data) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def export(out_dir: Path) -> int:
    bundle = load_all()

    # generated_at 在导出时打戳 —— 不能放在模型默认值里，
    # 否则每次读取缓存都会变，快照就没法做 diff 了。
    bundle.generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    payload = dump(bundle)
    written: list[tuple[str, int]] = []

    # 1) 聚合包 —— 前端主用这个
    written.append(("index.json", _write(out_dir / "index.json", payload)))

    # 2) 拆分文件 —— 方便按需单独拉，也方便你直接看导出结果对不对
    singles = {
        "profile.json": payload["profile"],
        "skills.json": payload["skills"],
        "honors.json": payload["honors"],
        "courses.json": payload["courses"],
        "site.json": payload["site"],
        "stage.json": payload["stage"],
        "projects.json": payload["projects"],
    }
    for name, data in singles.items():
        written.append((name, _write(out_dir / name, data)))

    # 3) 每个项目单独一份
    for project in payload["projects"]:
        written.append(
            (f"projects/{project['id']}.json", _write(out_dir / "projects" / f"{project['id']}.json", project))
        )

    total = sum(size for _, size in written)
    print(f"内容已导出到 {out_dir}")
    print(f"  版本      {bundle.version}")
    print(f"  内容哈希  {bundle.content_hash}")
    print(f"  生成时间  {bundle.generated_at}")
    print(f"  项目数    {len(payload['projects'])}")
    print(f"  分镜数    {len(payload['stage']['sections'])}")
    print(f"  文件数    {len(written)}   合计 {total / 1024:.1f} KB")
    for name, size in written:
        print(f"    - {name:<34} {size / 1024:>7.1f} KB")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="把 content/ 导出成前端可用的静态 JSON 快照")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent / "web" / "public" / "data",
        help="输出目录，默认 web/public/data",
    )
    args = parser.parse_args()
    return export(args.out.resolve())


if __name__ == "__main__":
    sys.exit(main())
