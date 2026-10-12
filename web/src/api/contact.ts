/**
 * 联系表单 —— 三态传输适配器。
 *
 * GitHub Pages 是纯静态托管，没有后端接表单。所以按优先级尝试：
 *
 *   1. live 模式          → POST 到自己的 FastAPI，留言入库
 *   2. 配了 Web3Forms key → POST 到 Web3Forms（免费第三方，一个 key 即可，适配静态站）
 *   3. 都没有             → 退化成打开邮件客户端
 *
 * 无论走哪条路，页面上都始终展示邮箱和电话 —— 那才是最可靠的兜底。
 */

import axios from 'axios'

import type { ApiMode } from './types'

export interface ContactPayload {
  name: string
  email: string
  subject: string
  message: string
  /** 蜜罐：正常用户看不见，填了就说明是机器人 */
  honeypot?: string
}

export type ContactChannel = 'api' | 'web3forms' | 'mailto' | 'none'

export interface ContactResult {
  ok: boolean
  channel: ContactChannel
  message: string
}

const WEB3FORMS_ENDPOINT = 'https://api.web3forms.com/submit'

const apiClient = axios.create({
  baseURL: `${import.meta.env.BASE_URL}api/v1`,
  timeout: 15000,
})

/** 当前实际能用的通道（用于在 UI 上给出准确提示） */
export function resolveChannel(mode: ApiMode): ContactChannel {
  if (mode === 'live') return 'api'
  if (import.meta.env.VITE_WEB3FORMS_KEY) return 'web3forms'
  if (import.meta.env.VITE_CONTACT_EMAIL) return 'mailto'
  return 'none'
}

export async function submitContact(
  payload: ContactPayload,
  mode: ApiMode,
): Promise<ContactResult> {
  const channel = resolveChannel(mode)

  if (channel === 'api') {
    try {
      await apiClient.post('/contact', payload)
      return { ok: true, channel, message: '留言已收到，我会尽快回复你。' }
    } catch (err) {
      console.warn('[portfolio] 提交到后端失败', err)
      return { ok: false, channel, message: '提交失败，请直接发邮件给我。' }
    }
  }

  if (channel === 'web3forms') {
    try {
      const res = await fetch(WEB3FORMS_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          // 先铺开 payload，再覆盖 —— 反过来的话 subject 会被 payload 里的空值盖掉
          ...payload,
          access_key: import.meta.env.VITE_WEB3FORMS_KEY,
          from_name: payload.name,
          subject: payload.subject || `作品集留言 · ${payload.name}`,
        }),
      })
      const data = (await res.json()) as { success?: boolean }
      if (data?.success) {
        return { ok: true, channel, message: '留言已发送，我会尽快回复你。' }
      }
      return { ok: false, channel, message: '发送失败，请直接发邮件给我。' }
    } catch (err) {
      console.warn('[portfolio] Web3Forms 提交失败', err)
      return { ok: false, channel, message: '发送失败，请直接发邮件给我。' }
    }
  }

  // 兜底：打开邮件客户端
  openMailto(payload)
  return { ok: true, channel: 'mailto', message: '已为你打开邮件客户端。' }
}

/** 直接调起邮件客户端，内容预填好 */
export function openMailto(payload: Partial<ContactPayload>): void {
  const to = import.meta.env.VITE_CONTACT_EMAIL || ''
  const subject = payload.subject || '来自作品集的联系'
  const body = [
    payload.name ? `姓名：${payload.name}` : '',
    payload.email ? `邮箱：${payload.email}` : '',
    '',
    payload.message ?? '',
  ]
    .filter(Boolean)
    .join('\n')

  window.location.href = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
}
