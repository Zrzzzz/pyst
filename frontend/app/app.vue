<template>
  <a-config-provider :theme="themeConfig">
    <div class="app-container">
      <NuxtRouteAnnouncer />
      <NuxtPage />
    </div>
  </a-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from '@/composables/useTheme'

// 初始化主题
const { isDark, initTheme } = useTheme()
initTheme()

// Ant Design 主题配置
const themeConfig = computed(() => ({
  token: {
    colorBgBase: isDark.value ? '#1a1a2e' : '#ffffff',
    colorTextBase: isDark.value ? '#e1e4e8' : '#000000',
  },
  algorithm: isDark.value ? undefined : undefined, // 使用默认算法
}))
</script>

<style lang="scss">
@use './styles/main.scss' as *;

html.dark {
  color-scheme: dark;
}

/* 禁用某些元素的过渡 */
*:focus,
*:active,
input,
textarea,
select {
  transition: none;
}

/* 全局过渡动画 */
* {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-duration: 0.2s;
  transition-timing-function: ease-in-out;
}
</style>
