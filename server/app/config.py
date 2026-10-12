# -*- coding: utf-8 -*-
"""运行时配置。所有值都可以用环境变量覆盖（前缀 APP_）。"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVER_DIR = Path(__file__).resolve().parent.parent      # portfolio/server/
PROJECT_ROOT = SERVER_DIR.parent                          # portfolio/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=SERVER_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- 内容 ----
    content_dir: Path = PROJECT_ROOT / "content"
    # 前端静态资源目录。简历 PDF 就放在这里的 files/ 下，
    # live 模式下由后端读取并返回，static 模式下由 Pages 直接托管 —— 同一个文件。
    web_public_dir: Path = PROJECT_ROOT / "web" / "public"

    # ---- 服务 ----
    host: str = "127.0.0.1"
    port: int = 8000
    # 允许跨域的来源（开发期 Vite dev server / preview）
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    # ---- 数据库 ----
    database_url: str = f"sqlite:///{SERVER_DIR / 'portfolio.db'}"

    # ---- 联系表单 ----
    # 每个 IP 每分钟最多提交几次
    contact_rate_limit: str = "5/minute"
    # 邮件通知（留空则不发邮件，只入库）
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notify_email: str = ""

    # ---- 静态导出 ----
    version: str = "1.0.0"


settings = Settings()
