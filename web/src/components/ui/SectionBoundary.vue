<script setup lang="ts">
/**
 * 分镜错误边界。
 *
 * 为什么需要：Vue 在渲染出错时会中断整棵子树。之前荣誉屏因为一个字段
 * 是 null 就抛错，结果它和后面两屏（自述、联系）一起凭空消失了 ——
 * 页面上没有任何提示，看起来就像"网站少了半截"。
 *
 * 内容都在 content/*.yaml 里，是会被人手改的。一个字段写错不该让整页塌掉，
 * 所以每一屏都包一层：坏掉的那一屏单独显示错误，其余照常渲染。
 */
import { onErrorCaptured, ref } from 'vue'

const props = defineProps<{
  /** 原始分镜 id 和序号 —— 兜底屏也要保留，否则圆点导航和锚点会跳空 */
  sectionId: string
  sceneIndex: number
}>()

const failed = ref(false)
const message = ref('')

onErrorCaptured((err) => {
  failed.value = true
  message.value = err instanceof Error ? err.message : String(err)
  console.error('[portfolio] 这一屏渲染失败：', err)
  // 返回 false 阻止错误继续向上冒泡（否则会打到 App 上，整页还是没了）
  return false
})
</script>

<template>
  <slot v-if="!failed" />

  <section
    v-else
    :id="props.sectionId"
    class="scene"
    :data-scene-index="props.sceneIndex"
  >
    <div class="scene-inner">
      <div class="boundary-error">
        <p class="mono">这一屏渲染失败</p>
        <p class="detail">{{ message }}</p>
        <p class="hint">
          多半是 <code>content/</code> 里某个字段写错了。检查对应分镜引用的 YAML，
          修好后刷新即可。其余分镜不受影响。
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.boundary-error {
  max-width: 640px;
  margin: 0 auto;
  text-align: center;
}

.boundary-error .mono {
  font-family: var(--mono);
  font-size: 0.8rem;
  letter-spacing: 0.2em;
  color: #fca5a5;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.boundary-error .detail {
  font-family: var(--mono);
  font-size: 0.82rem;
  color: var(--ink);
  line-height: 1.7;
  word-break: break-word;
}

.boundary-error .hint {
  margin-top: 1.2rem;
  color: var(--ink-faint);
  font-size: 0.86rem;
  line-height: 1.8;
}

.boundary-error code {
  font-family: var(--mono);
  font-size: 0.85em;
  background: rgba(255, 255, 255, 0.06);
  padding: 0.15em 0.4em;
  border-radius: 5px;
}
</style>
