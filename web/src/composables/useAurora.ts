/**
 * 极光光晕的鼠标视差。
 *
 * 关键点：不是让光球硬跟着鼠标走，而是用一个 rAF 循环做线性插值（lerp），
 * 让它们缓慢地"追"过去。系数 0.04 越小越黏。每个球再用不同的偏移倍数
 * (i+1)*12 错开，就产生了纵深感。
 *
 * 三个球叠上 blur(120px) 之后，任何突兀的移动都会被糊掉 —— 所以这里
 * 追求的不是精确跟随，而是"有东西在缓慢呼吸"的感觉。
 */

import { onBeforeUnmount, onMounted, type Ref } from 'vue'

const LERP = 0.04
const OFFSET_STEP = 12

export function useAurora(blobs: Ref<HTMLElement[]>) {
  let targetX = 0
  let targetY = 0
  let currentX = 0
  let currentY = 0
  let rafId = 0
  let running = false

  const reducedMotion =
    typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches

  function onPointerMove(e: PointerEvent): void {
    // 归一化到 -0.5 ~ 0.5
    targetX = e.clientX / innerWidth - 0.5
    targetY = e.clientY / innerHeight - 0.5
  }

  function tick(): void {
    currentX += (targetX - currentX) * LERP
    currentY += (targetY - currentY) * LERP

    blobs.value.forEach((blob, i) => {
      const factor = (i + 1) * OFFSET_STEP
      blob.style.translate = `${currentX * factor}px ${currentY * factor}px`
    })

    rafId = requestAnimationFrame(tick)
  }

  function start(): void {
    if (running || reducedMotion) return
    running = true
    rafId = requestAnimationFrame(tick)
  }

  function stop(): void {
    running = false
    if (rafId) cancelAnimationFrame(rafId)
    rafId = 0
  }

  /** 标签页切到后台就停 —— 省电，也避免回来后一帧跳很远 */
  function onVisibilityChange(): void {
    if (document.hidden) stop()
    else start()
  }

  onMounted(() => {
    if (reducedMotion) return
    addEventListener('pointermove', onPointerMove, { passive: true })
    document.addEventListener('visibilitychange', onVisibilityChange)
    start()
  })

  onBeforeUnmount(() => {
    removeEventListener('pointermove', onPointerMove)
    document.removeEventListener('visibilitychange', onVisibilityChange)
    stop()
  })

  return { start, stop, reducedMotion }
}
