<template>
  <div class="empty-state">
    <i :class="iconClass">{{ icon }}</i>
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <button v-if="actionLabel" class="empty-state-action" @click="$emit('action')">
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: {
    type: String,
    default: '📝'
  },
  title: {
    type: String,
    default: '暂无数据'
  },
  description: {
    type: String,
    default: '暂无相关数据'
  },
  actionLabel: {
    type: String,
    default: null
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})

defineEmits(['action'])

const iconClass = computed(() => `empty-state-icon-${props.size}`)
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.empty-state i {
  display: block;
  color: #dee2e6;
  margin: 0 auto 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 0;
}

/* Size variants */
.empty-state-icon-small {
  font-size: 2rem;
}

.empty-state-icon-medium {
  font-size: 4rem;
}

.empty-state-icon-large {
  font-size: 6rem;
}

/* Action button */
.empty-state-action {
  margin-top: 20px;
  padding: 10px 24px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  border: 1.5px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.empty-state-action:hover {
  background: rgba(102, 126, 234, 0.12);
  border-color: rgba(102, 126, 234, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.empty-state-action:active {
  transform: translateY(0);
}
</style>
