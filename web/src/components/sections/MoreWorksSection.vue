<script setup lang="ts">
/**
 * 更多作品 —— 左边是当前项目的文字，右边是只放图的轮播。
 *
 * 文字不叠在图上：这些是企业系统的真实界面截图，盖住一半就看不到东西了。
 * 文字面板通过 v-model:index 跟着轮播的当前张走。
 */
import { computed, ref } from 'vue'

import type { Project, StageSection } from '@/api/types'
import { useContentStore } from '@/stores/content'
import { useStageStore } from '@/stores/stage'
import StageCarousel from '@/components/ui/StageCarousel.vue'

const props = defineProps<{ section: StageSection }>()

const content = useContentStore()
const stage = useStageStore()

const projects = computed(() => content.carouselProjects)

/** 与轮播同步的下标 */
const activeIndex = ref(0)
const active = computed<Project | null>(() => projects.value[activeIndex.value] ?? null)

/** 按钮只渲染带 url 的条目；url 为空的是纯说明条 */
const activeLinks = computed(() => (active.value?.links ?? []).filter((l) => l.url))
const activeNote = computed(() => active.value?.links.find((l) => l.note)?.note ?? '')

const footNote = computed(() => {
  const n = projects.value.length
  const withCover = projects.value.filter((p) => p.cover).length
  // 如实说明有多少个项目还没有截图，避免看起来像"图挂了"。
  // 别写「均可访问源码」之类的话 —— 这些是企业内部项目，和机密说明冲突。
  return withCover < n
    ? `${n} 个项目 · ${withCover} 个已配图，其余待补充`
    : `${n} 个项目`
})

const profileUrl = computed(
  () => content.profile?.contacts.find((c) => c.type === 'github')?.href ?? undefined,
)
</script>

<template>
  <section :id="props.section.id" class="scene">
    <div class="scene-inner">
      <div class="scene-text">
        <p v-reveal class="scene-num">{{ stage.numberOf(props.section.id) }}</p>
        <h2 v-reveal="1" class="scene-title-sm">更多作品</h2>
        <p v-reveal="2" class="scene-sub-sm">企业级项目 · 界面为实际运行截图</p>

        <!-- 跟着轮播切换的项目信息 -->
        <div v-if="active" v-reveal="3" class="works-detail">
          <p class="works-kicker">
            {{ String(activeIndex + 1).padStart(2, '0') }} ·
            {{ (active.category[0] || 'PROJECT').toUpperCase() }}
          </p>
          <h3 class="works-title">{{ active.title }}</h3>
          <p class="works-desc">{{ active.summary }}</p>

          <!-- 不截断：标签写几个就显示几个。
               之前这里 slice(0,6)，把第 7、8 个悄悄丢了 —— 数据里有的东西
               页面上看不见，比排版溢出更难发现。 -->
          <ul v-if="active.tags.length" class="works-tags" aria-label="技术栈">
            <li v-for="tag in active.tags" :key="tag">{{ tag }}</li>
          </ul>

          <!-- 没有按钮也没有说明时整块不渲染，否则会留下一段空白间距 -->
          <div v-if="activeLinks.length || activeNote" class="works-actions">
            <a
              v-for="link in activeLinks"
              :key="link.url + link.label"
              class="btn-sm primary"
              :href="link.url"
              target="_blank"
              rel="noopener"
            >
              {{ link.label }} ↗
            </a>
            <span v-if="activeNote" class="works-link-note">{{ activeNote }}</span>
          </div>
        </div>
      </div>

      <div v-reveal="2" class="scene-visual works-visual">
        <StageCarousel
          v-if="projects.length"
          v-model:index="activeIndex"
          :projects="projects"
          :config="content.carouselConfig"
          :foot-note="footNote"
          :profile-url="profileUrl"
        />

        <p v-else class="empty-hint">项目数据还没加载</p>

        <!-- 说明放在轮播正下方：整块的提示，不是某一张的注释 -->
        <p v-if="projects.length" class="works-note">
          <span class="works-note-mark" aria-hidden="true">※</span>
          企业级项目，机密，仅开发者可见
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.works-detail {
  margin-top: 1.6rem;
  max-width: 460px;
}

.works-kicker {
  font-family: var(--mono);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: var(--accent);
  transition: color var(--theme-transition);
}

.works-title {
  font-family: var(--serif);
  font-weight: 700;
  font-size: clamp(1.6rem, 2.4vw, 2.1rem);
  line-height: 1.2;
  color: #fff;
  margin: 0.7rem 0 0.8rem;
}

.works-desc {
  font-size: 0.92rem;
  line-height: 1.8;
  color: var(--ink-dim);
  margin-bottom: 1.1rem;
}

.works-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 1.2rem;
}

.works-tags li {
  padding: 0.34rem 0.64rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: var(--r-pill);
  color: rgba(241, 241, 246, 0.72);
  background: rgba(8, 9, 16, 0.36);
  font-family: var(--mono);
  font-size: 0.64rem;
  letter-spacing: 0.03em;
}

.works-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.works-link-note {
  font-size: 0.74rem;
  line-height: 1.6;
  color: var(--ink-dim);
}

/* 轮播 + 下方说明竖着排 */
.works-visual {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  gap: 1rem;
}

/* 机密提示 —— 用 accent 色和 ※ 标记让它被看见，
   别用最淡那一档，那样等于没写 */
.works-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  line-height: 1.6;
  color: var(--ink-dim);
}

.works-note-mark {
  color: var(--accent);
  font-size: 0.9rem;
  transition: color var(--theme-transition);
}

.empty-hint {
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--ink-faint);
}

@media (max-width: 900px) {
  .works-detail {
    margin-left: auto;
    margin-right: auto;
    text-align: left;
  }
}
</style>
