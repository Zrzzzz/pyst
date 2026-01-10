<template>
  <div class="info-box">
    <div class="info-box-content">
      <span class="info-icon">💡</span>
      <div class="info-text">
        <strong>{{ title }}</strong>
        <p>{{ content }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  content?: string
}

withDefaults(defineProps<Props>(), {
  title: '偏离值',
  content: '偏离值 = 股票涨幅(%) - 指数涨幅(%) | 正值表示股票强于指数，负值表示股票弱于指数'
})
</script>

<style scoped>
.info-box {
  margin-bottom: 1.5rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(41, 98, 255, 0.1) 0%, rgba(61, 90, 254, 0.08) 100%);
  backdrop-filter: blur(12px);
  border-left: 4px solid #2962FF;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(41, 98, 255, 0.15), 0 0 20px rgba(41, 98, 255, 0.08);
  border: 1px solid rgba(41, 98, 255, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

:global(.dark) .info-box {
  background: linear-gradient(135deg, rgba(41, 98, 255, 0.1) 0%, rgba(61, 90, 254, 0.08) 100%);
  border-left: 4px solid #2962FF;
  box-shadow: 0 4px 12px rgba(41, 98, 255, 0.15), 0 0 20px rgba(41, 98, 255, 0.08);
  border: 1px solid rgba(41, 98, 255, 0.2);
}

.info-box::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(41, 98, 255, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(30%, -30%);
}

:global(.dark) .info-box::before {
  background: radial-gradient(circle, rgba(41, 98, 255, 0.2) 0%, transparent 70%);
}

.info-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(41, 98, 255, 0.25), 0 0 30px rgba(41, 98, 255, 0.12);
}

:global(.dark) .info-box:hover {
  box-shadow: 0 6px 20px rgba(41, 98, 255, 0.25), 0 0 30px rgba(41, 98, 255, 0.12);
}

.info-box-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.info-text {
  flex: 1;
  color: #EAECEF;
  font-size: 0.9375rem;
  line-height: 1.6;
  font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
}

:global(.dark) .info-text {
  color: #EAECEF;
}

.info-text strong {
  display: block;
  font-weight: 700;
  margin-bottom: 0.375rem;
  font-size: 1rem;
  color: #2962FF;
  letter-spacing: -0.01em;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.2);
}

:global(.dark) .info-text strong {
  color: #2962FF;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.2);
}

.info-text p {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .info-box {
    padding: 1rem;
  }

  .info-icon {
    font-size: 1.25rem;
  }

  .info-text {
    font-size: 0.875rem;
  }

  .info-text strong {
    font-size: 0.9375rem;
  }

  .info-text p {
    font-size: 0.8125rem;
  }
}
</style>

