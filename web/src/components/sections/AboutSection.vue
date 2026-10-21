<script setup lang="ts">
/** 关于我 —— 自我介绍 + 教育背景 + 主修课程 + 数字徽章 */
import { computed } from 'vue'

import type { Badge, StageSection } from '@/api/types'
import { useContentStore } from '@/stores/content'
import { useStageStore } from '@/stores/stage'
import { useUiStore } from '@/stores/ui'
import { assetUrl } from '@/utils/asset'

const props = defineProps<{ section: StageSection }>()

const content = useContentStore()
const stage = useStageStore()
const ui = useUiStore()

const profile = computed(() => content.profile)
const courses = computed(() => content.courses)
const badges = computed(() => profile.value?.badges ?? [])

/** 配了证书图的徽章可以点开看大图（复用荣誉屏那套 lightbox） */
function openBadgeCert(badge: Badge): void {
  if (!badge.cert) return
  ui.openImage(assetUrl(badge.cert), badge.label)
}

/**
 * 有证书图的徽章，在下面单独列一栏直接显示出来。
 * 只有数字徽章的话太隐蔽了 —— 没人会想到那个小 ⊕ 能点。
 */
const certBadges = computed(() => badges.value.filter((b) => b.cert))
</script>

<template>
  <section :id="props.section.id" class="scene">
    <div class="scene-inner">
      <div class="scene-text">
        <p v-reveal class="scene-num">{{ stage.numberOf(props.section.id) }}</p>
        <h2 v-reveal="1" class="scene-title-sm">关于我</h2>

        <p v-reveal="2" class="scene-desc about-desc">
          {{ profile?.tagline }}
        </p>

        <div v-if="badges.length" v-reveal="3" class="about-stats">
          <div
            v-for="badge in badges"
            :key="badge.label"
            class="about-stat"
            :class="{ clickable: !!badge.cert }"
            :role="badge.cert ? 'button' : undefined"
            :tabindex="badge.cert ? 0 : undefined"
            :aria-label="badge.cert ? `${badge.label}，点击查看证书` : undefined"
            @click="openBadgeCert(badge)"
            @keydown.enter="openBadgeCert(badge)"
            @keydown.space.prevent="openBadgeCert(badge)"
          >
            <div class="n">{{ badge.value }}<em>+</em></div>
            <div class="l">
              {{ badge.label }}
              <span v-if="badge.cert" class="cert-mark" aria-hidden="true">⊕</span>
            </div>
          </div>
        </div>
      </div>

      <div v-reveal="3" class="about-side">
        <!-- 教育背景 -->
        <div v-if="profile?.education.length" class="card edu-box">
          <p class="box-title">教育背景 EDUCATION</p>
          <div v-for="edu in profile.education" :key="edu.school" class="edu-item">
            <div class="edu-school">{{ edu.school }}</div>
            <div class="edu-meta">
              {{ edu.major }}
              <template v-if="edu.degree"> · {{ edu.degree }}</template>
              <template v-if="edu.grade"> · {{ edu.grade }}</template>
            </div>
            <div v-if="edu.start" class="edu-period">{{ edu.start }} — {{ edu.end }}</div>
          </div>
        </div>

        <!-- 主修课程 -->
        <div v-if="courses.length" class="card course-box">
          <p class="box-title">主修课程 COURSES</p>
          <ul class="course-list">
            <li v-for="course in courses" :key="course">{{ course }}</li>
          </ul>
        </div>

        <!-- 证书 —— 直接把图显示出来，点击看大图 -->
        <div v-if="certBadges.length" class="card cert-box">
          <p class="box-title">证书 CERTIFICATES</p>
          <div class="cert-grid">
            <button
              v-for="badge in certBadges"
              :key="badge.label"
              class="cert-thumb"
              type="button"
              :aria-label="`查看${badge.label}证书大图`"
              @click="openBadgeCert(badge)"
            >
              <img
                :src="assetUrl(badge.cert)"
                :alt="`${badge.label} 证书`"
                loading="lazy"
              />
              <span class="cert-thumb-label">{{ badge.label }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.about-desc {
  max-width: 520px;
  margin-top: 1.4rem;
}

.about-side {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.edu-box,
.course-box {
  padding: 2rem;
}

.box-title {
  font-family: var(--mono);
  font-size: 0.74rem;
  color: var(--accent);
  letter-spacing: 0.16em;
  margin-bottom: 1.2rem;
  transition: color var(--theme-transition);
}

.edu-school {
  font-size: 1.15rem;
  color: #fff;
  font-weight: 500;
}

.edu-meta {
  font-size: 0.9rem;
  color: var(--ink-dim);
  margin-top: 0.35rem;
}

.edu-period {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--ink-faint);
  margin-top: 0.5rem;
  letter-spacing: 0.06em;
}

.course-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.course-list li {
  padding: 0.4rem 0.72rem;
  border: 1px solid var(--line);
  border-radius: var(--r-pill);
  font-size: 0.78rem;
  color: var(--ink-dim);
  background: rgba(255, 255, 255, 0.02);
}

/* ---- 证书缩略图 ---- */
.cert-box {
  padding: 1.25rem 1.4rem;
}

.cert-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.8rem;
}

.cert-thumb {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0;
  text-align: left;
  cursor: pointer;
}

.cert-thumb img {
  width: 100%;
  /* 固定高度 + contain：两张证书比例不同（省一横版、软著竖版），
     锁高度才能让它们并排对齐，又不会被裁掉看不清内容 */
  height: 150px;
  object-fit: contain;
  padding: 5px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--line);
  border-radius: 10px;
  transition:
    transform 0.4s var(--ease),
    border-color 0.4s,
    background 0.4s;
}

.cert-thumb:hover img,
.cert-thumb:focus-visible img {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.08);
}

.cert-thumb-label {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--ink-faint);
  letter-spacing: 0.04em;
  transition: color 0.3s;
  /* 标签最多两行，超了省略 —— 避免撑高卡片 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cert-thumb:hover .cert-thumb-label {
  color: var(--ink);
}

/* 数字徽章 */
.about-stats {
  display: flex;
  gap: 2.6rem;
  margin: 1.8rem 0 2rem;
  flex-wrap: wrap;
}

.about-stat .n {
  font-family: var(--serif);
  font-weight: 700;
  font-size: 2.6rem;
  line-height: 1;
  color: #fff;
}

.about-stat .n em {
  color: var(--accent);
  font-style: normal;
  transition: color var(--theme-transition);
}

.about-stat .l {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--ink-faint);
  margin-top: 0.5rem;
  letter-spacing: 0.06em;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  transition: color 0.3s;
}

/* 有证书图的徽章：可点，hover 时整体提亮 */
.about-stat.clickable {
  cursor: pointer;
}

.about-stat.clickable:hover .l,
.about-stat.clickable:focus-visible .l {
  color: var(--ink);
}

.about-stat.clickable:hover .n em {
  filter: brightness(1.35);
}

.cert-mark {
  color: var(--accent);
  font-size: 0.9rem;
  transition: color var(--theme-transition);
}

@media (max-width: 900px) {
  .about-stats {
    justify-content: center;
  }

  .about-desc {
    margin-left: auto;
    margin-right: auto;
  }
}
</style>
