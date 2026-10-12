import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// GitHub Pages 有两种部署形态，base 不一样：
//
//   用户站  仓库名 <user>.github.io  →  访问 https://<user>.github.io/     → base 是 '/'
//   项目站  仓库名任意               →  访问 https://<user>.github.io/<repo>/ → base 是 '/<repo>/'
//
// 判别方法就是看仓库名是不是以 .github.io 结尾 —— 这是 GitHub 的约定。
// 搞错的话资源路径会全错（用户站会去请求 /<user>.github.io/assets/...，404）。
//
// 为什么用 PAGES_REPO（只传仓库名）而不是传完整的 '/<repo>/'：
//   git-bash / MSYS 会把以 '/' 开头的环境变量当成路径改写掉 ——
//   `GITHUB_PAGES_BASE=/portfolio/` 传进去会变成 `/study/git/Git/portfolio/`，
//   构建出来的资源路径就全错了。只传仓库名（没有前导斜杠）不会被改写。
//
// GitHub Action 里传的是 ${{ github.event.repository.name }}，仓库改名会自动跟上。
const USER_SITE_SUFFIX = '.github.io'

function resolveBase(): string {
  const repo = process.env.PAGES_REPO?.replace(/^\/+|\/+$/g, '')
  if (!repo) return '/'
  // 用户站跑在根路径上
  if (repo.toLowerCase().endsWith(USER_SITE_SUFFIX)) return '/'
  return `/${repo}/`
}

export default defineConfig({
  base: resolveBase(),

  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  server: {
    port: 5173,
    // 开发时把 /api 代理到 FastAPI，这样前端只需要写 /api/xxx，
    // 不用配 CORS，也不用区分环境。
    // 关掉后端时这个代理会失败 —— 那正是我们要测的 static 降级路径。
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    outDir: 'dist',
    // 视频和图片都放在 public/ 里原样拷贝，不做打包处理
    assetsInlineLimit: 4096,
    chunkSizeWarningLimit: 900,
  },
})
