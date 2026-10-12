# -*- coding: utf-8 -*-
"""
Pydantic 模型 —— 前后端唯一的数据契约。

前端 web/src/api/types.ts 与这里的定义一一对应，改字段时两边要同步。

设计约定：
  * 所有可选字段给默认值，YAML 里没写也不会炸。
  * 允许额外字段（extra="allow"），方便临时往 YAML 里塞实验性数据而不报错。
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


# ---------------------------------------------------------------- 主题 / 通用


class Theme(_Base):
    """一屏的极光配色。c1/c2 是两个光球的颜色，accent 是强调色。"""

    c1: str = "#7c8cff"
    c2: str = "#4fe0c8"
    accent: str = "#8b9dff"


class Metric(_Base):
    label: str
    value: str


class LinkItem(_Base):
    type: Literal["github", "demo", "doc", "blog", "other"] = "other"
    label: str
    url: str = ""
    # 按钮旁边的一句小字说明，比如「仅前后端代码，镜像由作者保管」。
    # 留空则不显示。
    note: str = ""


class GalleryItem(_Base):
    src: str
    alt: str = ""
    caption: str = ""
    kind: Literal["screenshot", "architecture", "result", "diagram"] = "screenshot"


class VideoItem(_Base):
    src: str = ""
    poster: str = ""
    caption: str = ""
    kind: Literal["mp4", "hls", "youtube", "bilibili"] = "mp4"
    external_url: str = Field(default="", alias="externalUrl")


class Stack(_Base):
    language: list[str] = []
    framework: list[str] = []
    middleware: list[str] = []
    infra: list[str] = []


# ---------------------------------------------------------------- profile


class Contact(_Base):
    type: Literal["phone", "email", "github", "blog", "wechat"] = "email"
    label: str
    value: str
    href: str = ""
    primary: bool = False
    # 网页版写信链接（点一下跳到对应邮箱的写信窗口，收件人已填好）。
    # 留空则前端退回到 href（mailto）。
    compose: str = ""


class Education(_Base):
    school: str
    major: str = ""
    degree: str = ""
    grade: str = ""
    start: str = ""
    end: str = ""
    logo: str = ""


class Badge(_Base):
    value: str
    label: str
    # 证书大图路径（放 web/public/certs/）。填了徽章就能点开看大图。
    cert: str | None = None


class Profile(_Base):
    name: str
    name_en: str = Field(default="", alias="nameEn")
    age: int | None = None
    headline: str = ""
    hero_title: str = Field(default="", alias="heroTitle")
    hero_title_accent: str = Field(default="", alias="heroTitleAccent")
    tagline: str = ""
    location: str = ""
    status: Literal["open", "busy", "closed"] = "open"
    status_text: str = Field(default="", alias="statusText")
    contacts: list[Contact] = []
    education: list[Education] = []
    badges: list[Badge] = []
    resume_pdf: str = Field(default="", alias="resumePdf")
    updated_at: str = Field(default="", alias="updatedAt")


# ---------------------------------------------------------------- skills


class SkillItem(_Base):
    name: str
    keywords: list[str] = []


class SkillGroup(_Base):
    id: str
    title: str
    accent: str = ""
    level: str = ""
    items: list[SkillItem] = []


class Skills(_Base):
    groups: list[SkillGroup] = []


# ---------------------------------------------------------------- honors


class CertImage(_Base):
    src: str
    alt: str = ""


class Honor(_Base):
    id: str
    title: str
    type: Literal["award", "copyright", "cert"] = "award"
    # vendor = 厂商认证（华为、阿里这类企业发的），跟政府级别的 national 区分开
    level: Literal["national", "provincial", "school", "vendor"] = "school"
    issuer: str = ""
    date: str = ""
    featured: bool = False
    # 证书上抄下来的佐证信息（编号、团队、指导教师…），原样展示在列表里。
    # 键名随意，前端按固定顺序挑常用的显示。
    meta: dict[str, str] = {}
    cert: CertImage | None = None


class Honors(_Base):
    honors: list[Honor] = []


# ---------------------------------------------------------------- courses


class Courses(_Base):
    courses: list[str] = []


# ---------------------------------------------------------------- projects


class Project(_Base):
    id: str
    order: int = 0
    title: str
    subtitle: str = ""
    period: str = ""
    role: str = ""
    team: str = ""
    status: Literal["competition", "internship", "course", "personal", "production"] = "personal"
    category: list[str] = []
    tags: list[str] = []
    summary: str = ""
    description: str = ""
    highlights: list[str] = []
    metrics: list[Metric] = []
    stack: Stack = Stack()

    cover: str | None = None
    images: list[GalleryItem] = []
    gallery: list[GalleryItem] = []
    frames: list[str] = []
    videos: list[VideoItem] = []
    links: list[LinkItem] = []

    # 轮播框的宽高比。不填用默认的 1.93（桌面向截图）。
    # 手绘/竖版素材填个更方的比例（如 1.5），能少留很多黑边。
    gallery_aspect: float | None = Field(default=None, alias="galleryAspect")

    theme: Theme | None = None
    featured: bool = False


# ---------------------------------------------------------------- site / stage


class StageSection(_Base):
    id: str
    nav: str = ""
    type: Literal["hero", "about", "skills", "project", "carousel", "honors", "selfeval", "contact"]
    project_id: str | None = Field(default=None, alias="projectId")
    theme: Theme = Theme()


class CarouselConfig(_Base):
    autoplay_ms: int = Field(default=5600, alias="autoplayMs")
    lock_ms: int = Field(default=670, alias="lockMs")
    ken_burns_ms: int = Field(default=7000, alias="kenBurnsMs")
    swipe_px: int = Field(default=48, alias="swipePx")
    offset_px: int = Field(default=64, alias="offsetPx")
    scale: float = 0.985


class VideoConfig(_Base):
    aspect: str = "16 / 10"
    seek_on_hover: bool = Field(default=True, alias="seekOnHover")


class Stage(_Base):
    sections: list[StageSection] = []
    carousel: CarouselConfig = CarouselConfig()
    video: VideoConfig = VideoConfig()


class SiteMeta(_Base):
    title: str = ""
    description: str = ""
    lang: str = "zh-CN"
    url: str = ""


class Site(_Base):
    """site.yaml 的根结构"""

    site: SiteMeta = SiteMeta()
    stage: Stage = Stage()


# ---------------------------------------------------------------- 聚合包


class Bundle(_Base):
    """
    前端一次拉全的聚合包。

    ★ 静态快照（web/public/data/index.json）就是这份结构的一份冻结副本，
      所以 live 和 static 两条路径前端拿到的东西完全一致。
    """

    version: str = "1.0.0"
    generated_at: str = Field(default="", alias="generatedAt")
    content_hash: str = Field(default="", alias="contentHash")

    profile: Profile
    skills: Skills
    honors: Honors
    courses: Courses
    self_evaluation: str = Field(default="", alias="selfEvaluation")
    site: SiteMeta
    stage: Stage
    projects: list[Project] = []


# ---------------------------------------------------------------- 表单 / 统计


class ContactRequest(_Base):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=160)
    subject: str = Field(default="", max_length=200)
    message: str = Field(min_length=1, max_length=5000)
    # 蜜罐字段：正常用户看不见也不会填，填了说明是机器人
    honeypot: str = ""


class ContactResponse(_Base):
    id: int
    status: str
    created_at: str = Field(alias="createdAt")


class VisitRequest(_Base):
    path: str = "/"
    referrer: str = ""


class StatsResponse(_Base):
    total: int
    today: int


def dump(model: BaseModel) -> dict[str, Any]:
    """统一序列化出口，保证 API 与导出脚本用的是一套规则。"""
    return model.model_dump(mode="json", by_alias=True)
