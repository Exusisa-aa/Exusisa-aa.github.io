# -*- coding: utf-8 -*-
"""简历 PDF 下载。

live 模式下由后端返回文件；static 模式下 GitHub Pages 直接托管同一个文件
（都在 web/public/files/ 下），所以两边下载到的内容是一样的。
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..config import settings
from ..content_loader import load_all

router = APIRouter(tags=["resume"])

# 下载时给用户看到的文件名（中文渲染更好的浏览器会显示这个）
DOWNLOAD_NAME = "陈明辉-Java全栈开发工程师与Agent智能体开发.pdf"


def resolve_resume_path() -> Path | None:
    """
    把 profile.yaml 里的 resumePdf（形如 /files/Xxx.pdf）解析成磁盘路径。

    只允许落在 web/public/files/ 目录内 —— 防止被构造成 ../ 穿越出去读别的文件。
    """
    rel = load_all().profile.resume_pdf
    if not rel:
        return None

    files_root = (settings.web_public_dir / "files").resolve()
    candidate = (settings.web_public_dir / rel.lstrip("/")).resolve()

    if not candidate.is_relative_to(files_root):
        return None
    return candidate if candidate.is_file() else None


@router.get("/resume.pdf", summary="预览简历 PDF")
async def preview_resume() -> FileResponse:
    """
    返回简历 PDF，供浏览器**直接预览**。

    注意不要用 FileResponse 的 filename 参数 —— 它会写出
    `Content-Disposition: attachment`，浏览器会直接下载而不是打开阅读器。
    这里手动写 inline，让 PDF 在新标签页里直接显示。

    中文文件名必须按 RFC 5987 编码（filename*=UTF-8''...）：
    HTTP 头只能是 latin-1，塞中文进去会直接报错。
    """
    path = resolve_resume_path()
    if path is None:
        raise HTTPException(
            status_code=404,
            detail="简历文件不存在。请把 PDF 放到 web/public/files/ 并确认 profile.yaml 的 resumePdf 指向它。",
        )
    return FileResponse(
        path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{quote(DOWNLOAD_NAME)}",
            "Cache-Control": "public, max-age=3600",
        },
    )
