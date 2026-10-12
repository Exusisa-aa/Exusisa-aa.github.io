/**
 * v-reveal —— 元素进入视口时淡入上浮。
 *
 * 用法：
 *   <h2 v-reveal>标题</h2>
 *   <p v-reveal="{ delay: 2 }">第二行</p>   <!-- 等价于手写 class="reveal d2" -->
 *
 * 关于 root：
 *   页面里的滚动容器 .scroller 正好是一屏高，所以元素在它内部滚动时
 *   相对**视口**的位置同样在变 —— 直接用 root: null（视口）即可，
 *   比传 root: scroller 更简单，也避开了"指令先于容器挂载"的时序问题。
 *
 * 触发后立刻 unobserve：入场动效只播一次，回滚上去再下来不重播。
 */

import type { Directive, DirectiveBinding } from 'vue'

import { shouldSkipAnimation } from '@/utils/debug'

interface RevealOptions {
  /** 阶梯延迟档位 1~6 */
  delay?: number
  /** 一次性观察器（默认共享），需要单独控制时传 true */
  standalone?: boolean
}

let sharedObserver: IntersectionObserver | null = null

function getSharedObserver(): IntersectionObserver {
  if (!sharedObserver) {
    sharedObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          entry.target.classList.add('in')
          sharedObserver?.unobserve(entry.target)
        }
      },
      {
        root: null,
        // 元素有一半进入视口就触发
        threshold: 0.5,
        // 底部留一点余量，避免元素刚露头就闪出来
        rootMargin: '0px 0px -5% 0px',
      },
    )
  }
  return sharedObserver
}

function resolveOptions(binding: DirectiveBinding<RevealOptions | number | undefined>): RevealOptions {
  const value = binding.value
  if (typeof value === 'number') return { delay: value }
  return value ?? {}
}

export const vReveal: Directive<HTMLElement, RevealOptions | number | undefined> = {
  mounted(el, binding) {
    const { delay } = resolveOptions(binding)

    el.classList.add('reveal')
    if (delay && delay > 0) el.classList.add(`d${Math.min(delay, 6)}`)

    // 系统开了"减少动态效果"、或加了 ?noanim 就直接显示，不要动画
    if (shouldSkipAnimation()) {
      el.classList.add('in')
      return
    }

    getSharedObserver().observe(el)
  },

  unmounted(el) {
    sharedObserver?.unobserve(el)
  },
}
