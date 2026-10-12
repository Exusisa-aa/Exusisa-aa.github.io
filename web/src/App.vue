<script setup lang="ts">
import { computed, nextTick, onMounted, watch } from 'vue'
import type { Component } from 'vue'

import type { SectionType, StageSection } from '@/api/types'
import { useScrollStage } from '@/composables/useScrollStage'
import { useContentStore } from '@/stores/content'
import { useStageStore } from '@/stores/stage'
import { isNoAnim } from '@/utils/debug'

import AuroraBackground from '@/components/layout/AuroraBackground.vue'
import BackToTop from '@/components/layout/BackToTop.vue'
import DotNav from '@/components/layout/DotNav.vue'
import NoiseOverlay from '@/components/layout/NoiseOverlay.vue'
import ScrollScroller from '@/components/layout/ScrollScroller.vue'
import TopBar from '@/components/layout/TopBar.vue'

import AboutSection from '@/components/sections/AboutSection.vue'
import ContactSection from '@/components/sections/ContactSection.vue'
import HeroSection from '@/components/sections/HeroSection.vue'
import HonorsSection from '@/components/sections/HonorsSection.vue'
import MoreWorksSection from '@/components/sections/MoreWorksSection.vue'
import ProjectSection from '@/components/sections/ProjectSection.vue'
import SelfEvalSection from '@/components/sections/SelfEvalSection.vue'
import SkillsSection from '@/components/sections/SkillsSection.vue'

import ImageLightbox from '@/components/ui/ImageLightbox.vue'
import SectionBoundary from '@/components/ui/SectionBoundary.vue'

const content = useContentStore()
const stage = useStageStore()

const { observeScenes } = useScrollStage()

/** 分镜类型 → 组件 */
const SECTION_COMPONENTS: Record<SectionType, Component> = {
  hero: HeroSection,
  about: AboutSection,
  skills: SkillsSection,
  project: ProjectSection,
  carousel: MoreWorksSection,
  honors: HonorsSection,
  selfeval: SelfEvalSection,
  contact: ContactSection,
}

const ready = computed(() => !content.loading && content.bundle !== null)

function componentFor(section: StageSection): Component {
  return SECTION_COMPONENTS[section.type] ?? HeroSection
}

/** project 类型的分镜要把对应项目数据传进去 */
function propsFor(section: StageSection) {
  if (section.type !== 'project') return { section }
  return {
    section,
    project: section.projectId ? content.projectById(section.projectId) : null,
  }
}

onMounted(async () => {
  await content.load()

  if (content.bundle) {
    stage.setSections(content.bundle.stage.sections)
    await observeScenes()
    await applyDeepLink()
  }
})

/**
 * 直接跳到某一屏，方便分享和截图。
 * 支持两种写法：
 *   #p-mycat-cluster   锚点（分镜 id）
 *   ?scene=3           第 3 屏（从 0 数）
 */
async function applyDeepLink(): Promise<void> {
  // 等这一轮渲染落地再跳，否则分镜元素还没进 DOM
  await nextTick()

  const param = new URLSearchParams(location.search).get('scene')
  if (param !== null) {
    const n = Number(param)
    if (!Number.isNaN(n)) stage.goTo(n, 'instant')
  } else {
    const hash = location.hash.replace('#', '')
    if (hash && stage.sections.some((s) => s.id === hash)) {
      stage.goToId(hash, 'instant')
    }
  }

  if (isNoAnim()) {
    const el = stage.scrollerEl
    console.info(
      `[portfolio] deepLink target=${param} scrollTop=${el?.scrollTop} ` +
        `scrollHeight=${el?.scrollHeight} clientHeight=${el?.clientHeight}`,
    )
  }
}

// 分镜列表变化时重新建立观察器（正常情况下只会发生一次）
watch(
  () => stage.sections.length,
  async (n) => {
    if (n > 0) await observeScenes()
  },
)
</script>

<template>
  <!-- 极光光晕 + 噪点，固定在所有内容之下 -->
  <AuroraBackground />
  <NoiseOverlay />

  <!-- 加载失败时给出明确提示，而不是白屏 -->
  <div v-if="content.error" class="load-error">
    <p class="mono">内容加载失败</p>
    <p class="detail">{{ content.error }}</p>
    <p class="hint">
      本地开发时请确认后端已启动（<code>npm run dev</code> 会同时起前后端），
      或先执行 <code>npm run export</code> 生成静态快照。
    </p>
  </div>

  <template v-else-if="ready">
    <TopBar />
    <DotNav />

    <ScrollScroller>
      <!-- 每屏单独包一层错误边界：坏掉一屏只坏那一屏，不会连累后面的 -->
      <SectionBoundary
        v-for="(section, i) in stage.sections"
        :key="section.id"
        :section-id="section.id"
        :scene-index="i"
      >
        <!-- data-scene-index 会被透传到分镜根元素上，截图脚本和滚动定位都用它 -->
        <component :is="componentFor(section)" v-bind="propsFor(section)" :data-scene-index="i" />
      </SectionBoundary>
    </ScrollScroller>

    <BackToTop />
    <ImageLightbox />
  </template>

  <!-- 首屏加载：只留背景，避免闪一下骨架屏 -->
  <div v-else class="boot" aria-hidden="true" />
</template>

<style scoped>
.boot {
  position: fixed;
  inset: 0;
}

.load-error {
  position: fixed;
  inset: 0;
  z-index: var(--z-topbar);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.9rem;
  padding: 2rem;
  text-align: center;
}

.load-error .mono {
  font-family: var(--mono);
  font-size: 0.8rem;
  letter-spacing: 0.2em;
  color: var(--accent);
  text-transform: uppercase;
}

.load-error .detail {
  color: var(--ink);
  font-size: 1.05rem;
  max-width: 640px;
}

.load-error .hint {
  color: var(--ink-faint);
  font-size: 0.86rem;
  max-width: 560px;
  line-height: 1.8;
}

.load-error code {
  font-family: var(--mono);
  font-size: 0.82em;
  color: var(--ink-dim);
  background: rgba(255, 255, 255, 0.06);
  padding: 0.15em 0.4em;
  border-radius: 5px;
}
</style>
