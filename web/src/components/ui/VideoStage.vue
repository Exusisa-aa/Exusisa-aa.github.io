<script setup lang="ts">
/**
 * 演示视频框 —— 全站细节最密的一个组件。
 *
 * 三个来自参考站的克制之处：
 *   1. 进度条默认 opacity 0，hover 才浮现；底下垫一层渐变保证可读
 *   2. 播放/暂停按钮默认完全隐藏，只在用户主动暂停时出现
 *   3. 框体用 inset 0 1px 0 的白色内阴影模拟"玻璃边缘高光"，
 *      再加一道 135° 对角扫光 —— 纯 CSS 做出屏幕反射的质感
 *
 * 进度条支持点击和拖动（用 Pointer Capture，鼠标划出元素也不会断）。
 */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import type { VideoItem } from '@/api/types'
import { formatTime, useVideoStage } from '@/composables/useVideoStage'
import { assetUrl } from '@/utils/asset'

const props = defineProps<{
  video: VideoItem
  /** 悬停才显示进度条 */
  seekOnHover?: boolean
}>()

const videoEl = ref<HTMLVideoElement | null>(null)
const progressEl = ref<HTMLElement | null>(null)

const { feedback, play, pause, toggleFromUser, seekToRatio } = useVideoStage(videoEl)

const currentTime = ref(0)
const duration = ref(0)
const seeking = ref(false)

const fillPercent = computed(() =>
  duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0,
)

const timeLabel = computed(
  () => `${formatTime(currentTime.value)} / ${formatTime(duration.value)}`,
)

/** 用户拖到框内时别自动播放打断他 */
const isUserPaused = computed(() => feedback.value === 'paused')
const isPlayConfirming = computed(() => feedback.value === 'playing')

function onTimeUpdate(): void {
  const el = videoEl.value
  if (!el) return
  currentTime.value = el.currentTime
  duration.value = el.duration || 0
}

function onLoadedMetadata(): void {
  duration.value = videoEl.value?.duration || 0
}

function seekFromEvent(e: PointerEvent): void {
  const el = progressEl.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const ratio = (e.clientX - rect.left) / rect.width
  seekToRatio(ratio)
}

function onPointerDown(e: PointerEvent): void {
  seeking.value = true
  seekFromEvent(e)
  ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent): void {
  if (seeking.value) seekFromEvent(e)
}

function onPointerUp(): void {
  seeking.value = false
}

onMounted(() => {
  // 自动播放可能被浏览器策略拒绝，静默处理即可 —— 用户点一下就能播
  play(false)
})

onBeforeUnmount(() => {
  pause(false)
})
</script>

<template>
  <div
    class="demo-frame"
    :class="{ 'is-user-paused': isUserPaused, 'is-play-confirming': isPlayConfirming }"
  >
    <video
      ref="videoEl"
      :poster="assetUrl(props.video.poster) || undefined"
      autoplay
      muted
      loop
      playsinline
      preload="metadata"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @click="toggleFromUser"
    >
      <source :src="assetUrl(props.video.src)" type="video/mp4" />
    </video>

    <span v-if="props.video.caption" class="demo-badge">{{ props.video.caption }}</span>

    <!-- 播放/暂停：默认隐藏，见 .is-user-paused / .is-play-confirming -->
    <button class="demo-playback-toggle" type="button" :aria-label="isUserPaused ? '播放演示视频' : '暂停演示视频'" @click="toggleFromUser">
      <svg class="demo-play-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M8 5v14l11-7z" />
      </svg>
      <svg class="demo-pause-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M7 5h4v14H7zM13 5h4v14h-4z" />
      </svg>
    </button>

    <div
      ref="progressEl"
      class="demo-progress"
      :class="{ 'always-show': !props.seekOnHover }"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <div class="demo-progress-track">
        <div class="demo-progress-fill" :style="{ width: `${fillPercent}%` }" />
      </div>
      <span class="demo-time">{{ timeLabel }}</span>
    </div>
  </div>
</template>

<style scoped>
.demo-frame {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 10;
  border-radius: var(--r-frame);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: #000;
  /* 外面的大投影 + 内侧顶部 1px 高光 —— 后者是"玻璃边缘"的来源 */
  box-shadow: var(--shadow-frame), var(--highlight-inset);
  transform: translateZ(0);
}

.demo-frame video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  cursor: pointer;
}

/* 对角扫光：一道很淡的白色渐变被 ::before 扫过去 */
.demo-frame::before {
  content: '';
  position: absolute;
  top: -30%;
  left: -30%;
  width: 60%;
  height: 160%;
  background: linear-gradient(
    100deg,
    transparent,
    rgba(255, 255, 255, 0.09),
    transparent
  );
  transform: translateX(-120%) rotate(8deg);
  pointer-events: none;
  z-index: 5;
}

.demo-frame:hover::before {
  animation: sweep 1.6s var(--ease-soft) 0.15s 1;
}

/* 左上角常驻的一层斜向高光 */
.demo-frame::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.14), transparent 42%);
}

.demo-badge {
  position: absolute;
  left: 14px;
  top: 14px;
  z-index: 6;
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  color: #fff;
  background: rgba(8, 8, 14, 0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 0.35rem 0.7rem;
  border-radius: var(--r-pill);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

/* ---- 播放/暂停按钮 ---- */
.demo-playback-toggle {
  position: absolute;
  left: 50%;
  top: 50%;
  z-index: 8;
  width: 68px;
  height: 68px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.28);
  color: #fff;
  background: rgba(7, 7, 13, 0.54);
  backdrop-filter: blur(18px) saturate(1.25);
  -webkit-backdrop-filter: blur(18px) saturate(1.25);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.38), var(--highlight-inset);
  /* 默认完全隐藏：不打扰自动播放 */
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transform: translate(-50%, -50%) scale(0.88);
  transition:
    opacity 0.2s ease,
    transform 0.2s ease,
    visibility 0s linear 0.2s;
}

.demo-playback-toggle svg {
  position: absolute;
  width: 27px;
  height: 27px;
  fill: currentColor;
}

.demo-pause-icon {
  display: none;
}

/* 用户暂停了：按钮持续显示 */
.demo-frame.is-user-paused .demo-playback-toggle,
/* 用户点了播放：显示暂停图标作为反馈 */
.demo-frame.is-play-confirming .demo-playback-toggle {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: translate(-50%, -50%) scale(1);
  transition-delay: 0s;
}

.demo-frame.is-play-confirming .demo-play-icon {
  display: none;
}

.demo-frame.is-play-confirming .demo-pause-icon {
  display: block;
}

.demo-playback-toggle:hover {
  background: rgba(7, 7, 13, 0.68);
  border-color: rgba(255, 255, 255, 0.45);
}

/* ---- 进度条 ---- */
.demo-progress {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 6;
  height: 30px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  cursor: pointer;
  /* 默认隐藏，hover 才浮现 —— 底下垫渐变保证文字可读 */
  opacity: 0;
  transition: opacity 0.3s;
  background: linear-gradient(transparent, rgba(4, 4, 9, 0.65));
}

.demo-frame:hover .demo-progress,
.demo-progress.always-show {
  opacity: 1;
}

.demo-progress-track {
  position: relative;
  flex: 1;
  height: 4px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.22);
}

.demo-progress-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  border-radius: 3px;
  background: var(--accent);
  transition: background var(--theme-transition);
}

.demo-progress-fill::after {
  content: '';
  position: absolute;
  right: -7px;
  top: 50%;
  transform: translateY(-50%);
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.6);
}

.demo-time {
  flex: 0 0 auto;
  margin-left: 12px;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 0.05em;
}

@media (max-width: 760px) {
  .demo-playback-toggle {
    width: 58px;
    height: 58px;
  }
}
</style>
