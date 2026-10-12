# -*- coding: utf-8 -*-
"""API 路由集合。"""

from fastapi import APIRouter

from . import contact, content, resume, stats

# 业务接口统一挂在 /api/v1 下
api_router = APIRouter(prefix="/v1")
api_router.include_router(content.router)
api_router.include_router(contact.router)
api_router.include_router(stats.router)
api_router.include_router(resume.router)

__all__ = ["api_router"]
