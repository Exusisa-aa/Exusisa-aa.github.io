<script setup lang="ts">
/**
 * 图片大图查看器。
 *
 * 状态放在 ui store 里，任何地方调 ui.openImage(src, alt) 就能打开。
 * 证书大图和项目截图共用这一个。
 */
import { computed, ref, watch } from 'vue'

import { useLightbox } from '@/composables/useLightbox'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()

const isOpen = computed(() => ui.imageSrc !== null)
const panel = ref<HTMLElement | null>(null)

useLightbox(isOpen, panel)

/**
 * 图片路径写错是这里最容易出的问题（比如 yaml 里写 .png、实际文件是 .jpg）。
 * 与其甩一个破图图标让人猜，不如把路径直接显示出来。
 */
const loadFailed = ref(false)
watch(
  () => ui.imageSrc,
  () => {
    loadFailed.value = false
  },
)

function close(): void {
  ui.closeImage()
}
</script>

<template>
  <Teleport to="body">
    <div
      ref="panel"
      class="cert-lightbox"
      :class="{ show: isOpen }"
      role="dialog"
      aria-modal="true"
      aria-label="图片大图"
      :aria-hidden="!isOpen"
    >
      <div class="cert-lightbox-bg" @click="close" />

      <img
        v-if="ui.imageSrc && !loadFailed"
        :src="ui.imageSrc"
        :alt="ui.imageAlt"
        @error="loadFailed = true"
      />

      <div v-else-if="loadFailed" class="cert-missing">
        <p class="title">图片没找到</p>
        <p class="path">{{ ui.imageSrc }}</p>
        <p class="hint">
          检查 <code>content/</code> 里写的路径，和 <code>web/public/</code> 下的实际文件
          <strong>完全一致</strong>（含扩展名）。文件名重复扩展名（<code>.png.png</code>）
          是最常见的坑 —— Windows 默认隐藏已知扩展名，容易看不出来。
        </p>
      </div>

      <button class="cert-close" type="button" aria-label="关闭" @click="close">×</button>
    </div>
  </Teleport>
</template>

<style scoped>
.cert-lightbox {
  position: fixed;
  inset: 0;
  z-index: var(--z-lightbox);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  /* 关着的时候必须彻底移出交互，否则会挡住底下的按钮 */
  pointer-events: none;
  transition: opacity 0.35s;
}

.cert-lightbox.show {
  opacity: 1;
  pointer-events: auto;
}

.cert-lightbox-bg {
  position: absolute;
  inset: 0;
  background: rgba(4, 4, 9, 0.86);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.cert-lightbox img {
  position: relative;
  z-index: 2;
  max-width: 88vw;
  max-height: 86vh;
  border-radius: 10px;
  box-shadow: 0 40px 100px rgba(0, 0, 0, 0.7);
  animation: certin 0.4s var(--ease);
}

/* 图片缺失时的提示卡 —— 替代浏览器那个破图图标 */
.cert-missing {
  position: relative;
  z-index: 2;
  max-width: 520px;
  padding: 2rem;
  margin: 0 6vw;
  text-align: center;
  border: 1px solid var(--line);
  border-radius: var(--r-card);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.cert-missing .title {
  font-family: var(--serif);
  font-size: 1.2rem;
  color: #fff;
  margin-bottom: 1rem;
}

.cert-missing .path {
  font-family: var(--mono);
  font-size: 0.78rem;
  color: var(--accent);
  word-break: break-all;
  margin-bottom: 1.2rem;
}

.cert-missing .hint {
  font-size: 0.84rem;
  color: var(--ink-faint);
  line-height: 1.8;
}

.cert-missing code {
  font-family: var(--mono);
  font-size: 0.86em;
  background: rgba(255, 255, 255, 0.07);
  padding: 0.12em 0.38em;
  border-radius: 4px;
}

.cert-close {
  position: absolute;
  top: 4vh;
  right: 4vw;
  z-index: 3;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid var(--line);
  color: #fff;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
  font-family: var(--sans);
}

.cert-close:hover {
  background: rgba(255, 255, 255, 0.16);
}
</style>
