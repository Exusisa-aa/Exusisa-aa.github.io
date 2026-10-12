/**
 * 运行模式探测 —— ★ 前后端解耦的关键。
 *
 * 启动时只探测一次 /api/health，决定走 live（后端在跑）还是 static（读 JSON 快照）。
 * 探测结果缓存到模块级变量和 sessionStorage，同一个会话里不会重复探测。
 *
 * ⚠️ 最容易踩的坑：
 *    GitHub Pages 上请求 /api/health 返回的是 **404 + text/html**，不是网络异常。
 *    如果只判断「请求有没有抛错」，就会把静态站误判成 live 模式，
 *    然后所有请求都静默失败，页面一片空白。
 *    所以必须同时校验 status === 200 且 content-type 是 JSON。
 */

import type { ApiMode } from './types'

const PROBE_TIMEOUT_MS = 1500
const STORAGE_KEY = 'portfolio:api-mode'

let cached: ApiMode | null = null

/** 允许用 ?api=live / ?api=static 强制指定模式，方便本地调试两条路径 */
function forcedMode(): ApiMode | null {
  if (typeof location === 'undefined') return null
  const value = new URLSearchParams(location.search).get('api')
  return value === 'live' || value === 'static' ? value : null
}

async function doProbe(): Promise<ApiMode> {
  const forced = forcedMode()
  if (forced) return forced

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), PROBE_TIMEOUT_MS)

  try {
    // 带上 BASE_URL —— 部署在子路径下时也要能找到正确的地址
    const url = `${import.meta.env.BASE_URL}api/health`
    const res = await fetch(url, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    })

    // ① 状态码必须是 200（GitHub Pages 会给 404）
    if (!res.ok) return 'static'

    // ② content-type 必须是 JSON（GitHub Pages 的 404 页是 text/html）
    const contentType = res.headers.get('content-type') ?? ''
    if (!contentType.includes('application/json')) return 'static'

    // ③ 再确认一下确实是我们的后端（防止有别的服务占用这个路径）
    const data = (await res.json()) as { mode?: string }
    return data?.mode === 'live' ? 'live' : 'static'
  } catch {
    // 网络错误 / 超时 / 后端没起 —— 一律降级
    return 'static'
  } finally {
    clearTimeout(timer)
  }
}

export async function probeApiMode(): Promise<ApiMode> {
  if (cached) return cached

  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (stored === 'live' || stored === 'static') {
      cached = stored
      return stored
    }
  } catch {
    /* 隐私模式下 sessionStorage 可能不可用，忽略 */
  }

  const mode = await doProbe()
  cached = mode

  try {
    sessionStorage.setItem(STORAGE_KEY, mode)
  } catch {
    /* 忽略 */
  }

  return mode
}

/** 测试用：清掉缓存 */
export function resetApiModeCache(): void {
  cached = null
  try {
    sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    /* 忽略 */
  }
}
