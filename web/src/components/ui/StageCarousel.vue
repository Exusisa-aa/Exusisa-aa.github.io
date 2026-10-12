<script setup lang="ts">
/**
 * 固定舞台轮播 —— 只负责**图片**，不负责文字。
 *
 * 文字（项目名、简介、标签、链接）由调用方放在组件外面，
 * 通过 v-model:index 跟着当前张切换。这样做是因为之前文字是绝对定位
 * 叠在图片上的，会把界面截图盖掉一大块 —— 而截图恰恰是要给人看的东西。
 *
 * 图片用 contain 而不是 cover：这些是企业系统的真实界面截图，
 * 用 cover 会裁掉两侧的内容；contain 保证整张都能看到。
 * 同理也没做 Ken Burns 推镜 —— 那会放大后裁掉边缘。
 */
import { computed, ref, watch } from 'vue'

import type { CarouselConfig, Project } from '@/api/types'
import { useCarousel } from '@/composables/useCarousel'
import { useUiStore } from '@/stores/ui'
import { assetUrl } from '@/utils/asset'
import { isNoAnim } from '@/utils/debug'

const props = defineProps<{
  projects: Project[]
  config: CarouselConfig | null
  /** 当前第几张，配合 v-model:index 与外部文字同步 */
  index?: number
  /** 底部左侧的说明文案 */
  footNote?: string
  profileUrl?: string
}>()

const emit = defineEmits<{ 'update:index': [number] }>()

const ui = useUiStore()

const count = computed(() => props.projects.length)
const configRef = computed(() => props.config)

const {
  index,
  cfg,
  stateOf,
  next,
  prev,
  goToAbsolute,
  pause,
  resume,
  onPointerDown,
  onPointerUp,
  onPointerCancel,
  onKeydown,
} = useCarousel(count, configRef, { autoplay: !isNoAnim() })

// 把内部下标同步给外部，外部的文字面板才知道该显示哪一个项目
watch(index, (i) => emit('update:index', i), { immediate: true })

const rootStyle = computed(() => ({ '--kb-duration': `${cfg.value.kenBurnsMs}ms` }))

function isActive(i: number): boolean {
  return i === index.value
}

/** 没有封面图时用渐变占位块兜底 */
function coverStyle(project: Project) {
  if (project.cover) return {}
  const theme = project.theme
  const c1 = theme?.c1 ?? 'var(--c1)'
  const c2 = theme?.c2 ?? 'var(--c2)'
  return {
    background:
      `radial-gradient(circle at 74% 34%, color-mix(in srgb, ${c1} 34%, transparent), transparent 58%),` +
      `radial-gradient(circle at 22% 82%, color-mix(in srgb, ${c2} 20%, transparent), transparent 52%),` +
      `#0a0c15`,
  }
}

// ---------------------------------------------------------------- 点击放大
// 拖动翻页和点击放大都挂在同一块区域上，所以要区分：
// 按下到抬起之间指针移动超过阈值就算拖动，不触发放大。

let startX: number | null = null
const dragged = ref(false)

function onDown(e: PointerEvent): void {
  startX = e.clientX
  dragged.value = false
  onPointerDown(e)
}

function onUp(e: PointerEvent): void {
  if (startX !== null && Math.abs(e.clientX - startX) > 12) dragged.value = true
  onPointerUp(e)
}

function enlarge(): void {
  if (dragged.value) return
  const project = props.projects[index.value]
  if (!project?.cover) return
  ui.openImage(assetUrl(project.cover), `${project.title} 界面截图`)
}
</script>

<template>
  <div
    class="project-carousel"
    :style="rootStyle"
    role="region"
    aria-roledescription="轮播"
    aria-label="更多作品"
    tabindex="0"
    @keydown="onKeydown"
    @pointerdown="onDown"
    @pointerup="onUp"
    @pointercancel="onPointerCancel"
    @mouseenter="pause"
    @mouseleave="resume"
    @focusin="pause"
    @focusout="resume"
  >
    <div class="project-stage">
      <div
        v-for="(project, i) in props.projects"
        :key="project.id"
        class="project-slide"
        :class="stateOf(i)"
        :aria-hidden="!isActive(i)"
        :inert="!isActive(i) || undefined"
      >
        <img
          v-if="project.cover"
          class="project-media"
          :src="assetUrl(project.cover)"
          :alt="`${project.title} 界面截图，点击放大`"
          loading="lazy"
          @click="enlarge"
        />
        <div v-else class="project-media project-media--placeholder" :style="coverStyle(project)" />
      </div>

      <button class="project-arrow prev" type="button" aria-label="上一个项目" @click="prev">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M15 18l-6-6 6-6" />
        </svg>
      </button>

      <button class="project-arrow next" type="button" aria-label="下一个项目" @click="next">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M9 18l6-6-6-6" />
        </svg>
      </button>
    </div>

    <div class="project-footer">
      <span class="project-footer-note">{{ props.footNote }}</span>

      <div class="project-dots" role="tablist" aria-label="选择项目">
        <button
          v-for="(project, i) in props.projects"
          :key="project.id"
          class="project-dot"
          :class="{ active: isActive(i) }"
          type="button"
          role="tab"
          :aria-selected="isActive(i)"
          :aria-label="project.title"
          @click="goToAbsolute(i)"
        />
      </div>

      <a
        v-if="props.profileUrl"
        class="project-profile-link"
        :href="props.profileUrl"
        target="_blank"
        rel="noopener"
      >
        全部仓库 ↗
      </a>
    </div>
  </div>
</template>

<style scoped>
.project-carousel {
  position: relative;
  width: 100%;
  min-width: 0;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--r-carousel);
  background: #0d0e16;
  box-shadow: 0 34px 90px rgba(0, 0, 0, 0.38);
  isolation: isolate;
}

.project-stage {
  position: relative;
  /*
    用比例撑高度、不用固定 vh —— 这样框和截图同形，
    contain 下几乎没有黑边，切张时高度也不会跳。
    四张封面都是 2560×1271 ~ 2560×1379，约 1.9:1。
  */
  aspect-ratio: 1.9;
  overflow: hidden;
  background: #06070c;
}

/* ---- 幻灯片三态：只做位移 + 淡入淡出 ---- */
.project-slide {
  position: absolute;
  inset: 0;
  overflow: hidden;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transform: translate3d(64px, 0, 0);
  transition:
    opacity 0.65s ease,
    transform 0.65s var(--ease),
    visibility 0s linear 0.65s;
}

.project-slide.is-before {
  transform: translate3d(-64px, 0, 0);
}

.project-slide.is-active {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: none;
  transition-delay: 0s;
}

.project-media {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  /* contain：完整显示界面，不裁切 */
  object-fit: contain;
  cursor: zoom-in;
  display: block;
}

.project-media--placeholder {
  cursor: default;
  object-fit: cover;
}

/* ---- 左右箭头 ---- */
.project-arrow {
  position: absolute;
  z-index: 5;
  top: 50%;
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  transform: translateY(-50%);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 50%;
  color: #fff;
  background: rgba(7, 8, 14, 0.55);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  opacity: 0.45;
  transition:
    opacity 0.3s,
    background 0.3s,
    border-color 0.3s,
    transform 0.3s;
}

.project-carousel:hover .project-arrow,
.project-carousel:focus-within .project-arrow {
  opacity: 1;
}

.project-arrow:hover {
  background: rgba(119, 216, 239, 0.9);
  border-color: #77d8ef;
  color: #071014;
  transform: translateY(-50%) scale(1.06);
}

.project-arrow svg {
  width: 18px;
  height: 18px;
}

.project-arrow.prev {
  left: 14px;
}

.project-arrow.next {
  right: 14px;
}

/* ---- 底部条 ---- */
.project-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-width: 0;
  padding: 0.72rem 1.1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.09);
  color: var(--ink-faint);
  font-family: var(--mono);
  font-size: 0.65rem;
}

.project-footer-note {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-dots {
  display: flex;
  gap: 0.4rem;
  flex: 0 0 auto;
}

.project-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  padding: 0;
  transition: all 0.3s;
}

.project-dot.active {
  background: var(--accent);
  transform: scale(1.4);
}

.project-profile-link {
  flex: 0 0 auto;
  color: rgba(255, 255, 255, 0.76);
  text-decoration: none;
  transition: color 0.25s;
  white-space: nowrap;
}

.project-profile-link:hover {
  color: #fff;
}

@media (prefers-reduced-motion: reduce) {
  .project-slide {
    transition-duration: 0.01ms !important;
    transform: none !important;
  }
}

@media (max-width: 900px) {
  .project-arrow {
    /* 触屏没有 hover，按钮常显 */
    opacity: 1;
    width: 38px;
    height: 38px;
  }

  .project-footer-note {
    display: none;
  }
}
</style>
