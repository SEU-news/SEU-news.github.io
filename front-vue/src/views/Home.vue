<template>
  <div class="home-page">
    <!-- 欢迎标题 -->
    <header class="page-header">
      <h1>至善新声</h1>
      <p>东南大学校园信息聚合平台</p>
    </header>

    <!-- 主内容区 -->
    <main class="main-container">
      <!-- 左侧：PDF 预览 -->
      <section class="pdf-section">
        <div class="section-header">
          <h2>最新公告 PDF</h2>
          <button @click="refreshPDF" class="btn btn-sm btn-outline-primary" title="刷新PDF">
            刷新
          </button>
        </div>

        <div class="pdf-container">
          <div v-if="pdfLoading" class="pdf-loading">
            <LoadingSpinner />
          </div>
          <iframe
            v-else
            :key="pdfTimestamp"
            :src="pdfUrl"
            class="pdf-iframe"
            frameborder="0"
          ></iframe>
        </div>
      </section>

      <!-- 右侧：功能入口 -->
      <section class="actions-section">
        <div class="section-header">
          <h2>快速入口</h2>
        </div>

        <div class="actions-list">
          <!-- 访客登录 -->
          <div class="action-card" @click="goToLogin">
            <div class="card-icon">👤</div>
            <h3>访客登录</h3>
            <p>进入访客系统</p>
          </div>

          <!-- 管理入口 -->
          <div class="action-card" @click="goToManage">
            <div class="card-icon">⚙️</div>
            <h3>管理入口</h3>
            <p>后台管理系统</p>
          </div>

          <!-- 消息列表 -->
          <router-link to="/news" class="action-card link-card">
            <div class="card-icon">📰</div>
            <h3>消息列表</h3>
            <p>查看最新消息</p>
          </router-link>

          <!-- 联系我们 -->
          <router-link to="/contact" class="action-card link-card">
            <div class="card-icon">✉️</div>
            <h3>联系我们</h3>
            <p>意见反馈</p>
          </router-link>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoadingSpinner from '../components/admin/LoadingSpinner.vue'

const router = useRouter()
const authStore = useAuthStore()

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// PDF状态
const pdfLoading = ref(false)
const pdfTimestamp = ref(0)

// PDF URL
const pdfUrl = computed(() => {
  const baseUrl = API_BASE_URL.replace('/api', '')
  return `${baseUrl}/static/latest.pdf?t=${pdfTimestamp.value}`
})

// 跳转到管理页
function goToManage() {
  authStore.restoreState()

  if (!authStore.isLoggedIn) {
    router.push('/login?redirect=/manage')
    return
  }

  if (!authStore.hasEditorPerm && !authStore.hasAdminPerm) {
    alert('您没有管理权限')
    return
  }

  router.push('/manage')
}

// 跳转到登录页
function goToLogin() {
  authStore.restoreState()

  if (authStore.isLoggedIn) {
    alert('您已经登录了！')
    return
  }

  router.push('/login')
}

// 刷新PDF
function refreshPDF() {
  pdfTimestamp.value = Date.now()
}

// 初始化
onMounted(() => {
  pdfTimestamp.value = Date.now()
})
</script>

<style scoped>
@import '../styles/layout.css';
@import '../styles/utilities.css';
@import '../styles/buttons.css';

/* 页面容器 */
.home-page {
  min-height: 100vh;
  background: #fafafa;
  display: flex;
  flex-direction: column;
}

/* 页面头部 */
.page-header {
  text-align: center;
  padding: 30px 20px 20px;
  background: white;
  border-bottom: 1px solid #e9ecef;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #333333;
  margin: 0 0 0.5rem 0;
}

.page-header p {
  color: #666666;
  margin: 0 0 1rem 0;
}

.old-link {
  display: inline-block;
  padding: 6px 16px;
  background: #f0f0f0;
  color: #667eea;
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 0.85rem;
}

.old-link:hover {
  background: #667eea;
  color: white;
}

/* 主内容容器 */
.main-container {
  display: flex;
  gap: 20px;
  padding: 20px;
  flex: 1;
  min-height: calc(100vh - 120px);
}

/* 左侧 PDF 区域 */
.pdf-section {
  flex: 2;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333333;
  margin: 0;
}

.pdf-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 600px;
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 600px;
}

/* 右侧功能区域 */
.actions-section {
  flex: 1;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 功能卡片 */
.action-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.action-card:hover {
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  border-color: #667eea;
}

.card-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.action-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #333333;
  margin: 0;
}

.action-card p {
  font-size: 0.85rem;
  color: #666666;
  margin: 0;
}

.link-card {
  text-decoration: none;
  color: inherit;
}

.link-card:hover h3 {
  color: #667eea;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .main-container {
    flex-direction: column;
  }

  .pdf-section {
    flex: none;
    min-height: 600px;
  }

  .actions-section {
    max-width: none;
    flex: none;
  }

  .actions-list {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px 15px 15px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .main-container {
    padding: 10px;
    gap: 15px;
  }

  .actions-list {
    flex-direction: column;
  }
}
</style>
