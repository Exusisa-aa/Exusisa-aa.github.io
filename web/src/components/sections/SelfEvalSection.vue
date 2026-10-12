<script setup lang="ts">
/**
 * 自我评价 —— 把 content/self-evaluation.md 原样渲染出来。
 *
 * 用 markdown-it 而不是手写排版：这段文字是从简历里搬过来的，
 * 保留 Markdown 意味着以后想加粗、分段、加引用都不用改代码。
 */
import MarkdownIt from 'markdown-it'
import { computed } from 'vue'

import type { StageSection } from '@/api/types'
import { useContentStore } from '@/stores/content'

const props = defineProps<{ section: StageSection }>()

const content = useContentStore()

// html: false —— 内容来自本地文件，但仍然不开 HTML 透传，少一个注入口
const md = new MarkdownIt({ html: false, breaks: true, linkify: false })

const rendered = computed(() => {
  const source = content.selfEvaluation
  return source ? md.render(source) : ''
})
</script>

<template>
  <section :id="props.section.id" class="scene center">
    <div class="scene-inner">
      <div>
        <p v-reveal class="scene-tag selfeval-tag">// 自我评价</p>
        <h2 v-reveal="1" class="scene-title-sm selfeval-title">为什么做这行</h2>

        <div v-reveal="2" class="selfeval-body" v-html="rendered" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.selfeval-tag {
  color: var(--ink-faint) !important;
}

.selfeval-title {
  margin-bottom: 2rem;
}

.selfeval-body {
  max-width: 780px;
  margin: 0 auto;
  text-align: left;
  color: var(--ink-dim);
  font-size: 1.02rem;
  line-height: 2;
}

/* v-html 注入的内容不受 scoped 的 data 属性约束，
   所以这里用 :deep() 穿透进去改 Markdown 生成的标签 */
.selfeval-body :deep(p) {
  margin-bottom: 1.4rem;
}

.selfeval-body :deep(p:last-child) {
  margin-bottom: 0;
}

.selfeval-body :deep(strong) {
  color: var(--ink);
  font-weight: 500;
}

/* 引用块做成左侧竖线的强调样式 */
.selfeval-body :deep(blockquote) {
  margin: 1.6rem 0;
  padding-left: 1.2rem;
  border-left: 2px solid var(--accent);
  color: var(--ink);
  font-family: var(--serif);
  transition: border-color var(--theme-transition);
}

.selfeval-body :deep(code) {
  font-family: var(--mono);
  font-size: 0.86em;
  background: rgba(255, 255, 255, 0.06);
  padding: 0.15em 0.4em;
  border-radius: 5px;
}
</style>
