/**
 * 分镜调度 —— 监听滚动，判断当前在第几屏，并把该屏的主题色写到 :root。
 *
 * 为什么会用 root: null（视口）而不是滚动容器：
 *   .scroller 本身就是一屏高，元素在它内部滚动时相对视口的位置同样在变，
 *   所以视口观察器能正确工作，而且省掉了"容器 ref 还没绑定就要建观察器"的时序问题。
 */

import { nextTick, onBeforeUnmount, ref } from 'vue'

import { useStageStore } from '@/stores/stage'

export function useScrollStage() {
  const stage = useStageStore()
  const activeId = ref<string | null>(null)

  let observer: IntersectionObserver | null = null

  function disconnect(): void {
    observer?.disconnect()
    observer = null
  }

  /**
   * 在所有分镜渲染完成后调用。
   * 会用 data-scene-index 属性把 DOM 元素和分镜数组对应起来。
   */
  async function observeScenes(): Promise<void> {
    disconnect()
    await nextTick()

    const scenes = Array.from(
      document.querySelectorAll<HTMLElement>('[data-scene-index]'),
    ).sort(
      (a, b) => Number(a.dataset.sceneIndex) - Number(b.dataset.sceneIndex),
    )

    if (scenes.length === 0) return

    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          const index = Number((entry.target as HTMLElement).dataset.sceneIndex)
          if (Number.isNaN(index)) continue
          stage.setActive(index)
          activeId.value = stage.sections[index]?.id ?? null
        }
      },
      { threshold: 0.5 },
    )

    scenes.forEach((el) => observer?.observe(el))

    // 首屏主题色立刻生效，不要等到第一次滚动才变色
    stage.setActive(0)
  }

  onBeforeUnmount(disconnect)

  return { activeId, observeScenes, disconnect }
}
