/**
 * Lightbox 的通用行为：Esc 关闭、锁滚动、焦点陷阱。
 *
 * 焦点陷阱是容易被忽略但很重要的一环 —— 如果不管，打开大图后用 Tab 键
 * 还能跑到背后的页面上去，键盘和读屏用户会完全迷失。
 */

import { nextTick, onBeforeUnmount, watch, type Ref } from 'vue'

export function useLightbox(isOpen: Ref<boolean>, panel: Ref<HTMLElement | null>) {
  let lastFocused: HTMLElement | null = null
  let lockedOverflow = ''

  function onKeydown(e: KeyboardEvent): void {
    if (e.key === 'Escape') {
      isOpen.value = false
      return
    }
    if (e.key !== 'Tab') return

    const root = panel.value
    if (!root) return

    const focusables = root.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    )
    if (focusables.length === 0) {
      e.preventDefault()
      return
    }

    const first = focusables[0]
    const last = focusables[focusables.length - 1]
    const active = document.activeElement as HTMLElement | null

    if (e.shiftKey && (active === first || !root.contains(active))) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && active === last) {
      e.preventDefault()
      first.focus()
    }
  }

  watch(isOpen, async (open) => {
    if (open) {
      lastFocused = document.activeElement as HTMLElement | null

      // 锁住页面滚动
      lockedOverflow = document.body.style.overflow
      document.body.style.overflow = 'hidden'

      document.addEventListener('keydown', onKeydown)

      // 等 DOM 渲染出来再抢焦点
      await nextTick()
      const target = panel.value?.querySelector<HTMLElement>('button, [href], [tabindex]')
      target?.focus()
    } else {
      document.removeEventListener('keydown', onKeydown)
      document.body.style.overflow = lockedOverflow

      // 焦点还给打开它的那个元素
      lastFocused?.focus?.()
      lastFocused = null
    }
  })

  onBeforeUnmount(() => {
    document.removeEventListener('keydown', onKeydown)
    if (lockedOverflow !== undefined) document.body.style.overflow = lockedOverflow
  })
}
