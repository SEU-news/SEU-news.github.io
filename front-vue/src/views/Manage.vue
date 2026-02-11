<template>
  <div class="container mt-5">
    <!-- 顶部搜索和用户信息 -->
    <div class="row mb-3">
      <div class="col-md-6">
        <form @submit.prevent="fetchEntries">
          <div class="input-group">
            <input type="text" class="form-control" v-model="query" placeholder="Search content..." />
            <button class="btn btn-outline-secondary" type="submit">Search</button>
          </div>
        </form>
      </div>
      <div class="col-md-6 text-end">
        <button v-if="adminFlag" class="btn btn-primary" @click="goAdmin">管理员界面</button>
        <span class="me-2"><strong>{{ username }}</strong></span>
        <button class="btn btn-danger" @click="handleLogout">登出</button>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <!-- 功能按钮 -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>车大消息 消息刊载</h2>
      <div>
        <button class="btn btn-outline-primary" @click="handlePreview">预览</button>
        <button v-if="editorFlag" class="btn btn-primary" @click="goUpload">上传纯文本消息</button>
        <button v-if="editorFlag" class="btn btn-success" @click="goPublish">发布</button>
      </div>
    </div>

    <!-- URL 粘贴表单 -->
    <form @submit.prevent="handlePasteUrl" class="mb-4">
      <div class="input-group">
        <input type="text" class="form-control" v-model="link" placeholder="Paste url here..." required />
        <button class="btn btn-outline-secondary" type="submit">添加地址</button>
      </div>
    </form>

    <!-- 图片上传表单 -->
    <form @submit.prevent="handleUploadImage" enctype="multipart/form-data" class="mb-4">
      <div class="input-group">
        <input type="file" class="form-control" @change="onFileChange" accept="image/*" required />
        <button class="btn btn-outline-secondary" type="submit">上传图片</button>
      </div>
    </form>

    <!-- 排序按钮 -->
    <div class="d-flex flex-wrap mb-3">
      <button class="btn btn-outline-primary me-2 mb-2" @click="changeSort('created_at', 'asc')">按上传时间 ↑</button>
      <button class="btn btn-outline-primary me-2 mb-2" @click="changeSort('created_at', 'desc')">按上传时间 ↓</button>
      <button class="btn btn-outline-secondary me-2 mb-2" @click="changeSort('updated_at', 'asc')">按更新时间 ↑</button>
      <button class="btn btn-outline-secondary mb-2" @click="changeSort('updated_at', 'desc')">按更新时间 ↓</button>

      <small class="text-muted ms-auto mb-2">共 {{ total }} 条{{ query ? "（包含过滤结果）" : "" }}</small>
    </div>

    <!-- 内容表格 -->
    <table class="table table-hover" v-if="entries.length > 0">
      <thead>
        <tr>
          <th>操作</th>
          <th>标题</th>
          <th>状态</th>
          <th>描述</th>
          <th>刊载版块</th>
          <th>审阅人</th>
          <th>上传时间</th>
          <th>上工者</th>
          <th>锁定者</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="entry in entries" :key="entry.id">
          <tr v-if="entry">
          <td>
            <button v-if="editorFlag && entry.status === 'draft'" class="btn btn-sm btn-danger" @click="handleEdit(entry.id)">编辑</button>
            <button
              v-if="editorFlag && entry.status !== 'draft'"
              :class="entry.status === 'reviewed' || entry.status === 'published' ? 'btn btn-sm btn-success' : 'btn btn-sm btn-warning'"
              @click="handleReview(entry.id)"
            >
              {{ entry.status === 'reviewed' || entry.status === 'published' ? '修改' : '审核' }}
            </button>
            <button v-if="entry.creator_username === username" class="btn btn-sm btn-danger" @click="handleDelete(entry.id)">删除</button>
          </td>
          <td>
            <a :href="entry.link" target="_blank" rel="noopener noreferrer">{{ shortText(entry.title) }}</a>
          </td>
          <td :class="statusClass(entry.status)">{{ entry.status_display }}</td>
          <td>
            <span v-if="entry.content" :title="entry.content">{{ shortText(entry.content) }}</span>
          </td>
          <td>{{ entry.type }}</td>
          <td>{{ entry.reviewer_username }}</td>
          <td>{{ entry.formatted_created_at }}</td>
          <td :class="entry.describer_username === username ? 'table-success' : ''">{{ entry.describer_username }}</td>
          <td></td>
        </tr>
        </template>
      </tbody>
    </table>

    <!-- 空状态提示 -->
    <div v-else class="text-center py-5">
      <p class="text-muted">暂无内容，请先上传内容</p>
    </div>

    <!-- 分页 -->
    <nav aria-label="Page navigation">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: page === 1 }">
          <button class="page-link" @click="page--">上一页</button>
        </li>
        <li v-for="p in nearbyPages" :key="p" class="page-item" :class="{ active: p === page }">
          <button class="page-link" @click="goPage(p)">{{ p }}</button>
        </li>
        <li class="page-item" :class="{ disabled: page === totalPages }">
          <button class="page-link" @click="page++">下一页</button>
        </li>
      </ul>
      <form class="d-flex justify-content-center mt-2" @submit.prevent="goPage(inputPage)">
        <input type="number" class="form-control" v-model.number="inputPage" min="1" :max="totalPages" style="width: 80px;" />
        <button class="btn btn-primary">Go</button>
      </form>
    </nav>

    <!-- 每页显示条数 -->
    <div class="mb-3">
      <label for="pageSize">每页显示：</label>
      <select id="pageSize" class="form-select w-auto d-inline-block" v-model.number="pageSize" @change="fetchEntries">
        <option :value="10">10</option>
        <option :value="20">20</option>
        <option :value="50">50</option>
        <option :value="100">100</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getEntries, deleteEntry, pasteUrl, uploadImage } from '../api/content.js'
import { logout } from '../api/auth.js'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 数据
const entries = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const totalPages = ref(1)
const query = ref('')
const inputPage = ref(1)
const username = ref('') // 从 session 或 localStorage 获取
const adminFlag = ref(false)
const editorFlag = ref(false)
const message = ref('')
const messageClass = ref('alert-info')
const link = ref('')
const sortField = ref('created_at')
const sortOrder = ref('desc')
const selectedFile = ref(null)

// 工具函数
function shortText(text) {
  if (!text) return ''
  return text.length > 15 ? text.slice(0, 15) + '...' : text
}

function statusClass(status) {
  switch (status) {
    case 'pending': return 'table-secondary'
    case 'draft': return 'table-info'
    case 'reviewed': return 'table-success'
    case 'rejected': return 'table-danger'
    case 'published': return 'table-primary'
    default: return ''
  }
}

// 获取条目列表
async function fetchEntries() {
  try {
    console.log('fetchEntries called with params:', {
      page: page.value,
      page_size: pageSize.value,
      q: query.value,
      sort: sortField.value,
      order: sortOrder.value
    })

    const data = await getEntries({
      page: page.value,
      page_size: pageSize.value,
      q: query.value,
      sort: sortField.value,
      order: sortOrder.value,
    })

    console.log('fetchEntries received data:', data)

    // 处理返回数据格式，根据实际 API 响应调整
    entries.value = data.results || []
    total.value = data.count || 0
    totalPages.value = data.total_pages || 1

    console.log('fetchEntries set values:', {
      entriesCount: entries.value.length,
      total: total.value,
      totalPages: totalPages.value,
      entries: entries.value
    })
  } catch (err) {
    console.error('fetchEntries error:', err)
    showMessage('加载失败：' + err.message, 'alert-danger')
  }
}

function changeSort(field, order) {
  sortField.value = field
  sortOrder.value = order
  fetchEntries()
}

function goPage(p) {
  page.value = p
}

function showMessage(msg, cls = 'alert-info') {
  message.value = msg
  messageClass.value = cls
  setTimeout(() => { message.value = '' }, 5000)
}

// 按钮处理函数
function goAdmin() {
  router.push('/manage/admin')
}

function goUpload() {
  router.push('/manage/upload')
}

function goPublish() {
  router.push('/manage/publish')
}

async function handleLogout() {
  try {
    // 1. 调用后端登出API（清除session）
    await logout()

    // 2. 清除Pinia Store中的所有状态
    authStore.clearUser()

    // 3. 清除localStorage中的token（clearUser已清除user）
    localStorage.removeItem('token')

    // 4. 跳转到首页（不是登录页）
    router.push('/')
  } catch (err) {
    showMessage('登出失败：' + err.message, 'alert-danger')
  }
}

function handlePreview() {
  router.push('/manage/preview')
}

async function handlePasteUrl() {
  try {
    await pasteUrl({ url: link.value })
    showMessage('URL 添加成功', 'alert-success')
    link.value = ''
    fetchEntries()
  } catch (err) {
    showMessage('URL 添加失败：' + err.message, 'alert-danger')
  }
}

function onFileChange(e) {
  selectedFile.value = e.target.files[0]
}

async function handleUploadImage() {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('image', selectedFile.value)

  try {
    await uploadImage(formData)
    showMessage('图片上传成功', 'alert-success')
    selectedFile.value = null
    fetchEntries()
  } catch (err) {
    showMessage('图片上传失败：' + err.message, 'alert-danger')
  }
}

function handleEdit(id) {
  router.push(`/manage/edit/${id}`)
}

function handleReview(id) {
  router.push(`/manage/review/${id}`)
}

async function handleDelete(id) {
  if (!confirm('确定要删除这条内容吗？')) return

  try {
    await deleteEntry(id)
    showMessage('删除成功', 'alert-success')
    fetchEntries()
  } catch (err) {
    showMessage('删除失败：' + err.message, 'alert-danger')
  }
}

// 计算附近页码
const nearbyPages = computed(() => {
  const pages = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, page.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

onMounted(() => {
  // 从 authStore 读取用户信息
  username.value = authStore.user.username || ''
  adminFlag.value = authStore.hasAdminPerm || false
  editorFlag.value = authStore.hasEditorPerm || false

  console.log('Manage.vue onMounted:', {
    isLoggedIn: authStore.isLoggedIn,
    username: authStore.user.username,
    hasEditorPerm: authStore.hasEditorPerm,
    hasAdminPerm: authStore.hasAdminPerm,
    user: authStore.user
  })

  fetchEntries()
})

watch([page, pageSize], fetchEntries)
</script>

<style scoped>
/* 引入基础样式 */
@import '../styles/layout.css';
@import '../styles/utilities.css';
@import '../styles/buttons.css';
@import '../styles/forms.css';
@import '../styles/tables.css';
@import '../styles/alerts.css';
@import '../styles/navigation.css';

/* 组件特有样式 */
.container {
  max-width: 1400px;
  background: #fafafa;
  padding: 2rem;
}

.table-hover th, .table-hover td {
  vertical-align: middle;
}

h2 {
  color: #333;
  font-weight: 500;
}

/* 特有工具类 */
.w-auto {
  width: auto !important;
}
</style>
