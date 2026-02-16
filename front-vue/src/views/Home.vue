<template>
  <div class="home">
    <h1>至善新声门户</h1>
    <p>欢迎访问 News</p>
    <a href="javascript:void(0)" @click="redirectToOldSystem">旧的系统</a>

    <div class="home-container">

      <!-- 左侧 PDF -->
      <div class="pdf-card">
        <h3>最新公告 PDF</h3>
        <iframe :src="pdfUrl" width="100%" height="600px" style="border:none;"></iframe>
      </div>

      <!-- 右侧功能卡片 -->
      <div class="features_column">
        <div class="features_row">
          <div class="feature-card">
            <h3>最新动态</h3>
            <p>了解校园最新消息</p>
          </div>
          <div class="feature-card">
            <h3>学术资讯</h3>
            <p>掌握学术前沿信息</p>
          </div>
          <div class="feature-card">
            <h3>校园生活</h3>
            <p>关注校园文化活动</p>
          </div>
        </div>
        <div class="features_row">
          <div @click="goToLogin" class="feature-card link-card" style="cursor: pointer;">
            <h3>访客登录</h3>
            <p>进入访客系统</p>
          </div>

          <div @click="goToManage" class="feature-card link-card" style="cursor: pointer;">
            <h3>管理入口</h3>
            <p>后台管理入口</p>
          </div>

          <router-link to="/contact" class="feature-card link-card">
            <h3>联系我们</h3>
            <p>欢迎留言</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
  padding: 0.5rem;
  min-height: 100vh;
  background: #fafafa;
}

.home-container {
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: flex-start;
  flex-wrap: wrap;
  padding: 2rem;
}

/* PDF 卡片 */
.pdf-card {
  flex: 2 1 300px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 1rem;
  background: white;
  transition: all 0.2s ease;
}

.pdf-card:hover {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.3);
}

/* 功能卡片 */
.features_row {
  flex: 1 1 250px;
  display: flex;
  flex-direction: row;
  gap: 1rem;
}

.features_column {
  flex: 1 1 250px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-width: 150px;
  flex: 1;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  background: white;
  transition: all 0.2s ease;
  text-align: center;
  color: #333;
}

.feature-card h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-weight: 500;
}

.feature-card p {
  margin: 0;
  color: #666;
}

/* 鼠标悬停时美化 */
.feature-card:hover {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.3);
}

.link-card {
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.link-card:hover {
  color: #667eea;
}

h1 {
  color: #333;
  margin-bottom: 0.5rem;
}

p {
  color: #666;
}
</style>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// API基础URL（使用相对路径，支持本地开发和远程部署）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// PDF URL（动态构建，添加时间戳以刷新缓存）
const pdfTimestamp = ref(0)
const pdfUrl = computed(() => {
  const baseUrl = API_BASE_URL.replace('/api', '')
  return `${baseUrl}/static/latest.pdf?t=${pdfTimestamp.value}`
})

function goToManage() {
  // 先恢复登录状态
  authStore.restoreState()

  // 未登录 → 跳转到登录页
  if (!authStore.isLoggedIn) {
    router.push('/login?redirect=/manage')
    return
  }

  // 已登录但无权限 → 提示
  if (!authStore.hasEditorPerm && !authStore.hasAdminPerm) {
    alert('您没有管理权限')
    return
  }

  // 有权限 → 跳转到管理页
  router.push('/manage')
}

function goToLogin() {
  // 先恢复登录状态
  authStore.restoreState()

  // 如果已登录，提示用户
  if (authStore.isLoggedIn) {
    alert('您已经登录了！')
    return
  }

  // 跳转到登录页
  router.push('/login')
}

const redirectToOldSystem = () => {
  const oldSystemUrl = 'http://' + window.location.hostname + ':42610';
  window.open(oldSystemUrl, '_blank');
}

// 初始化时间戳
onMounted(() => {
  pdfTimestamp.value = Date.now()
})
</script>
