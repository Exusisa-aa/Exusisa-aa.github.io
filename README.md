# 陈明辉 · 个人作品集

个人简介 + 作品展示单页站。**Vue 3 + FastAPI**，可部署到 GitHub Pages。

视觉风格参考 [songtaoluo007-maker.github.io](https://songtaoluo007-maker.github.io/)：暗底极光光晕 + 衬线标题 + 等宽标签 + 玻璃拟态卡片 + 全屏分镜滚动。

---

## 快速开始

```bash
# 一次性安装（前后端依赖一起装）
npm run install:all

# 开发：同时起 FastAPI(8000) 和 Vite(5173)
npm run dev
```

打开 http://localhost:5173 。控制台会打印 `apiMode = live`。

只想跑前端（**这是线上真实路径，建议经常这么测**）：

```bash
npm run dev:web
```

---

## 启动后端

**必须把 `app` 当成包来加载**，因为后端代码内部用的是相对导入（`from .config import ...`）。直接跑 `main.py` 会报 `attempted relative import with no known parent package`。

在 `server/` 目录下，二选一：

```bash
python -m uvicorn app.main:app --reload --port 8000
python -m app.main                    # 等价，reload 已内置
```

在项目根目录：

```bash
npm run dev:api
```

### 用 PyCharm 调试

默认的 "Current File" 运行方式会踩上面那个坑。新建一个运行配置：

| 项 | 值 |
|---|---|
| 执行方式 | 选 **Module name**（不是 Script path） |
| Module name | `uvicorn` |
| Parameters | `app.main:app --reload --port 8000` |
| Working directory | `<项目根>/server` |

---

## 目录结构

```
portfolio/
├─ content/          ★ 只改这里就能更新网站内容（YAML + Markdown）
├─ server/           FastAPI：内容接口 + 联系表单 + 访客统计
├─ web/              Vue 3 + Vite 前端
│  ├─ public/data/   构建产物：静态 JSON 快照（★ 要提交进 git）
│  ├─ public/media/  项目图片与视频
│  └─ src/
└─ scripts/          素材处理 / 截图工具
```

---

## 内容怎么改

全部内容都在 `content/` 下，改完**刷新页面即生效，不用重启服务**（开发模式下）。上线时要重新导出快照，见下文。

| 文件 | 改什么 |
|---|---|
| `profile.yaml` | 姓名、联系方式、教育背景、首屏大标题、简历 PDF 路径 |
| `skills.yaml` | 技能分组（每组渲染成一张卡片） |
| `honors.yaml` | 荣誉资质；填了 `cert.src` 的条目点击可看证书大图 |
| `courses.yaml` | 主修课程标签 |
| `self-evaluation.md` | 自我评价，支持 Markdown |
| `site.yaml` | **页面结构**：分镜顺序、每屏主题色、轮播参数 |
| `projects/*.yaml` | 每个项目一个文件 |

### 调整页面顺序 / 换配色

改 `content/site.yaml` 的 `stage.sections` 就行，不用动代码：

```yaml
- id: skills
  nav: 能力                          # 顶栏和圆点导航显示的名字
  type: skills                       # hero|about|skills|project|carousel|honors|selfeval|contact
  theme: { c1: "#9d7cff", c2: "#7c8cff", accent: "#a58cff" }   # 这一屏的极光配色
```

`type: project` 的分镜要额外给 `projectId`，指向 `content/projects/` 里某个项目的 `id`。

---

## 两种运行模式

这套站要在 GitHub Pages 上跑，而 Pages 是纯静态托管、跑不了 FastAPI。所以：

```
content/*.yaml  ← 唯一数据源
      ├─→ FastAPI 读取，暴露 /api/v1/*          （live 模式）
      └─→ export.py 导出静态 JSON → web/public/data/   （static 模式）
```

前端启动时探测一次 `/api/health` 决定走哪条。**两条路径拿到的是同一份数据结构**（静态快照就是 `bundle` 接口的冻结副本），所以视觉和交互完全一致。

手动切换模式调试：

| 参数 | 作用 |
|---|---|
| `?api=static` | 强制走静态快照 |
| `?api=live` | 强制走后端 |
| `?noanim` | 关掉入场动效和滚动吸附（截图/打印/无障碍测试用） |
| `?scene=3` | 直接跳到第 3 屏 |
| `#p-mycat-cluster` | 用锚点跳到某屏 |

### 上线前必须导出快照

```bash
npm run export     # content/*.yaml → web/public/data/*.json
```

改了 YAML 却忘了导出，线上就还是旧内容 —— **这是最容易踩的坑**。

---

## 部署到 GitHub Pages

把这个目录作为仓库根目录推到 GitHub，仓库 **Settings → Pages → Source 选 GitHub Actions**，之后每次推送到 `main`，`.github/workflows/deploy-pages.yml` 会自动：导出内容快照 → 构建前端 → 发布。

### 两种仓库名，对应两种地址

| 仓库名 | 站点地址 | base |
|---|---|---|
| `<用户名>.github.io` | `https://<用户名>.github.io/` | `/` |
| 其它任意名字（如 `portfolio`） | `https://<用户名>.github.io/<仓库名>/` | `/<仓库名>/` |

`vite.config.ts` 靠「仓库名是否以 `.github.io` 结尾」自动判别，**不需要手改**。判据来自 workflow 传的 `${{ github.event.repository.name }}`。

> 搞错这一项的表现是：页面能打开，但 CSS/JS 全 404、样式全丢。所以本地验证时两种都要试一遍：
> ```bash
> cd web
> PAGES_REPO="你的用户名.github.io" npx vite build   # 用户站 → 产物路径应是 /assets/...
> PAGES_REPO="portfolio" npx vite build              # 项目站 → 产物路径应是 /portfolio/assets/...
> ```
>
> 为什么 workflow 只传仓库名而不是完整的 `/<仓库名>/`：git-bash / MSYS 会把以 `/` 开头的环境变量当路径改写，`/portfolio/` 传进去会变成 `/study/git/Git/portfolio/`，构建出来的资源路径全错。

### 本地模拟线上环境

```bash
npm run build:pages
cd web && npx cross-env PAGES_REPO=portfolio npx vite preview --port 4173
# 打开 http://127.0.0.1:4173/portfolio/
```

---

## 联系表单

按运行模式自动降级，页面上的邮箱和电话**始终显示**（那才是最可靠的兜底）：

| 情况 | 通道 |
|---|---|
| live 模式 | POST 到 FastAPI，留言存进 SQLite |
| 配了 `VITE_WEB3FORMS_KEY` | 通过 Web3Forms 转发到你邮箱 |
| 都没有 | 打开邮件客户端 |

静态部署建议配 Web3Forms（免费、不用注册）：

```bash
cd web && cp .env.example .env.production
# 去 https://web3forms.com 填个邮箱拿到 key，填进 VITE_WEB3FORMS_KEY
```

后端还配了蜜罐字段和限流（默认 5 次/分钟/IP），垃圾提交会被静默丢弃。

---

## 素材

```bash
npm run assets     # 把原始素材转成 WebP 放进 web/public/media/
```

脚本在 `scripts/prepare-assets.py`，改里面的 `IMAGES` 映射表即可增删。幂等的，可以随时重跑。

---

## 待补充清单

- [ ] 4 个项目的 `description` / `highlights` / `metrics`（YAML 里都标了 `【待填】`），不要编造指标数字
- [ ] 微服务商城 / Mycat 集群的 `period`、`role`（也是 `【待填】`）
- [ ] 鸿蒙应用高级开发者认证的发证日期，以及证书图（`honors.yaml`，放 `web/public/certs/harmonyos-senior.png`）
- [ ] 确认毕业届别（`profile.yaml` 里有 TODO）
- [ ] Web3Forms key（仅当把联系表单加回来时才需要）

## 已归档的素材

`简历/未使用素材/` 下放着 25 个文件（10.4 MB），是「水下养殖鱼检测平台」的录像、算法架构图、检测结果和逐帧切图。

**为什么移出去**：该项目是 `featured: false`，走「更多作品」轮播，而轮播只渲染 `cover` —— 这些图一张都不会显示，却要跟着仓库被下载。

**怎么拿回来**：把文件移回 `web/public/media/` 对应目录，解开 `scripts/prepare-assets.py` 里注释掉的映射，在 `01-underwater-yolo.yaml` 补回 `videos` / `gallery` / `frames` 三段，再把 `featured` 改成 `true` 并到 `site.yaml` 加一屏。

## 已知问题

- **滚动吸附用的是 `proximity` 不是 `mandatory`**。技能屏和联系屏内容高于一屏，用 `mandatory` 会导致超出部分永远滚不到（内容不可达）。改回 `mandatory` 前请先确认所有分镜都能塞进一屏。

---

## 常用命令

| 命令 | 作用 |
|---|---|
| `npm run dev` | 前后端一起起 |
| `npm run dev:web` | 只起前端（测静态降级路径） |
| `npm run export` | 导出内容快照 |
| `npm run build` | 导出 + 构建 |
| `npm run build:pages` | 按 Pages 子路径构建 |
| `npm run assets` | 处理图片素材 |
| `python scripts/shoot.py` | 逐屏截图（需要 dev server 在跑） |
| `python scripts/shoot.py --width 420` | 用手机尺寸截图 |
