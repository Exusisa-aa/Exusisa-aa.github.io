/**
 * 内容类型定义 —— 与 server/app/models.py 一一对应。
 *
 * ⚠️ 改字段时两边必须同步。后端序列化用的是 by_alias=True，
 *    所以这里的键名是 camelCase（对应 Python 侧的 alias）。
 */

export type HonorType = 'award' | 'copyright' | 'cert'
export type HonorLevel = 'national' | 'provincial' | 'school' | 'vendor'
export type ProjectStatus = 'competition' | 'internship' | 'course' | 'personal' | 'production'
export type GalleryKind = 'screenshot' | 'architecture' | 'result' | 'diagram'
export type SectionType =
  | 'hero'
  | 'about'
  | 'skills'
  | 'project'
  | 'carousel'
  | 'honors'
  | 'selfeval'
  | 'contact'

export interface Theme {
  c1: string
  c2: string
  accent: string
}

export interface Metric {
  label: string
  value: string
}

export interface LinkItem {
  type: 'github' | 'demo' | 'doc' | 'blog' | 'other'
  label: string
  url: string
  /** 按钮旁边的小字说明，留空则不显示 */
  note: string
}

export interface GalleryItem {
  src: string
  alt: string
  caption: string
  kind: GalleryKind
}

export interface VideoItem {
  src: string
  poster: string
  caption: string
  kind: 'mp4' | 'hls' | 'youtube' | 'bilibili'
  externalUrl: string
}

export interface Stack {
  language: string[]
  framework: string[]
  middleware: string[]
  infra: string[]
}

// ---------------------------------------------------------------- profile

export interface ContactItem {
  type: 'phone' | 'email' | 'github' | 'blog' | 'wechat'
  label: string
  value: string
  href: string
  primary: boolean
  /** 网页版写信链接；留空则退回 href（mailto） */
  compose: string
}

export interface Education {
  school: string
  major: string
  degree: string
  grade: string
  start: string
  end: string
  logo: string
}

export interface Badge {
  value: string
  label: string
  /** 证书大图路径；有值就说明这个徽章可以点开 */
  cert: string | null
}

export interface Profile {
  name: string
  nameEn: string
  age: number | null
  headline: string
  heroTitle: string
  heroTitleAccent: string
  tagline: string
  location: string
  status: 'open' | 'busy' | 'closed'
  statusText: string
  contacts: ContactItem[]
  education: Education[]
  badges: Badge[]
  resumePdf: string
  updatedAt: string
}

// ---------------------------------------------------------------- skills

export interface SkillItem {
  name: string
  keywords: string[]
}

export interface SkillGroup {
  id: string
  title: string
  accent: string
  level: string
  items: SkillItem[]
}

export interface Skills {
  groups: SkillGroup[]
}

// ---------------------------------------------------------------- honors

export interface CertImage {
  src: string
  alt: string
}

export interface Honor {
  id: string
  title: string
  type: HonorType
  level: HonorLevel
  issuer: string
  date: string
  featured: boolean
  /** 证书上的佐证信息，键名自由 */
  meta: Record<string, string>
  cert: CertImage | null
}

export interface Honors {
  honors: Honor[]
}

// ---------------------------------------------------------------- courses

export interface Courses {
  courses: string[]
}

// ---------------------------------------------------------------- projects

export interface Project {
  id: string
  order: number
  title: string
  subtitle: string
  period: string
  role: string
  team: string
  status: ProjectStatus
  category: string[]
  tags: string[]
  summary: string
  description: string
  highlights: string[]
  metrics: Metric[]
  stack: Stack

  cover: string | null
  images: GalleryItem[]
  gallery: GalleryItem[]
  frames: string[]
  videos: VideoItem[]
  links: LinkItem[]
  /** 轮播框宽高比，null 用默认 1.93 */
  galleryAspect: number | null

  theme: Theme | null
  featured: boolean
}

// ---------------------------------------------------------------- site / stage

export interface StageSection {
  id: string
  nav: string
  type: SectionType
  projectId: string | null
  theme: Theme
}

export interface CarouselConfig {
  autoplayMs: number
  lockMs: number
  kenBurnsMs: number
  swipePx: number
  offsetPx: number
  scale: number
}

export interface VideoConfig {
  aspect: string
  seekOnHover: boolean
}

export interface Stage {
  sections: StageSection[]
  carousel: CarouselConfig
  video: VideoConfig
}

export interface SiteMeta {
  title: string
  description: string
  lang: string
  url: string
}

// ---------------------------------------------------------------- 聚合包

export interface Bundle {
  version: string
  generatedAt: string
  contentHash: string

  profile: Profile
  skills: Skills
  honors: Honors
  courses: Courses
  selfEvaluation: string
  site: SiteMeta
  stage: Stage
  projects: Project[]
}

// ---------------------------------------------------------------- 运行模式

/** live = 后端在跑；static = 读构建时导出的 JSON 快照（GitHub Pages） */
export type ApiMode = 'live' | 'static'
