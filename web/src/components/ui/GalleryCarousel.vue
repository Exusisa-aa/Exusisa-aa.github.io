<script setup lang="ts">
/**
 * 图片轮播 —— 项目主视觉用。
 *
 * 和 StageCarousel（更多作品那个）的区别：这个是纯淡入淡出，没有位移和推镜。
 * 因为素材是终端/控制台的桌面截图，画面里全是信息，加位移和缩放只会晃眼睛。
 *
 * 复用同一套 useCarousel 逻辑（自动播放、hover 暂停、键盘、滑动、防连击、
 * reduced-motion 降级），只是样式换成淡入淡出。
 */
import { computed } from 'vue'

import type { GalleryItem } from '@/api/types'
import { useCarousel } from '@/composables/useCarousel'
import { useContentStore } from '@/stores/content'
import { useUiStore } from '@/stores/ui'
import { assetUrl } from '@/utils/asset'
import { isNoAnim } from '@/utils/debug'

const props = defineProps<{
  items: GalleryItem[]
  /**
   * 轮播框宽高比。默认 1.93 是桌面向截图的常见比例。
   * 素材比例差得远（手绘、竖版）时传个更方的值，能少留很多黑边。
   * 无论填多少，图片都用 contain —— 只会留边，不会裁掉内容。
   */
  aspect?: number | null
}>()

const frameStyle = computed(() => ({
  aspectRatio: String(props.aspect ?? 1.93),
}))

const content = useContentStore()
const ui = useUiStore()

const count = computed(() => props.items.length)
const config = computed(() => content.carouselConfig)

const {
  index,
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
} = useCarousel(count, config, { autoplay: !isNoAnim() })

const current = computed(() => props.items[index.value] ?? null)

/** 点图放大 —— 截图里字很小，不放大基本看不清 */
function enlarge(): void {
  const item = current.value
  if (!item) return
  ui.openImage(assetUrl(item.src), item.alt || item.caption || '项目截图')
}
</script>

<template>
  <div
    class="gallery"
    role="region"
    aria-roledescription="轮播"
    aria-label="项目运行截图"
    tabindex="0"
    @keydown="onKeydown"
    @pointerdown="onPointerDown"
    @pointerup="onPointerUp"
    @pointercancel="onPointerCancel"
    @mouseenter="pause"
    @mouseleave="resume"
    @focusin="pause"
    @focusout="resume"
  >
    <div class="gallery-stage" :style="frameStyle">
      <figure
        v-for="(item, i) in props.items"
        :key="item.src"
        class="gallery-slide"
        :class="stateOf(i)"
        :aria-hidden="i !== index"
        :inert="i !== index || undefined"
      >
        <img
          :src="assetUrl(item.src)"
          :alt="item.alt || item.caption"
          loading="lazy"
          @click="enlarge"
        />
      </figure>

      <!-- 左上角说明当前这张是什么，比纯圆点好认 -->
      <span class="gallery-badge">{{ index + 1 }} / {{ count }}</span>

      <button class="gallery-arrow prev" type="button" aria-label="上一张" @click="prev">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M15 18l-6-6 6-6" />
        </svg>
      </button>

      <button class="gallery-arrow next" type="button" aria-label="下一张" @click="next">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M9 18l6-6-6-6" />
        </svg>
      </button>
    </div>

    <!-- 说明放在框外 —— 截图本身就是满幅信息，盖在上面会挡内容 -->
    <div class="gallery-bar">
      <p class="gallery-caption">{{ current?.caption }}</p>
      <div class="gallery-dots" role="tablist" aria-label="选择截图">
        <button
          v-for="(item, i) in props.items"
          :key="item.src"
          class="gallery-dot"
          :class="{ active: i === index }"
          type="button"
          role="tab"
          :aria-selected="i === index"
          :aria-label="item.caption || `第 ${i + 1} 张`"
          @click="goToAbsolute(i)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.gallery {
  width: 100%;
  border-radius: var(--r-frame);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: #000;
  /* 外层大投影 + 内侧顶部 1px 高光 —— 和视频演示框保持同一套"玻璃边缘"观感 */
  box-shadow: var(--shadow-frame), var(--highlight-inset);
}

.gallery-stage {
  position: relative;
  /* 比例由 aspect prop 通过内联样式给（默认 1.93），这里只兜底 */
  background: #06070c;
}

.gallery-slide {
  position: absolute;
  inset: 0;
  margin: 0;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  /* 只有淡入淡出，没有位移/缩放 */
  transition:
    opacity 0.55s ease,
    visibility 0s linear 0.55s;
}

.gallery-slide.is-active {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transition-delay: 0s;
}

.gallery-slide img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  cursor: zoom-in;
  display: block;
}

.gallery-badge {
  position: absolute;
  left: 14px;
  top: 14px;
  z-index: 4;
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  color: #fff;
  background: rgba(8, 8, 14, 0.62);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 0.32rem 0.66rem;
  border-radius: var(--r-pill);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.gallery-arrow {
  position: absolute;
  z-index: 5;
  top: 50%;
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  transform: translateY(-50%);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 50%;
  color: #fff;
  background: rgba(7, 8, 14, 0.55);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  /* 平时半透明，hover 画布时才明显 —— 别让按钮抢了截图的戏 */
  opacity: 0.35;
  transition:
    opacity 0.3s,
    background 0.3s,
    border-color 0.3s,
    transform 0.3s;
}

.gallery:hover .gallery-arrow,
.gallery:focus-within .gallery-arrow {
  opacity: 1;
}

.gallery-arrow:hover {
  background: rgba(119, 216, 239, 0.9);
  border-color: #77d8ef;
  color: #071014;
  transform: translateY(-50%) scale(1.06);
}

.gallery-arrow svg {
  width: 17px;
  height: 17px;
}

.gallery-arrow.prev {
  left: 14px;
}

.gallery-arrow.next {
  right: 14px;
}

.gallery-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1.1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.09);
  background: rgba(8, 9, 16, 0.6);
}

.gallery-caption {
  font-size: 0.78rem;
  color: var(--ink-dim);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gallery-dots {
  display: flex;
  gap: 0.4rem;
  flex: 0 0 auto;
}

.gallery-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  padding: 0;
  transition: all 0.3s;
}

.gallery-dot.active {
  background: var(--accent);
  transform: scale(1.4);
}

@media (max-width: 900px) {
  .gallery-arrow {
    /* 触屏没有 hover，按钮常显 */
    opacity: 1;
    width: 36px;
    height: 36px;
  }

  .gallery-caption {
    font-size: 0.72rem;
    white-space: normal;
  }
}

@media (prefers-reduced-motion: reduce) {
  .gallery-slide {
    transition-duration: 0.01ms !important;
  }
}
</style>
