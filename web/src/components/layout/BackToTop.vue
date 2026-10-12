<script setup lang="ts">
/**
 * 回到首屏按钮 —— 滚过一屏之后才出现。
 */
import { onBeforeUnmount, onMounted } from 'vue'

import { useStageStore } from '@/stores/stage'
import { useUiStore } from '@/stores/ui'

const stage = useStageStore()
const ui = useUiStore()

function onScroll(): void {
  const el = stage.scrollerEl
  if (!el) return
  ui.setShowBackTop(el.scrollTop > window.innerHeight * 0.5)
}

function backToTop(): void {
  stage.goTo(0)
}

onMounted(() => {
  // 容器在子组件挂载时才有引用，这里用 rAF 等一帧
  requestAnimationFrame(() => {
    stage.scrollerEl?.addEventListener('scroll', onScroll, { passive: true })
  })
})

onBeforeUnmount(() => {
  stage.scrollerEl?.removeEventListener('scroll', onScroll)
})
</script>

<template>
  <button
    class="back-top"
    :class="{ show: ui.showBackTop }"
    type="button"
    aria-label="回到首屏"
    @click="backToTop"
  >
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2.5"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="M12 19V5M5 12l7-7 7 7" />
    </svg>
  </button>
</template>

<style scoped>
.back-top {
  position: fixed;
  right: 2.4vw;
  bottom: 2.4rem;
  z-index: var(--z-topbar);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--line);
  color: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  /* 默认藏起来，滚过一屏才浮现 */
  opacity: 0;
  transform: translateY(16px);
  pointer-events: none;
  transition: all 0.35s;
}

.back-top.show {
  opacity: 1;
  transform: none;
  pointer-events: auto;
}

.back-top:hover {
  background: var(--accent);
  color: #0a0a12;
  border-color: var(--accent);
  transform: translateY(-3px);
}

.back-top svg {
  width: 18px;
  height: 18px;
}

@media (max-width: 760px) {
  .back-top {
    display: none;
  }
}
</style>
