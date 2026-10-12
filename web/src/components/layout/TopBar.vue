<script setup lang="ts">
/**
 * 顶栏 —— logo + 分镜锚点 + 联系按钮。
 *
 * 导航项直接由 site.yaml 的 stage.sections 生成，
 * 增删分镜时这里不用改代码。
 */
import { computed } from 'vue'

import { useContentStore } from '@/stores/content'
import { useStageStore } from '@/stores/stage'

const content = useContentStore()
const stage = useStageStore()

/** 首屏自身不用放导航里，其余带 nav 文案的分镜都列出来 */
const navItems = computed(() =>
  stage.sections.filter((s) => s.type !== 'hero' && s.nav),
)

const logoText = computed(() => {
  const en = content.profile?.nameEn ?? ''
  return en || content.profile?.name || 'PORTFOLIO'
})

function go(id: string): void {
  stage.goToId(id)
}
</script>

<template>
  <header class="topbar">
    <div class="logo">
      {{ logoText.replace(/\s+/g, '') }}<b>.</b>
    </div>

    <nav class="top-links" aria-label="分镜导航">
      <a
        v-for="item in navItems"
        :key="item.id"
        href="#"
        :class="{ 'top-contact': item.type === 'contact' }"
        @click.prevent="go(item.id)"
      >
        {{ item.nav }}<span v-if="item.type === 'contact'"> ↗</span>
      </a>
    </nav>
  </header>
</template>

<style scoped>
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-topbar);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.4rem 4vw;
  /* 顶栏要能穿透点击，只有链接本身可点 */
  pointer-events: none;
}

.topbar a,
.logo {
  pointer-events: auto;
}

.logo {
  font-family: var(--mono);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--ink);
}

.logo b {
  color: var(--accent);
  transition: color var(--theme-transition);
}

.top-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.top-links a {
  font-family: var(--mono);
  font-size: 0.86rem;
  color: var(--ink-dim);
  text-decoration: none;
  letter-spacing: 0.05em;
  transition: color 0.3s;
  white-space: nowrap;
}

.top-links a:hover {
  color: var(--ink);
}

/* 联系按钮做成胶囊，和普通导航拉开层级 */
.top-contact {
  color: var(--ink) !important;
  padding: 0.48rem 1.08rem;
  border: 1px solid var(--line);
  border-radius: var(--r-pill);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.03);
  transition: border-color 0.3s;
}

.top-contact:hover {
  border-color: rgba(255, 255, 255, 0.3);
}

/* 小屏放不下这么多导航项，只留联系按钮 —— 右侧圆点导航接管 */
@media (max-width: 900px) {
  .top-links a:not(.top-contact) {
    display: none;
  }
}
</style>
