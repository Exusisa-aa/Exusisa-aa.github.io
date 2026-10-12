<script setup lang="ts">
/** 首屏 —— 大标题 + 求职状态 + 进入作品的入口 */
import { computed } from 'vue'

import type { StageSection } from '@/api/types'
import { useContentStore } from '@/stores/content'
import { useStageStore } from '@/stores/stage'
import { assetUrl } from '@/utils/asset'

const props = defineProps<{ section: StageSection }>()

const content = useContentStore()
const stage = useStageStore()

const profile = computed(() => content.profile)

/** status 决定状态行的后缀文案，不要在 profile.yaml 里重复写 */
const STATUS_LABEL: Record<string, string> = {
  open: '求职中',
  busy: '暂不看机会',
  closed: '不开放',
}

const statusLabel = computed(() =>
  profile.value ? (STATUS_LABEL[profile.value.status] ?? '') : '',
)

/** 首屏的两个按钮：我的介绍 / 新标签页预览简历 */
function goIntro(): void {
  // 找「关于我」那一屏，而不是写死下标 —— 分镜顺序在 site.yaml 里随时可能调。
  const intro = content.sections.find((s) => s.type === 'about') ?? content.sections[1]
  if (intro) stage.goToId(intro.id)
}

/**
 * 简历地址 —— 只做预览，不加 download 属性。
 * 浏览器会用自己的 PDF 阅读器在新标签页打开，想存的人可以自己存。
 *
 * 注：live 模式下后端返回 Content-Disposition: inline；
 * static 模式（GitHub Pages）直接托管同一个 PDF，同样是内联预览。
 */
const resumeUrl = computed(() => assetUrl(profile.value?.resumePdf) || null)
</script>

<template>
  <section :id="props.section.id" class="scene center">
    <div class="scene-inner">
      <div>
        <p v-reveal class="scene-tag hero-tag">
          // {{ profile?.name }} · 个人作品集 — {{ new Date().getFullYear() }}
        </p>

        <h1 v-reveal="1" class="hero-title">
          {{ profile?.heroTitle }}<br />
          <span class="grad">{{ profile?.heroTitleAccent }}</span>
        </h1>

        <p v-reveal="2" class="hero-sub">{{ profile?.headline }}</p>

        <p v-reveal="3" class="hero-status">
          {{ profile?.location }}
          <template v-if="profile?.statusText"><i> · </i>{{ profile.statusText }}</template>
          <template v-if="statusLabel"><i> · </i>{{ statusLabel }}</template>
        </p>

        <div v-reveal="4" class="hero-actions">
          <button class="btn" type="button" @click="goIntro">我的介绍 ↓</button>
          <a
            v-if="resumeUrl"
            class="btn ghost"
            :href="resumeUrl"
            target="_blank"
            rel="noopener"
          >
            查看简历 ↗
          </a>
        </div>
      </div>
    </div>

    <div class="scroll-cue">SCROLL</div>
  </section>
</template>

<style scoped>
.hero-tag {
  color: var(--ink-faint) !important;
}

.hero-title {
  font-family: var(--serif);
  font-weight: 700;
  font-size: var(--fs-hero);
  line-height: 1.06;
  color: #fff;
  margin: 1.4rem 0;
}

/* 第二行做渐变文字：background-clip: text 把渐变"塞进"字里 */
.hero-title .grad {
  background: linear-gradient(115deg, var(--c1), var(--c2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  transition: background var(--theme-transition);
}

.hero-sub {
  font-size: clamp(1.05rem, 1.6vw, 1.3rem);
  color: var(--ink);
  font-weight: 400;
  margin-bottom: 0.9rem;
}

.hero-status {
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--ink-faint);
  letter-spacing: 0.06em;
  margin-bottom: 2.4rem;
}

.hero-status i {
  color: var(--accent);
  font-style: normal;
  transition: color var(--theme-transition);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* 底部滚动提示：一根会呼吸的竖线 */
.scroll-cue {
  position: absolute;
  bottom: 2.2rem;
  left: 50%;
  transform: translateX(-50%);
  font-family: var(--mono);
  font-size: 0.7rem;
  letter-spacing: 0.34em;
  color: var(--ink-faint);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
}

.scroll-cue::after {
  content: '';
  width: 1px;
  height: 44px;
  background: linear-gradient(var(--accent), transparent);
  animation: cue 2s ease-in-out infinite;
}

@media (max-height: 700px) {
  .scroll-cue {
    display: none;
  }
}
</style>
