<template>
  <div class="watermark-container">
    <svg class="watermark-svg" :width="width" :height="height">
      <defs>
        <pattern :id="patternId" :x="spacing" :y="spacing" :width="spacing" :height="spacing" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
          <text
            x="0"
            y="0"
            :font-size="fontSize"
            :fill="color"
            :opacity="opacity"
            font-family="Arial, sans-serif"
            font-weight="500"
            text-anchor="start"
          >
            {{ text }}
          </text>
        </pattern>
      </defs>
      <rect :width="width" :height="height" :fill="`url(#${patternId})`" />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  fontSize?: number
  spacing?: number
  opacity?: number
  color?: string
  width?: number
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  text: '股票异动监控系统',
  fontSize: 16,
  spacing: 200,
  opacity: 0.08,
  color: '#2962FF',
  width: 1920,
  height: 1080
})

const patternId = computed(() => `watermark-pattern-${Math.random().toString(36).substr(2, 9)}`)
</script>

<style scoped>
.watermark-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.watermark-svg {
  width: 100%;
  height: 100%;
}
</style>

