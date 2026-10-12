/**
 * 访客统计 —— 同样按模式降级。
 *
 * 静态模式下**直接返回 null 并让 UI 隐藏计数组件**，
 * 而不是显示一个 0 —— 假的 0 比没有更难看。
 */

import axios from 'axios'

import type { ApiMode } from './types'

export interface StatsSummary {
  total: number
  today: number
}

const apiClient = axios.create({
  baseURL: `${import.meta.env.BASE_URL}api/v1`,
  timeout: 8000,
})

/** 记一次访问。只有 live 模式才有意义，static 静默跳过。 */
export async function recordVisit(mode: ApiMode): Promise<StatsSummary | null> {
  if (mode !== 'live') return null
  try {
    const { data } = await apiClient.post<StatsSummary>('/stats/visit', {
      path: location.pathname,
      referrer: document.referrer,
    })
    return data
  } catch {
    return null
  }
}

/** 取统计汇总。拿不到就返回 null，由 UI 决定隐藏。 */
export async function fetchStats(mode: ApiMode): Promise<StatsSummary | null> {
  if (mode !== 'live') return null
  try {
    const { data } = await apiClient.get<StatsSummary>('/stats/summary')
    return data
  } catch {
    return null
  }
}
