# -*- coding: utf-8 -*-
"""内容接口 —— 全部只读，数据来自 content/ 下的 YAML。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..content_loader import load_all
from ..models import (
    Bundle,
    Courses,
    Honors,
    Profile,
    Project,
    SiteMeta,
    Skills,
    Stage,
)

router = APIRouter(tags=["content"])


@router.get("/bundle", response_model=Bundle, summary="聚合包：前端一次拉全")
async def get_bundle() -> Bundle:
    """
    ★ 前端主要用这个接口。

    静态快照 web/public/data/index.json 就是它的冻结副本，
    所以 live / static 两种模式下前端拿到的结构完全一致。
    """
    return load_all()


@router.get("/profile", response_model=Profile, summary="个人简介")
async def get_profile() -> Profile:
    return load_all().profile


@router.get("/site", summary="站点元信息")
async def get_site() -> SiteMeta:
    return load_all().site


@router.get("/stage", summary="分镜配置（顺序 + 每屏主题色）")
async def get_stage() -> Stage:
    return load_all().stage


@router.get("/skills", response_model=Skills, summary="技能分组")
async def get_skills() -> Skills:
    return load_all().skills


@router.get("/courses", response_model=Courses, summary="主修课程")
async def get_courses() -> Courses:
    return load_all().courses


@router.get("/honors", response_model=Honors, summary="荣誉资质")
async def get_honors(
    type: str | None = Query(default=None, description="award | copyright | cert"),
    featured: bool | None = Query(default=None, description="只看重点条目"),
) -> Honors:
    honors = load_all().honors.honors
    if type:
        honors = [h for h in honors if h.type == type]
    if featured is not None:
        honors = [h for h in honors if h.featured is featured]
    return Honors(honors=honors)


@router.get("/self-evaluation", summary="自我评价（Markdown 原文）")
async def get_self_evaluation() -> dict:
    return {"markdown": load_all().self_evaluation}


@router.get("/projects", response_model=list[Project], summary="项目列表")
async def get_projects(
    category: str | None = Query(default=None, description="按分类过滤，如 vision / database"),
    featured: bool | None = Query(default=None, description="true 只返回有独立分镜的主作品"),
    limit: int | None = Query(default=None, ge=1, le=100),
) -> list[Project]:
    projects = load_all().projects
    if category:
        projects = [p for p in projects if category in p.category]
    if featured is not None:
        projects = [p for p in projects if p.featured is featured]
    if limit is not None:
        projects = projects[:limit]
    return projects


@router.get("/projects/{project_id}", response_model=Project, summary="项目详情")
async def get_project_detail(project_id: str) -> Project:
    project = next((p for p in load_all().projects if p.id == project_id), None)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
    return project
