#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
素材处理脚本 —— 把原始截图/录屏转成 WebP 并压到合适尺寸，放进 web/public/media/。

用法：
    python scripts/prepare-assets.py            # 正常处理
    python scripts/prepare-assets.py --dry-run  # 只打印将要做什么，不写文件

设计要点：
  * 幂等：已经存在且比源文件新的输出会被跳过，可以随时重跑。
  * 只读源目录，不修改你的原始素材。
  * 长边限制 + WebP 质量 82，观感基本无损，体积通常降到原来的 1/10。

⚠️ 视频目前是「原样复制」，没有压缩。装了 ffmpeg 之后可以解开下面的
   compress_video()，把 mp4 压到 1280 宽再发布，否则 GitHub Pages 上首屏会拖慢。
"""

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image

# ---------------------------------------------------------------- 路径

ROOT = Path(__file__).resolve().parent.parent          # portfolio/
MEDIA = ROOT / "web" / "public" / "media"
FILES = ROOT / "web" / "public" / "files"
STUDY = Path("k:/study")                               # 原始素材所在目录

MAX_EDGE = 1920     # 长边上限（px）
QUALITY = 82        # WebP 质量（照片类）
# 终端/控制台截图以文字为主，质量给低会把字压糊，单独用高一档
SHOT_QUALITY = 90

RESUME_DIR = ROOT.parent    # k:/study/简历/

# ---------------------------------------------------------------- 映射表
# (源文件, 目标相对路径)。目标路径相对 web/public/media/。
# 源文件不存在时只警告，不报错 —— 方便你陆续补素材。

# ⚠️ 水下养殖鱼检测平台的那批素材（架构图 / 检测结果 / 鱼病图 / 逐帧切图 / 录像）
#    已从仓库移出到 简历/未使用素材/ —— 原因是该项目的 featured: false，
#    走轮播、只渲染 cover，这些图一张都不会显示，却要跟着仓库被下载。
#
#    所以这里对应的映射**全部注释掉**，否则你跑一次 npm run assets 就会
#    把 10.4 MB 原样生成回去，前面的瘦身白做。
#
#    把该项目升回独立分镜时，解开注释即可（原始素材仍在 k:/study/yolo/ 下）。
IMAGES: list[tuple[Path, str]] = [
    # ---- 水下养殖鱼检测平台（已移出仓库，见上方说明）----
    # (STUDY / "yolo/架构图/Bionic-yolo架构图 .png",     "projects/underwater-yolo/arch/bionic-yolo.webp"),
    # (STUDY / "yolo/架构图/yolov8中文 .png",            "projects/underwater-yolo/arch/yolov8.webp"),
    # (STUDY / "yolo/架构图/yolo26n中文 .png",           "projects/underwater-yolo/arch/yolo26n.webp"),
    # (STUDY / "yolo/架构图/yolo26n注意力机制.png",       "projects/underwater-yolo/arch/attention.webp"),
    # (STUDY / "yolo/架构图/公式.jpg",                   "projects/underwater-yolo/arch/formula.webp"),
    # (STUDY / "yolo/结果图/最好结果.png",               "projects/underwater-yolo/results/best.webp"),
    # (STUDY / "yolo/结果图/中结果.png",                 "projects/underwater-yolo/results/mid.webp"),
    # (STUDY / "yolo/结果图/最次结果.png",               "projects/underwater-yolo/results/worst.webp"),
    # (STUDY / "yolo/结果图/鱼群.png",                   "projects/underwater-yolo/results/fish-school.webp"),
    # (STUDY / "yolo/测试图/寄生虫病.png",               "projects/underwater-yolo/tests/parasite.webp"),
    # (STUDY / "yolo/测试图/烂鳃病 .png",                "projects/underwater-yolo/tests/gill-rot.webp"),
    # (STUDY / "yolo/测试图/白尾病.png",                 "projects/underwater-yolo/tests/white-tail.webp"),
]

# 逐帧切图：各取前 N 帧，命名 net-00 / fish-00 …（net=网衣，fish=鱼病）
# 同上，已停用
FRAMES: list[tuple[Path, str, int]] = [
    # (STUDY / "yolo/网衣视频截图", "projects/underwater-yolo/frames", 6),
    # (STUDY / "yolo/魚病视频切图", "projects/underwater-yolo/frames", 6),
]

# 项目运行截图。
#
# ⚠️ 源文件一律放在各自命名的子目录里，不要直接丢在 简历/ 根目录。
#    之前微服务那批图就放根目录叫 1.png ~ 7.png，后来被新素材同名覆盖，
#    再跑这个脚本就会把已生成的 webp 覆盖成完全不相干的图。
#    子目录 + 语义化文件名 = 不会再撞车。
#
# 各项目的截图命名顺序就是轮播的展示顺序，改顺序请连 caption 一起改
# （见 content/projects/*.yaml 的 gallery）。
PROJECT_SHOTS: list[tuple[Path, str]] = [
    # ---- 微服务商城平台：7 张运行截图 ----
    (RESUME_DIR / "微服务商城截图" / "1.png", "projects/microservice-mall/01-docker-ps.webp"),
    (RESUME_DIR / "微服务商城截图" / "2.png", "projects/microservice-mall/02-redis-cluster.webp"),
    (RESUME_DIR / "微服务商城截图" / "3.png", "projects/microservice-mall/03-nacos-config.webp"),
    (RESUME_DIR / "微服务商城截图" / "4.png", "projects/microservice-mall/04-sentinel.webp"),
    (RESUME_DIR / "微服务商城截图" / "5.png", "projects/microservice-mall/05-seata.webp"),
    (RESUME_DIR / "微服务商城截图" / "6.png", "projects/microservice-mall/06-rabbitmq.webp"),
    (RESUME_DIR / "微服务商城截图" / "7.png", "projects/microservice-mall/07-elasticsearch.webp"),

    # ---- Mycat 数据库集群 ----
    # 输出名按内容起，不跟归档序号 —— 归档序号会变，内容不会。
    (RESUME_DIR / "数据库集群截图" / "01-架构图.png",     "projects/mycat-cluster/01-architecture.webp"),
    (RESUME_DIR / "数据库集群截图" / "03-schema配置.png", "projects/mycat-cluster/02-schema-xml.webp"),
    (RESUME_DIR / "数据库集群截图" / "02-mycateye监控.png", "projects/mycat-cluster/03-mycateye.webp"),

    # ---- 「更多作品」轮播封面：一个项目一张 ----
    # 文件名本身就是说明，别再改回 1.png / 2.png 这种 —— 撞过一次了。
    (RESUME_DIR / "数字化水产养殖平台.png",              "projects/underwater-yolo/cover.webp"),
    (RESUME_DIR / "中惠云启科技集团的后台管理系统.png",   "projects/zhonghui-admin/cover.webp"),
    (RESUME_DIR / "中惠云启科技集团的数据可视化平台.png", "projects/zhonghui-datav/cover.webp"),
    (RESUME_DIR / "中惠云启科技集团的招投标网.png",       "projects/zhonghui-bidding/cover.webp"),
]

# 视频：原样复制（见文件头说明）
# 同样已随检测平台一起移出仓库 —— 8.9 MB 是单个最大的文件，占了整仓的一半。
VIDEOS: list[tuple[Path, str]] = [
    # (STUDY / "yolo/测试图/烂鳃病1.mp4", "video/underwater-yolo.mp4"),
]

# 简历 PDF
PDFS: list[tuple[Path, str]] = [
    (ROOT.parent / "最最最终版/陈明辉-Java全栈开发工程师与Agent智能体开发-简历.pdf",
     "ChenMinghui-Resume.pdf"),
]


# ---------------------------------------------------------------- 工具


def is_fresh(src: Path, dst: Path) -> bool:
    """输出比源文件新就跳过，保证脚本可重跑。"""
    return dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime


def convert_image(src: Path, dst: Path, dry: bool, quality: int = QUALITY) -> str:
    if not src.exists():
        return f"  [跳过] 源文件不存在: {src}"
    if is_fresh(src, dst):
        return f"  [最新] {dst.name}"

    with Image.open(src) as im:
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        w, h = im.size
        if max(w, h) > MAX_EDGE:
            ratio = MAX_EDGE / max(w, h)
            im = im.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

        before = src.stat().st_size
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.save(dst, "WEBP", quality=quality, method=6)

    if dry:
        return f"  [将转换] {src.name}  ({before // 1024} KB) -> {dst}"
    after = dst.stat().st_size
    return (
        f"  [转换] {src.name}  {before // 1024} KB -> {after // 1024} KB"
        f"  ({100 * after // max(before, 1)}%)"
    )


def copy_file(src: Path, dst: Path, dry: bool, label: str = "复制") -> str:
    if not src.exists():
        return f"  [跳过] 源文件不存在: {src}"
    if is_fresh(src, dst):
        return f"  [最新] {dst.name}"
    if not dry:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    size_mb = src.stat().st_size / 1024 / 1024
    return f"  [{label}] {src.name} -> {dst.name}  ({size_mb:.1f} MB)"


# ---------------------------------------------------------------- 主流程


def main() -> int:
    ap = argparse.ArgumentParser(description="把原始素材转换成站点可用的 WebP")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写文件")
    args = ap.parse_args()
    dry = args.dry_run

    if dry:
        print("=== DRY RUN（不会写任何文件）===\n")

    missing = 0

    print("[1/5] 单图转换")
    for src, rel in IMAGES:
        line = convert_image(src, MEDIA / rel, dry)
        if "不存在" in line:
            missing += 1
        print(line)

    print("\n[2/5] 项目运行截图")
    for src, rel in PROJECT_SHOTS:
        line = convert_image(src, MEDIA / rel, dry, quality=SHOT_QUALITY)
        if "不存在" in line:
            missing += 1
        print(line)

    print("\n[3/5] 逐帧切图")
    for src_dir, rel_dir, limit in FRAMES:
        if not src_dir.exists():
            print(f"  [跳过] 目录不存在: {src_dir}")
            missing += 1
            continue
        frames = sorted(src_dir.glob("frame_*.jpg"))[:limit]
        if not frames:
            print(f"  [跳过] 目录里没有 frame_*.jpg: {src_dir}")
            missing += 1
            continue
        prefix = "net" if "网衣" in src_dir.name else "fish"
        for i, frame in enumerate(frames):
            dst = MEDIA / rel_dir / f"{prefix}-{i:02d}.webp"
            line = convert_image(frame, dst, dry)
            if "不存在" in line:
                missing += 1
            print(line)

    print("\n[4/5] 视频（未压缩，原样复制）")
    for src, rel in VIDEOS:
        line = copy_file(src, MEDIA / rel, dry)
        if "不存在" in line:
            missing += 1
        print(line)

    print("\n[5/5] 简历 PDF")
    for src, name in PDFS:
        line = copy_file(src, FILES / name, dry)
        if "不存在" in line:
            missing += 1
        print(line)

    if missing:
        print(f"\n⚠️  {missing} 项源文件缺失（已跳过）。补上素材后重跑本脚本即可。")

    print("\n完成。输出目录:", MEDIA if not dry else "(dry-run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
