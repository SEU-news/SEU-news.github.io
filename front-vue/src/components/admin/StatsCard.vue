<template>
  <div class="stat-card" :class="variantClass" @click="handleClick">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ displayValue }}</div>
    <div class="stat-icon">{{ icon }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    default: 0
  },
  icon: {
    type: String,
    default: '📊'
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'info'].includes(value)
  },
  clickable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const variantClass = computed(() => {
  return `stat-card-${props.variant}`
})

const displayValue = computed(() => {
  return typeof props.value === 'number' ? props.value.toLocaleString() : props.value
})

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: default;
  border-left: 4px solid #3498db;
  position: relative;
  overflow: hidden;
}

.stat-card[class*="clickable"],
.stat-card:where(.clickable) {
  cursor: pointer;
}

.stat-card:where(.clickable):hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Variants */
.stat-card-default {
  border-left-color: #3498db;
}

.stat-card-primary {
  border-left-color: #3498db;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card-success {
  border-left-color: #2ecc71;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.stat-card-warning {
  border-left-color: #f39c12;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-card-info {
  border-left-color: #1abc9c;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1;
}

.stat-icon {
  position: absolute;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  font-size: 2.5rem;
  opacity: 1;
  line-height: 1;
  pointer-events: none;
  z-index: 1;
}

.stat-icon {
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", "EmojiFont", sans-serif;
}
</style>
