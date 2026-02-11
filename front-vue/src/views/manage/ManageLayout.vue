<template>
  <div class="manage-layout">
    <!-- 页面头部 -->
    <div class="manage-header">
      <h2>{{ pageTitle }}</h2>
      <p>{{ pageDescription }}</p>
    </div>
    <!-- 主内容 -->
    <main class="manage-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 根据路由动态设置页面标题
const pageTitle = computed(() => {
  const titles = {
    'ManageList': '消息刊载',
    'ManagePublish': '发布内容'
  }
  return titles[route.name] || '管理中心'
})

const pageDescription = computed(() => {
  const descriptions = {
    'ManageList': '管理和编辑所有消息内容',
    'ManagePublish': '发布已审核的内容'
  }
  return descriptions[route.name] || ''
})
</script>

<style scoped>
@import '../../styles/manage.css';
</style>
