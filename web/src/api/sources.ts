/**
 * 内容来源 —— live 与 static 两条路径的唯一收口点。
 *
 * 两个实现都返回同样的 Bundle，所以上层组件完全不需要知道自己跑在哪种模式下。
 */

import axios from 'axios'

import type { ApiMode, Bundle } from './types'

export interface ContentSource {
  readonly mode: ApiMode
  getBundle(): Promise<Bundle>
}

// ---------------------------------------------------------------- live

const apiClient = axios.create({
  baseURL: `${import.meta.env.BASE_URL}api/v1`,
  timeout: 10000,
})

export class LiveSource implements ContentSource {
  readonly mode = 'live' as const

  async getBundle(): Promise<Bundle> {
    const { data } = await apiClient.get<Bundle>('/bundle')
    return data
  }
}

// ---------------------------------------------------------------- static

export class StaticSource implements ContentSource {
  readonly mode = 'static' as const

  async getBundle(): Promise<Bundle> {
    // 快照就是 /api/v1/bundle 的冻结副本，结构完全一致
    const url = `${import.meta.env.BASE_URL}data/index.json`
    const res = await fetch(url, { cache: 'no-cache' })
    if (!res.ok) {
      throw new Error(`静态快照缺失（HTTP ${res.status}）。请先跑 npm run export。`)
    }
    return (await res.json()) as Bundle
  }
}

export function createSource(mode: ApiMode): ContentSource {
  return mode === 'live' ? new LiveSource() : new StaticSource()
}

/**
 * 拿内容 —— 带一层兜底。
 *
 * 正常情况下按探测出的模式走；万一 live 请求失败（后端中途挂了、
 * 接口报错），再退一次到静态快照，而不是直接把页面搞白。
 */
export async function fetchBundle(mode: ApiMode): Promise<{ bundle: Bundle; mode: ApiMode }> {
  const primary = createSource(mode)

  try {
    return { bundle: await primary.getBundle(), mode }
  } catch (err) {
    if (mode === 'static') throw err // 静态都失败了，没得退

    console.warn('[portfolio] live 模式拉取失败，降级到静态快照', err)
    const fallback = new StaticSource()
    return { bundle: await fallback.getBundle(), mode: 'static' }
  }
}
