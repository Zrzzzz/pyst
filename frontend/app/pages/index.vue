<template>
  <div class="home-page">
    <!-- 水印 -->
    <!-- <Watermark /> -->

    <!-- 页头 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">股票异动监控</h1>
          <p class="page-subtitle">实时监控股票涨幅和偏离值</p>
        </div>
        <div class="header-actions">
          <a-button type="text" @click="showChangelog = true" class="changelog-btn">
            📝 更新日志
          </a-button>
        </div>
      </div>
    </div>

    <!-- 偏离值说明 -->
    <InfoBox
      title="偏离值"
      content="偏离值 = 股票涨幅(%) - 指数涨幅(%) | 正值表示股票强于指数，负值表示股票弱于指数"
    />

    <!-- 10日榜 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">📊 10日偏离值榜 Top 30</h2>
        <a-tag color="blue">{{ stockStore.count10 }}</a-tag>
      </div>

      <StockTable :stocks="stockStore.sortedStocks10" :loading="stockStore.loading" :other-stocks="stockStore.sortedStocks30" />
    </div>

    <!-- 分割线 -->
    <hr class="divider" />

    <!-- 30日榜 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">📈 30日偏离值榜 Top 30</h2>
        <a-tag color="blue">{{ stockStore.count30 }}</a-tag>
      </div>

      <StockTable :stocks="stockStore.sortedStocks30" :loading="stockStore.loading" :other-stocks="stockStore.sortedStocks10" />
    </div>

    <!-- 页脚 -->
    <div class="page-footer">
      <p class="text-gray-600">股票异动监控系统 | © 2024</p>
    </div>

    <!-- 主题切换悬浮按钮 -->
    <ThemeToggle />

    <!-- 更新日志抽屉 -->
    <Changelog v-model:visible="showChangelog" :changelog="stockStore.changelog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStockStore } from '@/stores/stock'
import StockTable from '@/components/StockTable.vue'
import InfoBox from '@/components/InfoBox.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import Watermark from '@/components/Watermark.vue'
import Changelog from '@/components/Changelog.vue'

const stockStore = useStockStore()
const showChangelog = ref(false)

onMounted(() => {
  stockStore.fetchBothStocks()
})
</script>

<style scoped>
/* 主容器 */
.home-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

/* 页头 */
.page-header {
  margin-bottom: 2.5rem;
  animation: slideDown 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: rgba(248, 249, 250, 0.8);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 0 20px rgba(41, 98, 255, 0.08);
  border: 1px solid rgba(41, 98, 255, 0.15);
  transition: all 0.3s ease;
}

/* 亮色模式 */
:global(html:not(.dark)) .header-content {
  background: rgba(248, 249, 250, 0.9);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 0 20px rgba(41, 98, 255, 0.08);
}

/* 深色模式 */
:global(html.dark) .header-content {
  background: rgba(21, 26, 33, 0.7);
  border: 1px solid rgba(41, 98, 255, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(41, 98, 255, 0.1);
}

.header-text {
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 200px;
  justify-content: flex-end;
}

.changelog-btn {
  color: #2962FF;
  font-weight: 600;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.changelog-btn:hover {
  background: rgba(41, 98, 255, 0.1);
  color: #2962FF;
}

:global(.dark) .changelog-btn {
  color: #2962FF;
}

:global(.dark) .changelog-btn:hover {
  background: rgba(41, 98, 255, 0.15);
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: -0.02em;
  text-shadow: 0 0 20px rgba(41, 98, 255, 0.2);
}

:global(.dark) .page-title {
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 20px rgba(41, 98, 255, 0.2);
}

.page-subtitle {
  color: #374151;
  background-clip: text;
  font-size: 1.125rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

/* 亮色模式 */
:global(html:not(.dark)) .page-subtitle {
  color: #374151;
}

/* 深色模式 */
:global(html.dark) .page-subtitle {
  color: #EAECEF;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
  animation: fadeIn 0.8s ease-out 0.2s both;
}

.stats-grid :deep(.arco-statistic) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.18);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:global(.dark) .stats-grid :deep(.arco-statistic) {
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.stats-grid :deep(.arco-statistic):hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

:global(.dark) .stats-grid :deep(.arco-statistic):hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

/* 操作栏 */
.action-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  animation: fadeIn 0.8s ease-out 0.3s both;
}

.action-bar :deep(.arco-btn-primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-bar :deep(.arco-btn-primary):hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* 区块 */
.section {
  margin-bottom: 3rem;
  animation: fadeIn 0.8s ease-out 0.4s both;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-title {
  color: #1F2937;
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  letter-spacing: -0.01em;
}

/* 亮色模式 */
:global(html:not(.dark)) .section-title {
  color: #1F2937;
}

/* 深色模式 */
:global(html.dark) .section-title {
  color: #EAECEF;
}

/* 分隔线 */
.divider {
  margin: 3rem 0;
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(41, 98, 255, 0.2), transparent);
  opacity: 0.8;
}

:global(.dark) .divider {
  background: linear-gradient(90deg, transparent, rgba(41, 98, 255, 0.2), transparent);
}

/* 页脚 */
.page-footer {
  text-align: center;
  margin-top: 4rem;
  padding: 2rem;
  color: #6B7280;
  font-size: 0.875rem;
  animation: fadeIn 1s ease-out 0.6s both;
  font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
}

/* 亮色模式 */
:global(html:not(.dark)) .page-footer {
  color: #6B7280;
}

/* 深色模式 */
:global(html.dark) .page-footer {
  color: #E1E4E8;
}

/* 动画 */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-page {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .section-title {
    font-size: 1.5rem;
  }
}
</style>

