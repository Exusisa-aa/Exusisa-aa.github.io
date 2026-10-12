/**
 * 固定舞台轮播 —— 参考站那套的核心逻辑。
 *
 * 与常见轮播（轨道位移）不同，这里是所有幻灯片**绝对定位叠放**，
 * 靠三个状态类控制显隐和位移：
 *
 *   is-active  当前这张：opacity 1、无位移、可交互
 *   is-before  排在当前之前的：向左偏移
 *   is-after   排在当前之后的：向右偏移
 *
 * 离场的那一张也走同样的位移（方向由 direction 决定），所以切换方向感一致。
 *
 * 几个容易漏掉但很影响体感的点：
 *   · locked —— 切换后 670ms 内不再响应，防止连点把动画打断成一团
 *   · document.hidden 时暂停自动播放，切回来自动恢复
 *   · prefers-reduced-motion 直接关掉自动播放
 *   · 指针滑动超过 swipePx 才翻页，避免误触
 */

import { computed, onBeforeUnmount, onMounted, ref, watch, type Ref } from 'vue'

import type { CarouselConfig } from '@/api/types'

export type SlideState = 'is-active' | 'is-before' | 'is-after'

const DEFAULT_CONFIG: CarouselConfig = {
  autoplayMs: 5600,
  lockMs: 670,
  kenBurnsMs: 7000,
  swipePx: 48,
  offsetPx: 64,
  scale: 0.985,
}

export function useCarousel(
  count: Ref<number>,
  config: Ref<CarouselConfig | null>,
  options: { autoplay?: boolean } = {},
) {
  const cfg = computed(() => config.value ?? DEFAULT_CONFIG)

  const index = ref(0)
  /** 上一次激活的那张 —— 它正在离场，位移方向要跟本次切换保持一致 */
  const previousIndex = ref(0)
  const direction = ref<1 | -1>(1)
  const locked = ref(false)
  /** 用户主动暂停（鼠标悬停、点了暂停按钮） */
  const userPaused = ref(false)

  let lockTimer: ReturnType<typeof setTimeout> | null = null
  let autoplayTimer: ReturnType<typeof setTimeout> | null = null

  const reducedMotion =
    typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches

  const autoplayEnabled = computed(
    () => options.autoplay !== false && !reducedMotion && !userPaused.value,
  )

  // ---------------------------------------------------------------- 状态计算

  /** 某张幻灯片当前该挂什么状态类。渲染时逐张调用。 */
  function stateOf(i: number): SlideState {
    if (i === index.value) return 'is-active'
    // 正在离场的那张，位移方向跟本次切换一致，动画才连贯
    const isLeaving = i === previousIndex.value
    const goesBefore = isLeaving ? direction.value > 0 : i < index.value
    return goesBefore ? 'is-before' : 'is-after'
  }

  // ---------------------------------------------------------------- 切换

  function goTo(nextIndex: number, dir?: 1 | -1): void {
    const n = count.value
    if (n < 1) return

    const target = ((nextIndex % n) + n) % n
    if (target === index.value || locked.value) return

    direction.value = dir ?? (target > index.value ? 1 : -1)
    previousIndex.value = index.value
    index.value = target

    // 冷却期：这期间忽略后续切换请求
    locked.value = true
    if (lockTimer) clearTimeout(lockTimer)
    lockTimer = setTimeout(
      () => {
        locked.value = false
        lockTimer = null
      },
      reducedMotion ? 20 : cfg.value.lockMs,
    )

    // 手动切换后重新计时，别马上又自动翻页
    if (autoplayEnabled.value) scheduleAutoplay()
  }

  const next = () => goTo(index.value + 1, 1)
  const prev = () => goTo(index.value - 1, -1)

  function goToAbsolute(i: number): void {
    const dir: 1 | -1 = i > index.value ? 1 : -1
    goTo(i, dir)
  }

  // ---------------------------------------------------------------- 自动播放

  function clearAutoplay(): void {
    if (autoplayTimer) {
      clearTimeout(autoplayTimer)
      autoplayTimer = null
    }
  }

  function scheduleAutoplay(): void {
    clearAutoplay()
    if (!autoplayEnabled.value || document.hidden) return
    autoplayTimer = setTimeout(() => {
      autoplayTimer = null
      next()
      scheduleAutoplay()
    }, cfg.value.autoplayMs)
  }

  function pause(): void {
    userPaused.value = true
    clearAutoplay()
  }

  function resume(): void {
    userPaused.value = false
    scheduleAutoplay()
  }

  function onVisibilityChange(): void {
    if (document.hidden) clearAutoplay()
    else scheduleAutoplay()
  }

  // ---------------------------------------------------------------- 交互

  let pointerStartX: number | null = null

  function onPointerDown(e: PointerEvent): void {
    if (e.button !== 0) return
    pointerStartX = e.clientX
  }

  function onPointerUp(e: PointerEvent): void {
    if (pointerStartX === null) return
    const delta = e.clientX - pointerStartX
    pointerStartX = null
    if (Math.abs(delta) < cfg.value.swipePx) return
    if (delta < 0) next()
    else prev()
  }

  function onPointerCancel(): void {
    pointerStartX = null
  }

  function onKeydown(e: KeyboardEvent): void {
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      prev()
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      next()
    }
  }

  // ---------------------------------------------------------------- 生命周期

  watch(count, (n) => {
    if (n > 0 && index.value >= n) {
      index.value = 0
      previousIndex.value = 0
    }
  })

  onMounted(() => {
    document.addEventListener('visibilitychange', onVisibilityChange)
    scheduleAutoplay()
  })

  onBeforeUnmount(() => {
    document.removeEventListener('visibilitychange', onVisibilityChange)
    clearAutoplay()
    if (lockTimer) clearTimeout(lockTimer)
  })

  return {
    index,
    previousIndex,
    direction,
    locked,
    userPaused,
    autoplayEnabled,
    reducedMotion,
    cfg,
    stateOf,
    next,
    prev,
    goToAbsolute,
    pause,
    resume,
    onPointerDown,
    onPointerUp,
    onPointerCancel,
    onKeydown,
  }
}
