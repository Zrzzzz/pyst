<template>
  <a-drawer
    v-model:visible="visible"
    title="📝 更新日志"
    placement="right"
    width="400px"
    :closable="true"
  >
    <div class="changelog-content">
      <div v-for="log in changelog" :key="log.version" class="changelog-item">
        <div class="changelog-header">
          <span class="version-badge">v{{ log.version }}</span>
          <span class="date-badge">{{ log.date }}</span>
        </div>
        <ul class="changelog-list">
          <li v-for="(change, idx) in log.changes" :key="idx" class="changelog-change">
            {{ change }}
          </li>
        </ul>
      </div>
    </div>
  </a-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ChangelogItem {
  version: string
  date: string
  changes: string[]
}

interface Props {
  visible?: boolean
  changelog?: ChangelogItem[]
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  changelog: () => []
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})
</script>

<style scoped>
/* 使用 Arco Design 官方颜色 */

.changelog-content {
  padding: 1rem 0;
}

.changelog-item {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border-2);
}

.changelog-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.changelog-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.version-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, var(--color-primary-3) 0%, var(--color-primary-4) 100%);
  border: 1px solid var(--color-primary-5);
  border-radius: 6px;
  color: var(--color-primary-6);
  font-weight: 700;
  font-size: 0.875rem;
}

.date-badge {
  color: var(--color-text-3);
  font-size: 0.8125rem;
  font-weight: 500;
}

.changelog-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.changelog-change {
  padding: 0.5rem 0;
  color: var(--color-text-2);
  font-size: 0.875rem;
  line-height: 1.5;
}

.changelog-change::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 4px;
  background: var(--color-primary-6);
  border-radius: 50%;
  margin-right: 0.5rem;
  vertical-align: middle;
}
</style>

