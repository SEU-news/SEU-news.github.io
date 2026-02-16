<template>
  <div class="home-page">
    <!-- 顶部欢迎区域 -->
    <header class="welcome-section">
      <h1 class="welcome-title">至善新声</h1>
      <p class="welcome-subtitle">东南大学校园信息聚合平台</p>
      <a href="javascript:void(0)" @click="redirectToOldSystem" class="old-system-link">
        访问旧系统
      </a>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- PDF 预览卡片 -->
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

      <!-- 功能入口卡片 -->
      <section class="quick-actions">
        <div class="section-header">
          <h2>快速入口</h2>
        </div>

        <div class="action-cards-grid">
          <!-- 登录/访客 -->
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

          <!-- 查看消息 -->
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

// 跳转到旧系统
const redirectToOldSystem = () => {
  const oldSystemUrl = 'http://' + window.location.hostname + ':42610'
  window.open(oldSystemUrl, '_blank')
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 1rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 2rem 0;
}

.old-system-link {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.old-system-link:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 主内容区 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 区域标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

/* PDF 区域 */
.pdf-section {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.pdf-container {
  width: 100%;
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

/* 快速入口区域 */
.quick-actions {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* 卡片网格 */
.action-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

/* 动作卡片 */
.action-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 25px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  border-color: #667eea;
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.action-card h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333333;
  margin: 0 0 0.5rem 0;
}

.action-card p {
  font-size: 0.9rem;
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
@media (max-width: 768px) {
  .home-page {
    padding: 10px;
  }

  .welcome-section {
    padding: 30px 15px;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .action-cards-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
  }

  .action-card {
    padding: 20px 15px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
