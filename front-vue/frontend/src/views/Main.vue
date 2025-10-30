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
        <strong>您好, {{ username }}</strong>
        <button class="btn btn-danger" @click="logout">登出</button>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <!-- 功能按钮 -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>车大消息 消息刊载</h2>
      <div>
        <button class="btn btn-outline-primary" @click="preview">预览</button>
        <button class="btn btn-primary" @click="uploadText">上传纯文本消息</button>
        <button class="btn btn-success" @click="publish">发布</button>
      </div>
    </div>

    <!-- URL 粘贴表单 -->
    <form @submit.prevent="addLink" class="mb-4">
      <div class="input-group">
        <input type="text" class="form-control" v-model="link" placeholder="Paste url here..." required />
        <button class="btn btn-outline-secondary" type="submit">添加地址</button>
      </div>
    </form>

    <!-- 图片上传表单 -->
    <form @submit.prevent="uploadImage" enctype="multipart/form-data" class="mb-4">
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
          <th>锁定者</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in entries" :key="entry.id" v-if="entry.type !== 'DDLOnly'">
          <td>
            <button v-if="editorFlag && entry.status === 'draft'" class="btn btn-sm btn-danger" @click="edit(entry.id)">编辑</button>
            <button v-if="editorFlag && entry.status !== 'draft'" :class="entry.status === 'reviewed' || entry.status === 'published' ? 'btn btn-sm btn-success' : 'btn btn-sm btn-warning'" @click="review(entry.id)">
              {{ entry.status === 'reviewed' || entry.status === 'published' ? '修改' : '审核' }}
            </button>
            <button v-if="entry.creator_username === username" class="btn btn-sm btn-danger" @click="deleteEntry(entry.id)">删除</button>
          </td>
          <td>
            <a :href="entry.link" target="_blank" rel="noopener noreferrer">{{ shortText(entry.title) }}</a>
          </td>
          <td :class="statusClass(entry.status)">{{ entry.status_display }}</td>
          <td>
            <span v-if="entry.content" v-tooltip="entry.content">{{ shortText(entry.content) }}</span>
          </td>
          <td>{{ entry.type }}</td>
          <td>{{ entry.reviewer_username }}</td>
          <td>{{ entry.formatted_created_at }}</td>
          <td :class="entry.describer_username === username ? 'table-success' : ''">{{ entry.describer_username }}</td>
          <td></td>
        </tr>
      </tbody>
    </table>

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

const entries = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const totalPages = ref(1)
const query = ref('')
const inputPage = ref(1)
const username = ref('Admin')
const adminFlag = ref(true)
const editorFlag = ref(true)
const message = ref('')
const link = ref('')
const sortField = ref('created_at')
const sortOrder = ref('desc')

function shortText(text) {
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

// 示例 API 请求函数
async function fetchEntries() {
  const res = await fetch(`/api/entries?page=${page.value}&page_size=${pageSize.value}&q=${query.value}&sort=${sortField.value}&order=${sortOrder.value}`)
  const data = await res.json()
  entries.value = data.entries
  total.value = data.total
  totalPages.value = data.total_pages
}

function changeSort(field, order) {
  sortField.value = field
  sortOrder.value = order
  fetchEntries()
}

function goPage(p) {
  page.value = p
}

onMounted(fetchEntries)
watch([page, pageSize], fetchEntries)

// 模拟按钮事件
function goAdmin() { console.log('goAdmin') }
function logout() { console.log('logout') }
function preview() { console.log('preview') }
function uploadText() { console.log('uploadText') }
function publish() { console.log('publish') }
function addLink() { console.log('addLink', link.value) }
function onFileChange(e) { console.log('file', e.target.files[0]) }
function uploadImage() { console.log('uploadImage') }
function edit(id) { console.log('edit', id) }
function review(id) { console.log('review', id) }
function deleteEntry(id) { console.log('delete', id) }

// 计算附近页码
const nearbyPages = computed(() => {
  const pages = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, page.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})
</script>

<style scoped>
.table-hover th, .table-hover td {
  vertical-align: middle;
}
</style>
