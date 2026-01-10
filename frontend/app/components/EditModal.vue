<template>
  <a-modal
    v-model:visible="visible"
    title="修改涨幅"
    @ok="handleSave"
    @cancel="handleCancel"
    width="400px"
  >
    <a-form :model="formData" layout="vertical">
      <a-form-item label="修改涨幅 (%)" required>
        <a-input-number
          v-model="formData.value"
          :step="0.01"
          :min="minValue"
          :max="maxValue"
          placeholder="输入涨幅百分比"
        />
      </a-form-item>
      <a-form-item>
        <div class="form-hint">
          范围: {{ formatNumber(minValue) }}% ~ {{ formatNumber(maxValue) }}%
        </div>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  visible?: boolean
  title?: string
  limitUpPct?: number
  currentValue?: number
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  title: '修改涨幅',
  limitUpPct: 10,
  currentValue: 10
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  save: [value: number]
}>()

const formData = ref({
  value: props.currentValue
})

const minValue = computed(() => -props.limitUpPct)
const maxValue = computed(() => props.limitUpPct)

const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

watch(
  () => props.currentValue,
  (newVal) => {
    formData.value.value = newVal
  }
)

const formatNumber = (num: number): string => {
  return parseFloat(num.toFixed(2)).toString()
}

const handleSave = () => {
  const value = formData.value.value
  if (value === undefined || value === null) {
    return
  }
  if (value < minValue.value || value > maxValue.value) {
    return
  }
  emit('save', value)
  visible.value = false
}

const handleCancel = () => {
  visible.value = false
}
</script>

<style scoped>
.form-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

/* 亮色模式 */
:global(html:not(.dark)) .form-hint {
  color: #6B7280;
}

/* 深色模式 */
:global(html.dark) .form-hint {
  color: #94a3b8;
}

/* 优化模态框样式 */
:deep(.arco-modal) {
  border-radius: 16px;
  overflow: hidden;
  background: rgba(248, 249, 250, 0.95) !important;
  border: 1px solid rgba(41, 98, 255, 0.15);
}

/* 亮色模式 */
:global(html:not(.dark)) :deep(.arco-modal) {
  background: rgba(248, 249, 250, 0.95) !important;
  border: 1px solid rgba(41, 98, 255, 0.15);
}

/* 深色模式 */
:global(html.dark) :deep(.arco-modal) {
  background: rgba(21, 26, 33, 0.95) !important;
  border: 1px solid rgba(41, 98, 255, 0.15);
}

:deep(.arco-modal-header) {
  background: linear-gradient(135deg, rgba(41, 98, 255, 0.1) 0%, rgba(61, 90, 254, 0.05) 100%);
  color: #2962FF;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(41, 98, 255, 0.15);
}

:deep(.arco-modal-title) {
  color: #2962FF;
  font-weight: 700;
  font-size: 1.125rem;
}

:deep(.arco-modal-body) {
  padding: 2rem;
  background: rgba(248, 249, 250, 0.95) !important;
  color: #1F2937;
}

/* 亮色模式 */
:global(html:not(.dark)) :deep(.arco-modal-body) {
  background: rgba(248, 249, 250, 0.95) !important;
  color: #1F2937;
}

/* 深色模式 */
:global(html.dark) :deep(.arco-modal-body) {
  background: rgba(21, 26, 33, 0.95) !important;
  color: #f1f5f9;
}

:deep(.arco-modal-footer) {
  padding: 1.5rem 2rem;
  background: rgba(248, 249, 250, 0.8);
  border-top: 1px solid rgba(41, 98, 255, 0.15);
}

/* 亮色模式 */
:global(html:not(.dark)) :deep(.arco-modal-footer) {
  background: rgba(248, 249, 250, 0.8);
}

/* 深色模式 */
:global(html.dark) :deep(.arco-modal-footer) {
  background: rgba(15, 23, 42, 0.7);
}

:global(.dark) :deep(.arco-modal-footer) {
  background: rgba(15, 23, 42, 0.7);
  border-top: 1px solid rgba(41, 98, 255, 0.15);
}

:deep(.arco-btn-primary) {
  background: rgba(41, 98, 255, 0.2);
  border: 1px solid rgba(41, 98, 255, 0.3);
  color: #2962FF;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

:deep(.arco-btn-primary):hover {
  background: rgba(41, 98, 255, 0.3);
  border-color: rgba(41, 98, 255, 0.5);
  box-shadow: 0 4px 12px rgba(41, 98, 255, 0.2);
}

/* 亮色模式输入框 */
:global(html:not(.dark)) :deep(.arco-input-wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(41, 98, 255, 0.2) !important;
}

:global(html:not(.dark)) :deep(.arco-input-wrapper:focus-within) {
  box-shadow: 0 0 0 3px rgba(41, 98, 255, 0.15);
  border-color: rgba(41, 98, 255, 0.4) !important;
}

:global(html:not(.dark)) :deep(.arco-input) {
  color: #1F2937 !important;
  background: rgba(255, 255, 255, 0.9) !important;
}

:global(html:not(.dark)) :deep(.arco-input::placeholder) {
  color: rgba(31, 41, 55, 0.4);
}

:global(html:not(.dark)) :deep(.arco-form-item-label) {
  color: #6B7280;
}

/* 深色模式输入框 */
:global(html.dark) :deep(.arco-input-wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
  background: rgba(30, 41, 59, 0.8) !important;
  border: 1px solid rgba(41, 98, 255, 0.3) !important;
}

:global(html.dark) :deep(.arco-input-wrapper:focus-within) {
  box-shadow: 0 0 0 3px rgba(41, 98, 255, 0.2);
  border-color: rgba(41, 98, 255, 0.5) !important;
}

:global(html.dark) :deep(.arco-input) {
  color: #f1f5f9 !important;
  background: rgba(30, 41, 59, 0.8) !important;
}

:global(html.dark) :deep(.arco-input::placeholder) {
  color: rgba(241, 245, 249, 0.5);
}

:global(html.dark) :deep(.arco-form-item-label) {
  color: #94a3b8;
}

/* 全局模态框样式覆盖 */
:global(.arco-modal-mask) {
  background-color: rgba(0, 0, 0, 0.45);
}

:global(.arco-modal-header) {
  background: linear-gradient(135deg, rgba(41, 98, 255, 0.1) 0%, rgba(61, 90, 254, 0.05) 100%);
  border-bottom: 1px solid rgba(41, 98, 255, 0.15);
}

:global(.arco-modal-title) {
  color: #2962FF;
  font-weight: 700;
}

/* 亮色模式全局样式 */
:global(html:not(.dark)) .arco-modal {
  background: rgba(248, 249, 250, 0.95) !important;
  border: 1px solid rgba(41, 98, 255, 0.15);
}

:global(html:not(.dark)) .arco-modal-body {
  background: rgba(248, 249, 250, 0.95) !important;
  color: #1F2937;
}

:global(html:not(.dark)) .arco-modal-footer {
  background: rgba(248, 249, 250, 0.8);
  border-top: 1px solid rgba(41, 98, 255, 0.15);
}

/* 深色模式全局样式 */
:global(html.dark) .arco-modal {
  background: rgba(21, 26, 33, 0.95) !important;
  border: 1px solid rgba(41, 98, 255, 0.15);
}

:global(html.dark) .arco-modal-body {
  background: rgba(21, 26, 33, 0.95) !important;
  color: #f1f5f9;
}

:global(html.dark) .arco-modal-footer {
  background: rgba(15, 23, 42, 0.7);
  border-top: 1px solid rgba(41, 98, 255, 0.15);
}

/* 亮色模式输入框全局样式 */
:global(html:not(.dark)) .arco-input-number-wrapper {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(41, 98, 255, 0.2) !important;
}

:global(html:not(.dark)) .arco-input-number {
  color: #1F2937 !important;
  background: rgba(255, 255, 255, 0.9) !important;
}

/* 深色模式输入框全局样式 */
:global(html.dark) .arco-input-number-wrapper {
  background: rgba(30, 41, 59, 0.8) !important;
  border: 1px solid rgba(41, 98, 255, 0.3) !important;
}

:global(html.dark) .arco-input-number {
  color: #f1f5f9 !important;
  background: rgba(30, 41, 59, 0.8) !important;
}

:global(.arco-input-number-button) {
  color: #2962FF;
}
</style>

