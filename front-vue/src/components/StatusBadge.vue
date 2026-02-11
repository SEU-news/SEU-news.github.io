<template>
  <span class="status-badge" :class="sizeClass" :style="badgeStyle">
    <span class="status-icon">{{ config.icon }}</span>
    <span class="status-label">{{ config.label }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { useStatusConfig } from '@/composables/useStatusConfig'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})

const { getStatusConfig } = useStatusConfig()

const config = computed(() => getStatusConfig(props.status))

const sizeClass = computed(() => `status-badge-${props.size}`)

const badgeStyle = computed(() => ({
  backgroundColor: `${config.value.color}15`,
  color: config.value.color
}))
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 20px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.status-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Size variants */
.status-badge-small {
  padding: 4px 10px;
  font-size: 0.75rem;
}

.status-badge-medium {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.status-badge-large {
  padding: 8px 16px;
  font-size: 0.95rem;
}

/* Icon and label */
.status-icon {
  font-size: 1.1em;
  line-height: 1;
}

.status-label {
  line-height: 1;
}
</style>
