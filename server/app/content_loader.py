# -*- coding: utf-8 -*-
"""
内容加载层 —— ★ 全站唯一的 YAML → Pydantic 入口。

FastAPI 的接口和 export.py 的静态导出都走这里，绝不允许各自解析 YAML。
这是「live 模式」和「static 模式」数据完全一致的唯一保证。
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

import yaml

from .config import settings
from .models import (
    Bundle,
    Courses,
    Honors,
    Profile,
    Project,
    SiteMeta,
    Skills,
    Stage,
)


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _content_files(content_dir: Path) -> list[Path]:
    """所有参与内容哈希的文件（YAML + Markdown）。"""
    if not content_dir.exists():
        return []
    files = sorted(content_dir.rglob("*.yaml")) + sorted(content_dir.rglob("*.yml"))
    files += sorted(content_dir.rglob("*.md"))
    return [f for f in files if f.is_file()]


def content_fingerprint(content_dir: Path | None = None) -> str:
    """
    内容指纹：文件名的 hash + 每个文件的 mtime 与大小。

    用作缓存键 —— 只要内容目录里有任何文件被改动，指纹就变，缓存自动失效。
    比逐个读取内容算 sha256 快得多，且对开发时的频繁改动足够灵敏。
    """
    content_dir = content_dir or settings.content_dir
    h = hashlib.sha256()
    for f in _content_files(content_dir):
        st = f.stat()
        h.update(f"{f.relative_to(content_dir)}|{st.st_mtime_ns}|{st.st_size}\n".encode())
    return h.hexdigest()[:16]


def content_hash(content_dir: Path | None = None) -> str:
    """内容真哈希：把文件内容拼起来算 sha256，写进静态快照里做版本标记。"""
    content_dir = content_dir or settings.content_dir
    h = hashlib.sha256()
    for f in _content_files(content_dir):
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _load_projects(content_dir: Path) -> list[Project]:
    proj_dir = content_dir / "projects"
    if not proj_dir.exists():
        return []
    projects: list[Project] = []
    for path in sorted(proj_dir.glob("*.y*ml")):
        data = _read_yaml(path)
        if not data:
            continue
        data.setdefault("id", path.stem)
        projects.append(Project.model_validate(data))
    projects.sort(key=lambda p: (p.order, p.id))
    return projects


def _build_bundle(content_dir: Path) -> Bundle:
    site_raw = _read_yaml(content_dir / "site.yaml")

    return Bundle(
        version=settings.version,
        content_hash=content_hash(content_dir),
        profile=Profile.model_validate(_read_yaml(content_dir / "profile.yaml")),
        skills=Skills.model_validate(_read_yaml(content_dir / "skills.yaml")),
        honors=Honors.model_validate(_read_yaml(content_dir / "honors.yaml")),
        courses=Courses.model_validate(_read_yaml(content_dir / "courses.yaml")),
        self_evaluation=_read_text(content_dir / "self-evaluation.md"),
        site=SiteMeta.model_validate(site_raw.get("site", {})),
        stage=Stage.model_validate(site_raw.get("stage", {})),
        projects=_load_projects(content_dir),
    )


@lru_cache(maxsize=4)
def _cached_bundle(content_dir_str: str, fingerprint: str) -> Bundle:
    """fingerprint 只是缓存键的一部分，用来在内容变化时自动失效。"""
    return _build_bundle(Path(content_dir_str))


def load_all(content_dir: Path | None = None) -> Bundle:
    """
    加载全部内容。

    结果按「内容目录 + 内容指纹」缓存 —— 改了 YAML 之后下一次调用会自动重新加载，
    不需要重启服务，也不需要手动清缓存。
    """
    content_dir = content_dir or settings.content_dir
    return _cached_bundle(str(content_dir), content_fingerprint(content_dir))


def clear_cache() -> None:
    _cached_bundle.cache_clear()


# ---------------------------------------------------------------- 查询辅助


def get_project(project_id: str) -> Project | None:
    return next((p for p in load_all().projects if p.id == project_id), None)


def list_projects(
    category: str | None = None,
    featured: bool | None = None,
    limit: int | None = None,
) -> list[Project]:
    projects = load_all().projects
    if category:
        projects = [p for p in projects if category in p.category]
    if featured is not None:
        projects = [p for p in projects if p.featured is featured]
    if limit is not None:
        projects = projects[: max(limit, 0)]
    return projects
