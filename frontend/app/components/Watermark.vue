<template>
  <div class="watermark-container">
    <div class="watermark-text">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  text?: string
}

withDefaults(defineProps<Props>(), {
  text: '小X爱股'
})
</script>

<style scoped>
.watermark-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 15;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.watermark-text {
  font-size: 120px;
  font-weight: 900;
  font-family: 'Arial Black', 'Microsoft YaHei', sans-serif;
  letter-spacing: 0.1em;
  transform: rotate(-45deg);
  user-select: none;
  white-space: nowrap;
  /* 默认亮色模式 */
  color: rgba(102, 126, 234, 0.12);
  text-shadow: 2px 2px 8px rgba(102, 126, 234, 0.08);
}

/* 深色模式 */
:global(html.dark) .watermark-text {
  color: rgba(41, 98, 255, 0.15) !important;
  text-shadow: 2px 2px 8px rgba(41, 98, 255, 0.1) !important;
}
</style>

