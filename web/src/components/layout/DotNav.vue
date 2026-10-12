<script setup lang="ts">
/**
 * 右侧圆点导航 —— 当前屏的点会放大并发光。
 */
import { useStageStore } from '@/stores/stage'

const stage = useStageStore()
</script>

<template>
  <nav class="dots" aria-label="分镜快速跳转">
    <button
      v-for="(section, i) in stage.sections"
      :key="section.id"
      class="dot"
      :class="{ active: i === stage.activeIndex }"
      type="button"
      :aria-label="`跳到第 ${i + 1} 屏：${section.nav || section.id}`"
      :aria-current="i === stage.activeIndex ? 'true' : undefined"
      @click="stage.goTo(i)"
    />
  </nav>
</template>

<style scoped>
.dots {
  position: fixed;
  right: 2.4vw;
  top: 50%;
  transform: translateY(-50%);
  z-index: var(--z-topbar);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  padding: 0;
  transition: all 0.35s;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.6);
}

.dot.active {
  background: var(--accent);
  transform: scale(1.5);
  box-shadow: 0 0 12px var(--accent);
}

@media (max-width: 760px) {
  .dots {
    right: 1rem;
  }
}
</style>
