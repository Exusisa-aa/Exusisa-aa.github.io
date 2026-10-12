# -*- coding: utf-8 -*-
"""
FastAPI 应用入口。

启动：
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import sys

# ---------------------------------------------------------------------------
# 启动方式守卫
#
# 下面这些 import 用的是包内相对导入（from . import ...），只有把 app 当成
# 「包」加载时才成立。直接 `python app/main.py` / `python main.py` 会把模块
# 当独立脚本跑，相对导入失去参照，报的是 "attempted relative import with no
# known parent package" —— 这行错误信息很难让人联想到是启动方式的问题。
# 所以这里提前拦一下，直接给出能照做的命令。
# ---------------------------------------------------------------------------
if __package__ in (None, ""):
    sys.exit(
        "启动方式不对：不能直接运行 main.py。\n"
        "\n"
        "在 server/ 目录下执行：\n"
        "    python -m uvicorn app.main:app --reload --port 8000\n"
        "\n"
        "或者回到项目根目录执行：\n"
        "    npm run dev        前后端一起起\n"
        "    npm run dev:api    只起后端\n"
        "\n"
        "用 PyCharm 的话：Run → Edit Configurations，新建一个配置，\n"
        "把 \"Script path\" 换成 \"Module name\"，填 uvicorn；\n"
        "Parameters: app.main:app --reload --port 8000\n"
        "Working directory: <项目>/server"
    )

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from . import __version__
from .api import api_router
from .config import settings
from .content_loader import load_all
from .db import init_db
from .limiter import limiter

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("portfolio")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    bundle = load_all()
    log.info(
        "内容已加载：%d 个项目 · %d 组技能 · %d 条荣誉 · %d 屏分镜",
        len(bundle.projects),
        len(bundle.skills.groups),
        len(bundle.honors.honors),
        len(bundle.stage.sections),
    )
    log.info("简历 PDF: %s", bundle.profile.resume_pdf or "(未配置)")
    yield


app = FastAPI(
    title="陈明辉 · 个人作品集 API",
    description="内容接口 + 联系表单 + 访客统计。内容源是 content/ 下的 YAML。",
    version=__version__,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["meta"], summary="存活探测")
async def health() -> dict:
    """
    ★ 前端启动时探测这个接口，用来决定走 live 还是 static 模式。

    静态模式下 GitHub Pages 会对 /api/health 返回 404 + text/html，
    所以前端必须同时校验 status === 200 和 content-type 是 JSON，
    只看请求成功与否会误判成 live。
    """
    bundle = load_all()
    return {
        "status": "ok",
        "mode": "live",
        "version": bundle.version,
        "contentHash": bundle.content_hash,
    }


app.include_router(api_router, prefix="/api")


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)


if __name__ == "__main__":
    main()
