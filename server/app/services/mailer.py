# -*- coding: utf-8 -*-
"""
邮件通知 —— 可选功能。

默认不启用：只有 .env 里同时配了 SMTP_HOST 和 NOTIFY_EMAIL 才会发信。
没配的话表单照样入库，只是不给你发通知邮件。

用标准库 smtplib 而不是 aiosmtplib：这个函数是作为 BackgroundTask 在
线程池里跑的，同步写法更简单，也少一个依赖。
"""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from ..config import settings

log = logging.getLogger(__name__)


def send_notification(row) -> bool:
    """
    有新留言时发一封通知邮件。

    失败只记日志，不抛出 —— 留言已经入库了，发信失败不该让用户看到报错。
    """
    if not (settings.smtp_host and settings.notify_email):
        return False

    msg = EmailMessage()
    msg["Subject"] = f"[作品集留言] {row.subject or row.name}"
    msg["From"] = settings.smtp_user or settings.notify_email
    msg["To"] = settings.notify_email
    msg["Reply-To"] = row.email
    msg.set_content(
        f"姓名：{row.name}\n"
        f"邮箱：{row.email}\n"
        f"主题：{row.subject}\n"
        f"时间：{row.created_at.isoformat()}\n"
        f"IP：{row.ip}\n"
        f"{'-' * 40}\n"
        f"{row.message}\n"
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        return True
    except Exception as exc:  # noqa: BLE001 —— 发信失败原因很多，一律只记录
        log.warning("发送通知邮件失败: %s", exc)
        return False
