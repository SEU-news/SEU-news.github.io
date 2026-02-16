<template>
  <div class="news-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <h1>至善新声</h1>
      <p>校园信息与动态</p>
    </header>

    <!-- 消息列表 -->
    <main class="news-container">
      <div v-if="loading" class="loading-state">
        <LoadingSpinner />
      </div>

      <div v-else-if="contents.length === 0" class="empty-state">
        <EmptyState
          icon="📰"
          title="暂无消息"
          description="还没有发布任何消息"
        />
      </div>

      <div v-else class="contents-list">
        <div
          v-for="item in contents"
          :key="item.id"
          class="content-card"
        >
          <div class="card-header">
            <div class="card-badges">
              <span v-if="item.tag" class="badge badge-secondary">{{ item.tag }}</span>
              <span v-if="item.status_display" class="badge" :class="getStatusBadgeClass(item.status)">
                {{ item.status_display }}
              </span>
            </div>
            <span class="publish-date">{{ item.formatted_created_at }}</span>
          </div>
          <h3 class="card-title">{{ item.title }}</h3>
          <div class="card-content" v-html="item.content"></div>
          <div v-if="item.link" class="card-footer">
            <a :href="item.link" target="_blank" class="link-btn">
              查看详情
            </a>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination-wrapper">
        <Pagination
          :current-page="currentPage"
          :total-pages="totalPages"
          @page-change="handlePageChange"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getEntries } from '../api/content.js'
import EmptyState from '../components/EmptyState.vue'
import Pagination from '../components/Pagination.vue'
import LoadingSpinner from '../components/admin/LoadingSpinner.vue'

// 数据状态
const loading = ref(true)
const contents = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)

// 总页数
const totalPages = ref(0)

// 加载消息列表
async function loadContents() {
  loading.value = true
  try {
    const response = await getEntries({
      page: currentPage.value,
      page_size: pageSize.value,
      status: 'published'
    })
    contents.value = response.results || []
    totalCount.value = response.count || 0
    totalPages.value = Math.ceil(totalCount.value / pageSize.value)
  } catch (error) {
    console.error('加载消息失败:', error)
  } finally {
    loading.value = false
  }
}

// 页码变化处理
function handlePageChange(page) {
  currentPage.value = page
  loadContents()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 获取状态徽章样式
function getStatusBadgeClass(status) {
  const classMap = {
    'draft': 'badge-secondary',
    'pending': 'badge-warning',
    'reviewed': 'badge-info',
    'rejected': 'badge-danger',
    'published': 'badge-success',
    'terminated': 'badge-dark'
  }
  return classMap[status] || 'badge-secondary'
}

// 初始化
onMounted(() => {
  loadContents()
})
</script>

<style scoped>
@import '../styles/layout.css';
@import '../styles/utilities.css';
@import '../styles/alerts.css';

/* 页面容器 */
.news-page {
  min-height: 100vh;
  background: #fafafa;
}

/* 页面头部 */
.page-header {
  text-align: center;
  padding: 40px 20px 30px;
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
  margin: 0;
}

/* 消息列表容器 */
.news-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px 20px;
}

/* 内容列表 */
.contents-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 内容卡片 */
.content-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.content-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.card-badges {
  display: flex;
  gap: 8px;
}

.publish-date {
  font-size: 0.85rem;
  color: #999999;
}

/* 卡片标题 */
.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333333;
  margin: 0 0 15px 0;
  line-height: 1.4;
}

/* 卡片内容 */
.card-content {
  color: #666666;
  line-height: 1.6;
  margin-bottom: 15px;
}

/* 卡片底部 */
.card-footer {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.link-btn {
  display: inline-block;
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.link-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

/* 分页容器 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 30px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

/* 空状态 */
.empty-state {
  padding: 40px 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 30px 15px 20px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .news-container {
    padding: 20px 15px;
  }

  .content-card {
    padding: 15px;
  }

  .card-title {
    font-size: 1.1rem;
  }
}
</style>
