/**
 * 内容仓库 —— 全站数据的唯一来源。
 *
 * 组件永远从这里读数据，不关心后端在不在。
 * live / static 的差异在 api 层就被抹平了。
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { probeApiMode } from '@/api/health'
import { fetchBundle } from '@/api/sources'
import type { ApiMode, Bundle } from '@/api/types'

export const useContentStore = defineStore('content', () => {
  const bundle = ref<Bundle | null>(null)
  const mode = ref<ApiMode>('static')
  const loading = ref(true)
  const error = ref<string | null>(null)

  // ---------------------------------------------------------------- 派生数据

  const profile = computed(() => bundle.value?.profile ?? null)
  const skills = computed(() => bundle.value?.skills.groups ?? [])
  const honors = computed(() => bundle.value?.honors.honors ?? [])
  const courses = computed(() => bundle.value?.courses.courses ?? [])
  const selfEvaluation = computed(() => bundle.value?.selfEvaluation ?? '')
  const site = computed(() => bundle.value?.site ?? null)
  const sections = computed(() => bundle.value?.stage.sections ?? [])
  const carouselConfig = computed(() => bundle.value?.stage.carousel ?? null)
  const videoConfig = computed(() => bundle.value?.stage.video ?? null)
  const projects = computed(() => bundle.value?.projects ?? [])

  /** 有独立分镜的主作品 */
  const featuredProjects = computed(() => projects.value.filter((p) => p.featured))

  /** 放进「更多作品」轮播的项目 */
  const carouselProjects = computed(() => projects.value.filter((p) => !p.featured))

  function projectById(id: string) {
    return projects.value.find((p) => p.id === id) ?? null
  }

  // ---------------------------------------------------------------- 加载

  async function load(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const detected = await probeApiMode()
      const result = await fetchBundle(detected)
      bundle.value = result.bundle
      mode.value = result.mode
      console.info(
        `[portfolio] apiMode = ${result.mode}` +
          ` · ${result.bundle.projects.length} 个项目` +
          ` · 内容哈希 ${result.bundle.contentHash}`,
      )
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
      console.error('[portfolio] 内容加载失败', err)
    } finally {
      loading.value = false
    }
  }

  return {
    bundle,
    mode,
    loading,
    error,
    profile,
    skills,
    honors,
    courses,
    selfEvaluation,
    site,
    sections,
    carouselConfig,
    videoConfig,
    projects,
    featuredProjects,
    carouselProjects,
    projectById,
    load,
  }
})
