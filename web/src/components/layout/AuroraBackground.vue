<script setup lang="ts">
/**
 * 极光背景 —— 三个超大模糊光球。
 *
 * 颜色来自 CSS 变量 --c1 / --c2，由 stores/stage 按当前分镜写入，
 * 配合 tokens.css 里 1.4s 的 transition，整站色调会随滚动缓慢流转。
 *
 * mix-blend-mode: screen 让光球叠加时变亮而不是互相遮挡 —— 暗底上这很关键。
 */
import { onMounted, ref } from 'vue'

import { useAurora } from '@/composables/useAurora'

const blobEls = ref<HTMLElement[]>([])

useAurora(blobEls)

function register(el: Element | null, i: number): void {
  if (el) blobEls.value[i] = el as HTMLElement
}

onMounted(() => {
  // 清理掉可能的空位，避免补间循环里出现 undefined
  blobEls.value = blobEls.value.filter(Boolean)
})
</script>

<template>
  <div class="aurora" aria-hidden="true">
    <div :ref="(el) => register(el as Element | null, 0)" class="blob b1" />
    <div :ref="(el) => register(el as Element | null, 1)" class="blob b2" />
    <div :ref="(el) => register(el as Element | null, 2)" class="blob b3" />
  </div>
</template>

<style scoped>
.aurora {
  position: fixed;
  inset: 0;
  z-index: var(--z-aurora);
  overflow: hidden;
  pointer-events: none;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  mix-blend-mode: screen;
  opacity: 0.5;
  /* 换屏时颜色缓慢流转 —— 这是整站"活"起来的关键 */
  transition: background var(--theme-transition);
  will-change: transform;
}

.b1 {
  width: 52vmax;
  height: 52vmax;
  top: -18%;
  right: -12%;
  background: var(--c1);
}

.b2 {
  width: 42vmax;
  height: 42vmax;
  bottom: -22%;
  left: -10%;
  background: var(--c2);
}

.b3 {
  width: 30vmax;
  height: 30vmax;
  top: 38%;
  left: 30%;
  background: var(--c1);
  opacity: 0.26;
}

/* 移动端模糊半径过大很吃 GPU，收一收 */
@media (max-width: 760px) {
  .blob {
    filter: blur(80px);
    opacity: 0.42;
  }
}
</style>
