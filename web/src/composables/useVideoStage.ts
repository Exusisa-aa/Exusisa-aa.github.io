/**
 * 演示视频框的播放状态机。
 *
 * 参考站的取舍值得照搬：**播放/暂停按钮默认完全隐藏**。
 * 视频是自动静音循环播放的，按钮只在用户主动暂停时才浮出来 ——
 * 不打扰，但用户想停下来看的时候又找得到。
 *
 * 状态：
 *   hidden    默认。按钮不可见
 *   paused    用户暂停了。按钮持续显示
 *   playing   用户点了播放。按钮显示 600ms 后自动隐去
 */

import { onBeforeUnmount, ref, type Ref } from 'vue'

export type PlaybackFeedback = 'hidden' | 'paused' | 'playing'

const FEEDBACK_MS = 600

export function useVideoStage(video: Ref<HTMLVideoElement | null>) {
  const feedback = ref<PlaybackFeedback>('hidden')

  let hideTimer: ReturnType<typeof setTimeout> | null = null

  function clearHideTimer(): void {
    if (hideTimer) {
      clearTimeout(hideTimer)
      hideTimer = null
    }
  }

  function play(showFeedback = false): void {
    const el = video.value
    if (!el) return
    clearHideTimer()

    const result = el.play()
    feedback.value = showFeedback ? 'playing' : 'hidden'

    if (showFeedback) {
      hideTimer = setTimeout(() => {
        hideTimer = null
        feedback.value = 'hidden'
      }, FEEDBACK_MS)
    }

    // 浏览器可能因为自动播放策略拒绝播放 —— 那就退回"已暂停"，
    // 让按钮留在画面上，用户自己点一下就能播
    if (result && typeof result.catch === 'function') {
      result.catch(() => {
        clearHideTimer()
        feedback.value = 'paused'
      })
    }
  }

  function pause(showFeedback = false): void {
    const el = video.value
    if (!el) return
    clearHideTimer()
    el.pause()
    feedback.value = showFeedback ? 'paused' : 'hidden'
  }

  function toggleFromUser(): void {
    const el = video.value
    if (!el) return
    if (el.paused) play(true)
    else pause(true)
  }

  /** 拖动进度条到某个比例位置 */
  function seekToRatio(ratio: number): void {
    const el = video.value
    if (!el || !Number.isFinite(el.duration)) return
    el.currentTime = Math.max(0, Math.min(1, ratio)) * el.duration
  }

  onBeforeUnmount(clearHideTimer)

  return { feedback, play, pause, toggleFromUser, seekToRatio }
}

/** 秒数格式化成 0:00 */
export function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}
