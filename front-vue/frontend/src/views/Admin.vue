<template>
  <head>
    <title>Admin 管理页面</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/css/bootstrap.min.css">
  </head>

  <div class="container mt-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>所有条目管理</h2>
      <div>
        <strong>您好, 尊敬的管理员 {{ username }}</strong>
        <button @click="goHome" class="btn btn-secondary">返回主页</button>
        <button @click="goUserAdmin" class="btn btn-info">用户管理</button>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <!-- 排序按钮 -->
    <div class="d-flex flex-wrap mb-3">
      <button
        class="btn btn-outline-primary me-2 mb-2"
        @click="changeSort('created_at', 'asc')"
      >按上传时间 ↑</button>
      <button
        class="btn btn-outline-primary me-2 mb-2"
        @click="changeSort('created_at', 'desc')"
      >按上传时间 ↓</button>

      <button
        class="btn btn-outline-secondary me-2 mb-2"
        @click="changeSort('updated_at', 'asc')"
      >按更新时间 ↑</button>
      <button
        class="btn btn-outline-secondary mb-2"
        @click="changeSort('updated_at', 'desc')"
      >按更新时间 ↓</button>
    </div>

    <!-- 表格 -->
    <table class="table table-hover">
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
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in entries" :key="entry.id">
          <td>
            <button class="btn btn-sm btn-warning me-1" @click="recall(entry.id)">召回</button>
            <button class="btn btn-sm btn-danger" @click="deleteEntry(entry.id)">删除</button>
          </td>
          <td>
            <a :href="entry.link" target="_blank" rel="noopener noreferrer">{{ entry.title }}</a>
          </td>
          <td :class="statusClass(entry.status)">{{ entry.status }}</td>
          <td>{{ shortText(entry.content) }}</td>
          <td>{{ entry.type }}</td>
          <td>{{ entry.reviewer_username }}</td>
          <td>{{ entry.created_at }}</td>
          <td>{{ entry.describer_username }}</td>
        </tr>
      </tbody>
    </table>

    <!-- 分页 -->
    <div class="pagination d-flex justify-content-center mt-3">
      <button class="btn btn-outline-primary me-2" :disabled="page === 1" @click="page--">上一页</button>
      <span>第 {{ page }} / {{ totalPages }} 页</span>
      <button class="btn btn-outline-primary ms-2" :disabled="page === totalPages" @click="page++">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const entries = ref([])
const username = ref('Admin')
const message = ref('')
const page = ref(1)
const totalPages = ref(1)
const sortField = ref('created_at')
const sortOrder = ref('desc')

async function fetchEntries() {
  const response = await fetch(
    `/api/admin/entries/?page=${page.value}&sort=${sortField.value}&order=${sortOrder.value}`
  )
  const data = await response.json()
  entries.value = data.entries
  totalPages.value = data.total_pages
}

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

async function recall(id) {
  if (confirm('确定召回此条目？') && confirm('此操作不可撤销！')) {
    await fetch(`/api/recall/${id}/`, { method: 'POST' })
    message.value = '已召回'
    fetchEntries()
  }
}

async function deleteEntry(id) {
  if (confirm('确定删除此条目？') && confirm('此操作不可撤销！')) {
    await fetch(`/api/delete/${id}/`, { method: 'POST' })
    message.value = '已删除'
    fetchEntries()
  }
}

function changeSort(field, order) {
  sortField.value = field
  sortOrder.value = order
  fetchEntries()
}

function goHome() {
  router.push('/')
}
function goUserAdmin() {
  router.push('/user-admin')
}

onMounted(fetchEntries)
watch(page, fetchEntries)
</script>

<style scoped>
.table-hover th, .table-hover td {
  vertical-align: middle;
}
</style>
