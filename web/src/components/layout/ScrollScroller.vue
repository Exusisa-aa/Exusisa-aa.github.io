<script setup lang="ts">
/**
 * 滚动容器 —— 一屏一停的分镜舞台。
 *
 * 本身只管滚动行为，内容通过 slot 塞进来。
 * 这里不做任何滚动监听：分镜调度由 useScrollStage 用视口 IntersectionObserver 处理，
 * 回到顶部按钮在自己的组件里读 scrollTop。
 */
import { onMounted, ref } from 'vue'

import { useStageStore } from '@/stores/stage'
import { isNoAnim } from '@/utils/debug'

const scrollerEl = ref<HTMLElement | null>(null)
const stage = useStageStore()

/**
 * ?noanim 时关掉吸附和平滑滚动，方便截图和逐屏检查。
 * 平滑滚动也必须关 —— 否则 scrollIntoView 会走动画，
 * 无头截图会抓在滚动中途，画面看着像布局错了。
 */
const scrollerStyle = isNoAnim()
  ? { scrollSnapType: 'none', scrollBehavior: 'auto' as const }
  : { scrollSnapType: 'y proximity' }

onMounted(() => {
  // 供圆点导航和锚点跳转使用
  stage.setScroller(scrollerEl.value)
})
</script>

<template>
  <main ref="scrollerEl" class="scroller" id="scroller" :style="scrollerStyle">
    <slot />
  </main>
</template>
