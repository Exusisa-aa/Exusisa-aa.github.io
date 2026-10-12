<script setup lang="ts">
/**
 * 噪点层。
 *
 * 大面积高斯模糊 + 渐变在暗底上很容易出现色带（banding），
 * 盖一层 5% 不透明度的噪点就能把它打散，同时给画面加一点胶片质感。
 *
 * 噪点用内联 SVG 的 feTurbulence 生成，不需要额外图片文件。
 */
</script>

<template>
  <div class="grain" aria-hidden="true" />
</template>

<style scoped>
.grain {
  position: fixed;
  inset: 0;
  z-index: var(--z-noise);
  pointer-events: none;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='0.6'/%3E%3C/svg%3E");
}
</style>
