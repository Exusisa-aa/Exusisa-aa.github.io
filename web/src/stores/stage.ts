/**
 * 分镜状态 —— 管理"当前在第几屏"和每屏的主题色切换。
 *
 * 主题色写在 document.documentElement 的 CSS 变量上（--c1/--c2/--accent），
 * 配合 tokens.css 里 1.4s 的 transition，整站色调就会随滚动缓慢流转。
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import type { StageSection, Theme } from '@/api/types'

export const useStageStore = defineStore('stage', () => {
  const sections = ref<StageSection[]>([])
  const activeIndex = ref(0)

  /** 滚动容器的 DOM 引用。IntersectionObserver 和圆点导航都要用它当 root。 */
  const scrollerEl = ref<HTMLElement | null>(null)

  const activeSection = computed<StageSection | null>(() => sections.value[activeIndex.value] ?? null)

  function setSections(list: StageSection[]): void {
    sections.value = list
  }

  function setScroller(el: HTMLElement | null): void {
    scrollerEl.value = el
  }

  /** 把一屏的主题色写到 :root 上 */
  function applyTheme(theme: Partial<Theme> | null | undefined): void {
    if (!theme) return
    const root = document.documentElement
    if (theme.c1) root.style.setProperty('--c1', theme.c1)
    if (theme.c2) root.style.setProperty('--c2', theme.c2)
    if (theme.accent) root.style.setProperty('--accent', theme.accent)
  }

  function setActive(index: number): void {
    if (index < 0 || index >= sections.value.length) return
    activeIndex.value = index
    applyTheme(sections.value[index]?.theme)
  }

  /** 滚到第 index 屏 */
  function goTo(index: number, behavior: ScrollBehavior = 'smooth'): void {
    const container = scrollerEl.value
    const target = sections.value[index]
    if (!container || !target) return

    const el = container.querySelector<HTMLElement>(`#${CSS.escape(target.id)}`)
    if (el) el.scrollIntoView({ behavior, block: 'start' })
  }

  function goToId(id: string, behavior: ScrollBehavior = 'smooth'): void {
    const index = sections.value.findIndex((s) => s.id === id)
    if (index >= 0) goTo(index, behavior)
  }

  /**
   * 分镜编号，形如 "01"、"02"。
   *
   * 按在 site.yaml 里的位置算（从 01 起），**不要在组件里写死** ——
   * 增删分镜（比如把首屏藏起来）时，写死的号码会立刻对不上。
   */
  function numberOf(id: string): string {
    const i = sections.value.findIndex((s) => s.id === id)
    return String(Math.max(i + 1, 1)).padStart(2, '0')
  }

  return {
    numberOf,
    sections,
    activeIndex,
    activeSection,
    scrollerEl,
    setSections,
    setScroller,
    applyTheme,
    setActive,
    goTo,
    goToId,
  }
})
