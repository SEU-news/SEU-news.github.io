<template>
  <div class="container mt-5">
    <h2>搜索功能</h2>

    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <!-- 搜索表单 -->
    <div class="card mb-4">
      <div class="card-body">
        <form @submit.prevent="handleSearch">
          <div class="row g-3">
            <div class="col-md-8">
              <input
                v-model="searchQuery"
                type="text"
                class="form-control"
                placeholder="输入关键词搜索..."
                required
              />
            </div>
            <div class="col-md-4">
              <button type="submit" class="btn btn-primary w-100" :disabled="isSearching">
                {{ isSearching ? '搜索中...' : '搜索' }}
              </button>
            </div>
          </div>

          <!-- 高级搜索选项 -->
          <div class="mt-3">
            <button
              type="button"
              class="btn btn-sm btn-link p-0"
              @click="showAdvanced = !showAdvanced"
            >
              {{ showAdvanced ? '收起高级选项' : '展开高级选项' }}
            </button>

            <div v-if="showAdvanced" class="card mt-2">
              <div class="card-body">
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">类型</label>
                    <select v-model="searchFilters.type" class="form-select">
                      <option value="">全部</option>
                      <option value="教务">教务</option>
                      <option value="科研">科研</option>
                      <option value="活动">活动</option>
                      <option value="通知">通知</option>
                      <option value="招聘">招聘</option>
                      <option value="其他">其他</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">状态</label>
                    <select v-model="searchFilters.status" class="form-select">
                      <option value="">全部</option>
                      <option value="draft">草稿</option>
                      <option value="pending">待审核</option>
                      <option value="reviewed">已审核</option>
                      <option value="published">已发布</option>
                      <option value="rejected">已拒绝</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-if="hasSearched" class="card">
      <div class="card-header">
        <h5 class="mb-0">
          搜索结果
          <span class="badge bg-secondary ms-2">{{ searchResults.length }} 条</span>
        </h5>
      </div>
      <div class="card-body">
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">搜索中...</span>
          </div>
        </div>

        <div v-else-if="searchResults.length > 0" class="list-group">
          <div
            v-for="entry in searchResults"
            :key="entry.id"
            class="list-group-item list-group-item-action"
          >
            <div class="d-flex w-100 justify-content-between align-items-start">
              <div>
                <h6 class="mb-1">
                  <a
                    v-if="entry.link"
                    :href="entry.link"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-decoration-none"
                  >
                    {{ entry.title }}
                  </a>
                  <span v-else>{{ entry.title }}</span>
                </h6>
                <p class="mb-1 text-muted">{{ entry.content?.slice(0, 200) }}...</p>
                <small class="text-muted">
                  <span class="badge bg-primary me-2">{{ entry.type }}</span>
                  <span class="badge me-2" :class="getStatusBadgeClass(entry.status)">
                    {{ entry.status_display }}
                  </span>
                  {{ entry.creator_username }} - {{ entry.formatted_created_at }}
                </small>
              </div>
            </div>
            <div class="mt-2">
              <button
                v-if="entry.status === 'reviewed' || entry.status === 'published'"
                class="btn btn-sm btn-outline-primary"
                @click="goReview(entry.id)"
              >
                修改
              </button>
              <button
                v-if="entry.creator_username === currentUser"
                class="btn btn-sm btn-outline-danger"
                @click="goEdit(entry.id)"
              >
                编辑
              </button>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-5 text-muted">
          <div class="mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" class="text-muted" viewBox="0 0 16 16">
              <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
            </svg>
          </div>
          <h5>没有找到相关内容</h5>
          <p>试试其他关键词吧</p>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div v-if="!hasSearched" class="card mt-4">
      <div class="card-body text-center">
        <h5 class="mb-3">快速搜索</h5>
        <div class="d-flex flex-wrap gap-2 justify-content-center">
          <button
            v-for="keyword in popularKeywords"
            :key="keyword"
            class="btn btn-sm btn-outline-secondary"
            @click="quickSearch(keyword)"
          >
            {{ keyword }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { searchEntries } from '../api/content.js'

const router = useRouter()

// 搜索相关
const searchQuery = ref('')
const searchResults = ref([])
const hasSearched = ref(false)
const isSearching = ref(false)
const showAdvanced = ref(false)

// 高级搜索过滤器
const searchFilters = ref({
  type: '',
  status: '',
})

// 状态
const message = ref('')
const messageClass = ref('alert-info')
const currentUser = ref('') // 从 localStorage 或状态管理获取

// 热门关键词
const popularKeywords = ref([
  '教务',
  '考试',
  '讲座',
  '活动',
  '通知',
  '奖学金',
  '招聘',
  '科研',
])

// 搜索
async function handleSearch() {
  if (!searchQuery.value.trim()) {
    showMessage('请输入搜索关键词', 'alert-warning')
    return
  }

  isSearching.value = true
  message.value = ''
  hasSearched.value = true

  try {
    const data = await searchEntries(searchQuery.value)

    // 过滤结果（如果使用了高级搜索）
    let results = data.results || data.entries || []

    if (searchFilters.value.type) {
      results = results.filter(r => r.type === searchFilters.value.type)
    }
    if (searchFilters.value.status) {
      results = results.filter(r => r.status === searchFilters.value.status)
    }

    searchResults.value = results
  } catch (err) {
    showMessage('搜索失败：' + err.message, 'alert-danger')
  } finally {
    isSearching.value = false
  }
}

// 快速搜索
function quickSearch(keyword) {
  searchQuery.value = keyword
  handleSearch()
}

// 前往审核
function goReview(id) {
  router.push(`/review/${id}`)
}

// 前往编辑
function goEdit(id) {
  router.push(`/edit/${id}`)
}

// 显示消息
function showMessage(msg, cls = 'alert-info') {
  message.value = msg
  messageClass.value = cls
  setTimeout(() => { message.value = '' }, 5000)
}

// 获取状态徽章样式
function getStatusBadgeClass(status) {
  switch (status) {
    case 'draft': return 'bg-info'
    case 'pending': return 'bg-secondary'
    case 'reviewed': return 'bg-success'
    case 'rejected': return 'bg-danger'
    case 'published': return 'bg-primary'
    default: return 'bg-secondary'
  }
}
</script>

<style scoped>
@import '../styles/layout.css';
@import '../styles/utilities.css';
@import '../styles/buttons.css';
@import '../styles/forms.css';
@import '../styles/alerts.css';

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.card {
  margin-bottom: 1.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.card-body {
  background-color: #fff;
}

.btn-link {
  color: #0d6efd;
  text-decoration: none;
}

.btn-link:hover {
  text-decoration: underline;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.list-group-item {
  border: 1px solid rgba(0, 0, 0, 0.125);
  padding: 1rem;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.badge {
  margin-right: 0.25rem;
}
</style>
