# -*- coding: utf-8 -*-
"""
SQLite 持久化 —— 只存两类东西：联系表单留言 和 访客记录。

刻意不用 Alembic：这张表结构简单，启动时 create_all 足够。
真要改结构了，删掉 portfolio.db 重建即可（本地开发场景）。

注意：所有 session 都是同步的，因此用到 DB 的接口必须写成 `def`（不是 `async def`），
      FastAPI 会把它们丢进线程池执行，不会阻塞事件循环。
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


class ContactMessage(Base):
    __tablename__ = "contact_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(160))
    subject: Mapped[str] = mapped_column(String(200), default="")
    message: Mapped[str] = mapped_column(Text)
    ip: Mapped[str] = mapped_column(String(64), default="")
    user_agent: Mapped[str] = mapped_column(String(300), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class VisitLog(Base):
    __tablename__ = "visit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String(300), default="/")
    referrer: Mapped[str] = mapped_column(String(300), default="")
    ip: Mapped[str] = mapped_column(String(64), default="")
    visited_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


engine = create_engine(
    settings.database_url,
    # SQLite 默认禁止跨线程复用连接，而 FastAPI 的线程池会跨线程用，所以必须关掉这个检查
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI 依赖注入用的 session 生成器。"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------- 查询辅助


def add_visit(session: Session, path: str, referrer: str, ip: str) -> tuple[int, int]:
    """记一次访问，返回 (总数, 今日数)。"""
    session.add(VisitLog(path=path[:300], referrer=referrer[:300], ip=ip[:64]))
    session.commit()
    return visit_summary(session)


def visit_summary(session: Session) -> tuple[int, int]:
    total = session.scalar(select(func.count()).select_from(VisitLog)) or 0
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today = (
        session.scalar(
            select(func.count()).select_from(VisitLog).where(VisitLog.visited_at >= today_start)
        )
        or 0
    )
    return int(total), int(today)
