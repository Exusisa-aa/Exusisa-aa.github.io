# -*- coding: utf-8 -*-
"""访客统计 —— 只做一个简单的总计/今日计数，不做用户追踪。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..db import add_visit, get_session, visit_summary
from ..models import StatsResponse, VisitRequest

router = APIRouter(tags=["stats"])


@router.post("/stats/visit", response_model=StatsResponse, summary="记一次访问")
def record_visit(
    request: Request,
    payload: VisitRequest,
    session: Session = Depends(get_session),
) -> StatsResponse:
    total, today = add_visit(
        session,
        path=payload.path,
        referrer=payload.referrer,
        ip=request.client.host if request.client else "",
    )
    return StatsResponse(total=total, today=today)


@router.get("/stats/summary", response_model=StatsResponse, summary="统计汇总")
def summary(session: Session = Depends(get_session)) -> StatsResponse:
    total, today = visit_summary(session)
    return StatsResponse(total=total, today=today)
