<template>
  <button
    @click="toggleTheme"
    class="theme-toggle"
    :class="{ 'dark': isDark }"
    :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
  >
    <transition name="icon-fade" mode="out-in">
      <svg v-if="isDark" key="moon" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
      <svg v-else key="sun" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    </transition>
  </button>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { isDark, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 1px solid rgba(41, 98, 255, 0.3);
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(41, 98, 255, 0.4), 0 0 20px rgba(41, 98, 255, 0.2);
  overflow: hidden;
  z-index: 1000;
}

.theme-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(41, 98, 255, 0.6), 0 0 30px rgba(41, 98, 255, 0.3);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.theme-toggle.dark {
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  border: 1px solid rgba(41, 98, 255, 0.3);
  box-shadow: 0 4px 16px rgba(41, 98, 255, 0.4), 0 0 20px rgba(41, 98, 255, 0.2);
}

.theme-toggle.dark:hover {
  box-shadow: 0 8px 24px rgba(41, 98, 255, 0.6), 0 0 30px rgba(41, 98, 255, 0.3);
}

.icon {
  width: 28px;
  height: 28px;
  stroke-width: 2;
}

/* 图标切换动画 */
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.icon-fade-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}

.icon-fade-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-toggle {
    bottom: 1.5rem;
    right: 1.5rem;
    width: 52px;
    height: 52px;
  }

  .icon {
    width: 26px;
    height: 26px;
  }
}
</style>

