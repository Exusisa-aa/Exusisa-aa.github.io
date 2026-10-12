<script setup lang="ts">
/**
 * 荣誉资质 —— 点击带证书图的条目打开大图。
 *
 * 没有证书图的条目不能点、也不显示「⊕」提示 ——
 * 避免用户点了没反应以为站点坏了。
 */
import { computed } from 'vue'

import type { StageSection } from '@/api/types'
import { useContentStore } from '@/stores/content'
import { useUiStore } from '@/stores/ui'
import { assetUrl } from '@/utils/asset'

const props = defineProps<{ section: StageSection }>()

const content = useContentStore()
const ui = useUiStore()

const honors = computed(() => content.honors)
const withCert = computed(() => honors.value.some((h) => h.cert?.src))

const LEVEL_LABEL: Record<string, string> = {
  national: '国家级',
  provincial: '省级',
  school: '校级',
  // 华为 / 阿里这类企业发的认证，别写成「国家级」——
  // 那个词在国内语境里指政府级别
  vendor: '厂商认证',
}

/**
 * meta 的键名是自由的，这里挑几个常用的给中文名并固定顺序，
 * 认不出来的键排在后面、直接用原键名。
 */
const META_LABELS: Record<string, string> = {
  certificateNo: '证书编号',
  registrationNo: '登记号',
  school: '获奖院校',
  team: '团队',
  advisor: '指导教师',
  authors: '著作权人',
}

function metaRows(honor: { meta?: Record<string, string> | null }) {
  // 内容是可以手改的，字段缺失/写错不该让整屏渲染不出来 —— 这里一律兜住
  const meta = honor.meta ?? {}
  const known = Object.keys(META_LABELS).filter((k) => meta[k])
  const rest = Object.keys(meta).filter((k) => !META_LABELS[k] && meta[k])
  return [...known, ...rest].map((key) => ({
    key,
    label: META_LABELS[key] ?? key,
    value: meta[key],
  }))
}

function openHonorCert(honorId: string): void {
  const honor = honors.value.find((h) => h.id === honorId)
  if (!honor?.cert?.src) return
  ui.openImage(assetUrl(honor.cert.src), honor.cert.alt || honor.title)
}
</script>

<template>
  <section :id="props.section.id" class="scene">
    <div class="scene-inner">
      <div class="scene-text">
        <p v-reveal class="scene-num">06</p>
        <h2 v-reveal="1" class="scene-title-sm">荣誉资质</h2>
        <p v-reveal="2" class="scene-desc honors-desc">
          比赛、软著与认证 —— 每一条都可以对应到简历里的原始材料。
        </p>
      </div>

      <div v-reveal="3">
        <div class="card cred-box">
          <p class="cred-title">资质 CREDENTIALS</p>
          <p v-if="withCert" class="cred-hint">点击查看证书大图</p>
          <p v-else class="cred-hint">证书原图待补充</p>

          <div
            v-for="honor in honors"
            :key="honor.id"
            class="cred-item"
            :class="{ clickable: !!honor.cert?.src }"
            :role="honor.cert?.src ? 'button' : undefined"
            :tabindex="honor.cert?.src ? 0 : undefined"
            @click="openHonorCert(honor.id)"
            @keydown.enter="openHonorCert(honor.id)"
            @keydown.space.prevent="openHonorCert(honor.id)"
          >
            <div class="cred-name">{{ honor.title }}</div>
            <div class="cred-issuer">
              <span class="cred-level">{{ LEVEL_LABEL[honor.level] ?? honor.level }}</span>
              {{ honor.issuer }}
              <template v-if="honor.date"> · {{ honor.date }}</template>
            </div>

            <!-- 证书上的佐证信息，从证书原文抄下来的 -->
            <dl v-if="metaRows(honor).length" class="cred-meta">
              <div v-for="row in metaRows(honor)" :key="row.key" class="cred-meta-row">
                <dt>{{ row.label }}</dt>
                <dd>{{ row.value }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.honors-desc {
  max-width: 420px;
}

.cred-box {
  padding: 2rem;
}

.cred-title {
  font-family: var(--mono);
  font-size: 0.74rem;
  color: var(--accent);
  letter-spacing: 0.16em;
  margin-bottom: 0.6rem;
  transition: color var(--theme-transition);
}

.cred-hint {
  font-family: var(--mono);
  font-size: 0.66rem;
  color: var(--ink-faint);
  letter-spacing: 0.08em;
  margin-bottom: 1.2rem;
}

.cred-item {
  padding: 1rem 0.8rem;
  border-top: 1px solid var(--line);
  border-radius: 8px;
  transition: background 0.3s;
}

.cred-item:first-of-type {
  border-top: none;
  padding-top: 0;
}

.cred-item.clickable {
  cursor: pointer;
}

.cred-item.clickable:hover,
.cred-item.clickable:focus-visible {
  background: rgba(255, 255, 255, 0.05);
}

.cred-name {
  font-size: 1rem;
  color: #fff;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 可点击的条目右侧给个 ⊕ 提示 */
.cred-item.clickable .cred-name::after {
  content: '⊕';
  color: var(--accent);
  font-size: 0.9rem;
  transition: color var(--theme-transition);
}

.cred-issuer {
  font-family: var(--mono);
  font-size: 0.74rem;
  color: var(--ink-faint);
  margin-top: 0.35rem;
}

.cred-level {
  color: var(--ink-dim);
  margin-right: 0.6rem;
}

/* 证书上的佐证信息：左标签右内容的两列小字 */
.cred-meta {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-top: 0.7rem;
  padding-left: 0.1rem;
}

.cred-meta-row {
  display: grid;
  grid-template-columns: 4.6rem 1fr;
  gap: 0.6rem;
  align-items: baseline;
}

.cred-meta-row dt {
  font-family: var(--mono);
  font-size: 0.66rem;
  color: var(--ink-faint);
  letter-spacing: 0.06em;
}

.cred-meta-row dd {
  font-size: 0.78rem;
  color: var(--ink-dim);
  line-height: 1.6;
}
</style>
