/** 全局 UI 状态：图片灯箱、回到顶部按钮 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  // ---- 图片灯箱 ----
  // 证书大图、项目截图都用它。名字保持通用，别按某一种用途命名。
  const imageSrc = ref<string | null>(null)
  const imageAlt = ref('')

  function openImage(src: string, alt = '图片'): void {
    imageSrc.value = src
    imageAlt.value = alt
  }

  function closeImage(): void {
    imageSrc.value = null
    imageAlt.value = ''
  }

  // ---- 回到顶部 ----
  const showBackTop = ref(false)

  function setShowBackTop(value: boolean): void {
    showBackTop.value = value
  }

  return {
    imageSrc,
    imageAlt,
    openImage,
    closeImage,
    showBackTop,
    setShowBackTop,
  }
})
