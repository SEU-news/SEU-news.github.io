<template>
  <div class="team-card">
    <div class="team-avatar">
      <span class="avatar-initial">{{ initial }}</span>
    </div>
    <h3 class="team-name">{{ name }}</h3>
    <span class="team-role">{{ role }}</span>
    <p class="team-description">{{ description }}</p>
    <a v-if="github" :href="github" target="_blank" rel="noopener noreferrer" class="team-github">
      GitHub ↗
    </a>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  role: {
    type: String,
    required: true
  },
  avatar: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    required: true
  },
  github: {
    type: String,
    default: ''
  }
})

const initial = computed(() => {
  return props.name.charAt(0).toUpperCase()
})
</script>

<style scoped>
.team-card {
  background: white;
  border-radius: 12px;
  padding: 30px 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  text-align: center;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.team-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.team-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-initial {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  line-height: 1;
}

.team-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.team-role {
  display: inline-block;
  padding: 4px 12px;
  background: #f0f0f0;
  border-radius: 12px;
  font-size: 0.85rem;
  color: #667eea;
  margin-bottom: 15px;
}

.team-description {
  font-size: 0.95rem;
  color: #6c757d;
  line-height: 1.6;
  margin: 0 0 15px 0;
  flex-grow: 1;
}

.team-github {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.team-github:hover {
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
