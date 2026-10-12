# -*- coding: utf-8 -*-
"""联系表单 —— 入库 + 蜜罐反垃圾 + 限流 + 可选邮件通知。"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from ..config import settings
from ..db import ContactMessage, get_session
from ..limiter import limiter
from ..models import ContactRequest, ContactResponse
from ..services.mailer import send_notification

router = APIRouter(tags=["contact"])

# 只做最基本的格式校验。邮箱真假不在这里判断 —— 前端也有一份同样的校验。
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# 关键词黑名单：命中就静默丢弃（返回成功但不入库），不给垃圾提交者反馈
_SPAM_HINTS = ("http://", "https://", "www.", "<a ", "viagra", "casino", "贷款", "博彩")


@router.post("/contact", response_model=ContactResponse, status_code=201, summary="提交联系表单")
@limiter.limit(settings.contact_rate_limit)
def submit_contact(
    request: Request,
    payload: ContactRequest,
    background: BackgroundTasks,
    session: Session = Depends(get_session),
) -> ContactResponse:
    now = datetime.now(timezone.utc)

    # 蜜罐命中 —— 正常用户看不到这个字段，填了就一定是机器人。
    # 返回 201 假成功，让机器人以为提交成功了，不触发重试。
    if payload.honeypot:
        return ContactResponse(id=0, status="received", createdAt=now.isoformat())

    if not _EMAIL_RE.match(payload.email):
        # 邮箱格式不对，同样走"假成功"，避免给爬虫探测接口行为的机会
        return ContactResponse(id=0, status="received", createdAt=now.isoformat())

    lowered = f"{payload.subject}\n{payload.message}".lower()
    if any(hint in lowered for hint in _SPAM_HINTS):
        return ContactResponse(id=0, status="received", createdAt=now.isoformat())

    row = ContactMessage(
        name=payload.name.strip(),
        email=payload.email.strip(),
        subject=payload.subject.strip(),
        message=payload.message.strip(),
        ip=(request.client.host if request.client else "")[:64],
        user_agent=request.headers.get("user-agent", "")[:300],
        created_at=now,
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    if settings.notify_email and settings.smtp_host:
        background.add_task(send_notification, row)

    return ContactResponse(id=row.id, status="received", createdAt=now.isoformat())
