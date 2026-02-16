<template>
  <div class="contact-card">
    <div class="contact-icon">{{ icon }}</div>
    <div class="contact-content">
      <div class="contact-label">{{ label }}</div>
      <a v-if="link" :href="link" class="contact-value contact-link">{{ value }}</a>
      <div v-else class="contact-value">{{ value }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  icon: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  value: {
    type: String,
    required: true
  },
  link: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.contact-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  align-items: center;
  gap: 15px;
  height: 100%;
}

.contact-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.contact-icon {
  font-size: 2.5rem;
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
  line-height: 1;
  flex-shrink: 0;
}

.contact-content {
  flex-grow: 1;
}

.contact-label {
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.contact-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  word-break: break-word;
}

.contact-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.2s ease;
}

.contact-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
