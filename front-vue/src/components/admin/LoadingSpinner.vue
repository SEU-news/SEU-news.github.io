<template>
  <div class="loading-spinner" :class="sizeClass">
    <span>{{ text }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  text: {
    type: String,
    default: '加载中...'
  }
})

const sizeClass = computed(() => `loading-spinner-${props.size}`)
</script>

<style scoped>
.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  color: #6c757d;
}

.loading-spinner::before {
  content: '';
  width: 40px;
  height: 40px;
  border: 3px solid #dee2e6;
  border-top-color: #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 15px;
  flex-shrink: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Small variant */
.loading-spinner-small {
  padding: 20px;
  font-size: 0.875rem;
}

.loading-spinner-small::before {
  width: 24px;
  height: 24px;
  border-width: 2px;
  margin-right: 10px;
}

/* Large variant */
.loading-spinner-large {
  padding: 60px;
  font-size: 1.125rem;
}

.loading-spinner-large::before {
  width: 56px;
  height: 56px;
  border-width: 4px;
  margin-right: 20px;
}
</style>
