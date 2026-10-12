<script setup lang="ts">
/**
 * 核心能力 —— 技能分组卡片。
 *
 * 每张卡 hover 时顶部会亮起一条渐变发光线（::before），
 * 是这个组件唯一的"动"，克制得刚好。
 */
import { computed } from 'vue'

import type { StageSection } from '@/api/types'
import { useContentStore } from '@/stores/content'

const props = defineProps<{ section: StageSection }>()

const content = useContentStore()
const groups = computed(() => content.skills)
</script>

<template>
  <!-- tall：内容明显高于一屏，交给 .scene.tall 顶部对齐 -->
  <section :id="props.section.id" class="scene tall">
    <div class="scene-inner wide">
      <div class="scene-head">
        <p v-reveal class="scene-num">02</p>
        <h2 v-reveal="1" class="scene-title-sm">核心能力</h2>
        <p v-reveal="2" class="scene-sub-sm">按方向分组 · 每组都能在项目里找到对应</p>
      </div>

      <div class="skill-grid">
        <article
          v-for="(group, i) in groups"
          :key="group.id"
          v-reveal="Math.min(i + 2, 6)"
          class="card skill-card"
          :style="{ '--skill-accent': group.accent || 'var(--accent)' }"
        >
          <p class="skill-num">{{ String(i + 1).padStart(2, '0') }}</p>
          <h3 class="skill-name">{{ group.title }}</h3>

          <div class="skill-items">
            <div v-for="item in group.items" :key="item.name" class="skill-item">
              <span class="skill-item-name">{{ item.name }}</span>
              <span v-if="item.keywords.length" class="skill-item-kw">
                {{ item.keywords.join(' · ') }}
              </span>
            </div>
          </div>

          <p v-if="group.level" class="skill-proof">{{ group.level }}</p>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* 宽屏 3 列 → 5 张卡排成 3+2，比 2 列的 2+2+1 矮一整行 */
.skill-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--gap-grid);
  align-items: start;
}

.skill-card {
  padding: 1.5rem 1.4rem;
  position: relative;
  overflow: hidden;
}

/* hover 时顶部亮起的渐变线 —— 卡片"通电"的那一下 */
.skill-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--skill-accent), transparent);
  opacity: 0;
  transition: opacity 0.45s;
}

.skill-card:hover::before {
  opacity: 1;
}

.skill-num {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--skill-accent);
  letter-spacing: 0.2em;
}

.skill-name {
  font-family: var(--serif);
  font-weight: 600;
  font-size: 1.25rem;
  color: #fff;
  margin: 0.55rem 0 0.9rem;
}

.skill-items {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.skill-item {
  display: flex;
  flex-direction: column;
  gap: 0.18rem;
}

.skill-item-name {
  font-size: 0.82rem;
  color: var(--ink);
  font-weight: 400;
}

.skill-item-kw {
  font-size: 0.74rem;
  color: var(--ink-dim);
  line-height: 1.65;
}

.skill-proof {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--ink-faint);
  letter-spacing: 0.08em;
  margin-top: 1rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--line);
}

/* 中等屏退回 2 列 */
@media (max-width: 1199px) {
  .skill-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .skill-grid {
    grid-template-columns: 1fr;
  }
}
</style>
