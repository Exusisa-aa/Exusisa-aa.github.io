<script setup lang="ts">
/**
 * 主作品分镜 —— 左边文案，右边演示框。
 *
 * 右边根据项目数据自动选：有视频走 VideoStage，只有图就走静态图框。
 * 两者共用同一套框体样式（圆角、高光边、投影），观感统一。
 */
import { computed } from 'vue'

import type { Project, StageSection } from '@/api/types'
import { useContentStore } from '@/stores/content'
import { assetUrl } from '@/utils/asset'
import GalleryCarousel from '@/components/ui/GalleryCarousel.vue'
import VideoStage from '@/components/ui/VideoStage.vue'

const props = defineProps<{
  section: StageSection
  project: Project | null
}>()

const content = useContentStore()

const video = computed(() => props.project?.videos[0] ?? null)
const gallery = computed(() => props.project?.gallery ?? [])
const videoConfig = computed(() => content.videoConfig)

/** 只有一张图时不值得做成轮播（箭头和圆点都是摆设），退化成静图 */
const showCarousel = computed(() => gallery.value.length > 1)
const staticImage = computed(
  () => props.project?.images[0] ?? props.project?.gallery[0] ?? null,
)

/** 分镜序号 —— 从 stage.sections 里数，保证和圆点导航一致 */
const sceneNum = computed(() => {
  const i = content.sections.findIndex((s) => s.id === props.section.id)
  return String(Math.max(i, 0)).padStart(2, '0')
})

/**
 * 技术栈那行。
 * 有 tags 药丸时就不再重复渲染 —— 两者内容高度重叠（都是语言和框架名），
 * 同时出现会读起来像写了两遍。
 */
const stackLine = computed(() => {
  if (!props.project || props.project.tags.length) return ''
  const s = props.project.stack
  return [...s.language, ...s.framework, ...s.middleware, ...s.infra].join(' · ')
})

/**
 * 有 url 的链接才渲染成按钮。
 * 允许出现「只有 note、没有 url」的条目 —— 用于「这个项目不开放跳转，
 * 但需要说明一句」的场景（比如镜像不公开）。
 */
const primaryLink = computed(() => props.project?.links.find((l) => l.url) ?? null)
const linkNote = computed(() => props.project?.links.find((l) => l.note)?.note ?? '')

/** 整条 links 都是空的才提示"待补充"；有意留空的不算 */
const showLinkPlaceholder = computed(
  () => !primaryLink.value && !linkNote.value && (props.project?.links.length ?? 0) === 0,
)
</script>

<template>
  <section :id="props.section.id" class="scene">
    <div class="scene-inner">
      <div class="scene-text">
        <p v-reveal class="scene-num">{{ sceneNum }}</p>
        <h2 v-reveal="1" class="scene-title">{{ props.project?.title }}</h2>
        <p v-if="props.project?.subtitle" v-reveal="2" class="scene-tag">
          {{ props.project.subtitle }}
        </p>
        <p v-reveal="3" class="scene-desc">{{ props.project?.summary }}</p>

        <ul v-if="props.project?.tags.length" v-reveal="4" class="project-tag-row">
          <li v-for="tag in props.project.tags" :key="tag" class="tag-pill">{{ tag }}</li>
        </ul>

        <p v-if="stackLine" v-reveal="4" class="scene-stack">{{ stackLine }}</p>

        <div v-reveal="5" class="scene-btns project-links">
          <a
            v-if="primaryLink?.url"
            class="btn"
            :href="primaryLink.url"
            target="_blank"
            rel="noopener"
          >
            {{ primaryLink.label }} ↗
          </a>
          <!-- 整个项目都还没配链接时给个提示，而不是渲染一个点不动的空按钮 -->
          <span v-else-if="showLinkPlaceholder" class="scene-btn-placeholder">
            链接待补充
          </span>

          <!-- 补充说明。有些项目只开源了部分内容、或者干脆不开放跳转，
               不写一句容易让人以为仓库是空的。 -->
          <p v-if="linkNote" class="link-note">{{ linkNote }}</p>
        </div>
      </div>

      <div v-reveal="2" class="scene-visual">
        <!-- 优先级：多图轮播 > 视频演示 > 单张静图 > 占位 -->
        <GalleryCarousel
          v-if="showCarousel"
          :items="gallery"
          :aspect="props.project?.galleryAspect"
        />

        <VideoStage
          v-else-if="video"
          :video="video"
          :seek-on-hover="videoConfig?.seekOnHover ?? true"
        />

        <div v-else-if="staticImage" class="demo-frame static-frame">
          <img :src="assetUrl(staticImage.src)" :alt="staticImage.alt" loading="lazy" />
          <span v-if="staticImage.caption" class="demo-badge">
            {{ staticImage.caption }}
          </span>
        </div>

        <!-- 既没视频也没图：用项目主题色做占位块，等补素材 -->
        <div v-else class="demo-frame static-frame empty-frame">
          <p class="empty-text">效果图待补充</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.project-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.48rem;
  margin-bottom: 1.1rem;
  max-width: 470px;
}

/* 按钮和它旁边的小字说明排成一行 */
.project-links {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  flex-wrap: wrap;
}

.link-note {
  font-size: 0.78rem;
  line-height: 1.6;
  /* 用 ink-dim 而不是 ink-faint —— 极光背景本来就偏亮，
     faint 那一档在上面几乎读不出来，而这句话是必须让人看到的 */
  color: var(--ink-dim);
  /* 左侧一道细竖线，把说明和按钮在视觉上绑定起来 */
  border-left: 1px solid rgba(255, 255, 255, 0.18);
  padding-left: 0.9rem;
  max-width: 320px;
}

/* 没有按钮时（项目不开放跳转），说明自己就是整行内容，
   那道竖线就没有"分隔"的对象了，去掉 */
.link-note:only-child {
  border-left: none;
  padding-left: 0;
}

/* 窄屏挤不下就换行，竖线去掉 */
@media (max-width: 1100px) {
  .link-note {
    border-left: none;
    padding-left: 0;
    max-width: none;
    flex-basis: 100%;
  }
}

.scene-btn-placeholder {
  font-family: var(--mono);
  font-size: 0.76rem;
  color: var(--ink-faint);
  letter-spacing: 0.06em;
  padding: 0.9rem 0;
}

/* 静态图框沿用视频框的观感，只是没有进度条和播放键 */
.static-frame {
  display: flex;
  align-items: center;
  justify-content: center;
}

.static-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.empty-frame {
  background: linear-gradient(
    140deg,
    color-mix(in srgb, var(--c1) 22%, transparent),
    color-mix(in srgb, var(--c2) 12%, transparent) 60%,
    #090b13
  );
}

.empty-text {
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  color: rgba(241, 241, 246, 0.4);
}
</style>
