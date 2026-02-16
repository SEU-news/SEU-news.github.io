<template>
  <div class="timeline">
    <div
      v-for="(milestone, index) in milestones"
      :key="index"
      class="timeline-item"
      :class="{ 'timeline-item-right': index % 2 === 1 }"
      :style="{ animationDelay: `${index * 150}ms` }"
    >
      <div class="timeline-content">
        <div class="timeline-date">{{ milestone.date }}</div>
        <h3 class="timeline-title">{{ milestone.title }}</h3>
        <p class="timeline-description">{{ milestone.description }}</p>
      </div>
      <div class="timeline-dot"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  milestones: {
    type: Array as () => Array<{
      date: string
      title: string
      description: string
    }>,
    required: true
  }
})
</script>

<style scoped>
.timeline {
  position: relative;
  padding: 20px 0;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #667eea, #764ba2);
  transform: translateX(-50%);
}

.timeline-item {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  position: relative;
  opacity: 0;
  animation: fadeSlideUp 0.6s ease forwards;
}

.timeline-item-right {
  flex-direction: row-reverse;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-content {
  flex: 1;
  padding: 20px 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  max-width: calc(50% - 30px);
}

.timeline-item-right .timeline-content {
  text-align: right;
}

.timeline-content:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.timeline-date {
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 8px;
}

.timeline-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.timeline-description {
  font-size: 0.95rem;
  color: #6c757d;
  line-height: 1.6;
  margin: 0;
}

.timeline-dot {
  position: absolute;
  left: 50%;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: translateX(-50%);
  z-index: 1;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
}

@media (max-width: 768px) {
  .timeline::before {
    left: 20px;
  }

  .timeline-item {
    flex-direction: column;
    align-items: flex-start;
    padding-left: 50px;
  }

  .timeline-item-right {
    flex-direction: column;
    align-items: flex-start;
  }

  .timeline-content {
    max-width: 100%;
    text-align: left !important;
  }

  .timeline-dot {
    left: 20px;
  }
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
