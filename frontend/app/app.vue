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

// Arco Design 主题配置
const themeConfig = computed(() => ({
  token: {
    // 亮色模式
    colorBgBase: isDark.value ? '#0B0E11' : '#FFFFFF',
    colorTextBase: isDark.value ? '#EAECEF' : '#1F2937',
    colorPrimary: '#2962FF',
    colorSuccess: isDark.value ? '#2EBD85' : '#059669',
    colorWarning: isDark.value ? '#F6A500' : '#F59E0B',
    colorError: isDark.value ? '#F6465D' : '#DC2626',
    colorInfo: '#2962FF',
    colorBorder: isDark.value ? 'rgba(41, 98, 255, 0.15)' : 'rgba(41, 98, 255, 0.2)',
    colorBgContainer: isDark.value ? '#151A21' : '#F8F9FA',
    colorBgElevated: isDark.value ? '#1F2937' : '#FFFFFF',
    colorBgLayout: isDark.value ? '#0B0E11' : '#FFFFFF',
  },
}))
</script>

<style lang="scss">
@use './styles/main.scss' as *;

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

/* 确保应用容器在水印上方 */
.app-container {
  position: relative;
  z-index: 20;
}
</style>
