<template>
  <div>
    <div class="admin-header">
      <h2>条目管理</h2>
      <p>管理系统所有内容条目</p>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-spinner">
      <span>加载中...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="entries.length === 0" class="empty-state">
      <i>📝</i>
      <h3>暂无条目</h3>
      <p>系统中还没有内容条目</p>
    </div>

    <!-- 表格 -->
    <div v-else class="table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th @click="toggleSort('id')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'id' }">
              <span class="header-content">
                ID
                <span class="sort-icon" v-html="getSortIcon('id')"></span>
              </span>
            </th>
            <th>标题</th>
            <th>状态</th>
            <!-- <th>描述</th> -->
            <th>刊载版块</th>
            <th>上工人</th>
            <th>审阅人</th>
            <th @click="toggleSort('created_at')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'created_at' }">
              <span class="header-content">
                上传时间
                <span class="sort-icon" v-html="getSortIcon('created_at')"></span>
              </span>
            </th>
            <th @click="toggleSort('deadline')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'deadline' }">
              <span class="header-content">
                截止时间
                <span class="sort-icon" v-html="getSortIcon('deadline')"></span>
              </span>
            </th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in entries" :key="entry.id">
            <td class="text-center">{{ entry.id }}</td>
            <td class="title-cell">
              <a :href="entry.link" target="_blank" rel="noopener noreferrer" :title="entry.title">{{ entry.title }}</a>
            </td>
            <td class="status-cell">
  <span class="status-badge" :style="{ backgroundColor: getStatusConfig(entry.status).color + '15', color: getStatusConfig(entry.status).color }">
    <span class="status-icon">{{ getStatusConfig(entry.status).icon }}</span>
    <span class="status-label">{{ getStatusConfig(entry.status).label }}</span>
  </span>
</td>
            <!-- <td>{{ shortText(entry.content) }}</td> -->
            <td>{{ entry.type }}</td>
            <td>{{ entry.describer_username }}</td>
            <td>{{ entry.reviewer_username }}</td>
            <td class="time-cell">
              <!-- <span class="time-icon">📅</span> -->
              <span class="time-text">{{ entry.formatted_created_at || '-' }}</span>
            </td>
            <td class="time-cell">
              <!-- <span class="time-icon">⏰</span> -->
              <span class="time-text">{{ entry.formatted_deadline || '未设置' }}</span>
            </td>
            <td class="actions-cell">
              <StatusDropdown :entry-id="entry.id" :current-status="entry.status" @status-changed="fetchEntries" />
              <DeadlineDropdown :entry-id="entry.id" :current-deadline="entry.deadline" :formatted-deadline="entry.formatted_deadline" @deadline-changed="fetchEntries" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <Pagination
      v-if="entries.length > 0"
      :page="page"
      :page-size="pageSize"
      :total-count="totalCount"
      :total-pages="totalPages"
      :page-size-options="pageSizeOptions"
      @page-change="page = $event"
      @page-size-change="handlePageSizeChange"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getEntries } from '../../api/content'
import StatusDropdown from '../../components/StatusDropdown.vue'
import DeadlineDropdown from '../../components/DeadlineDropdown.vue'
import Pagination from '../../components/Pagination.vue'

const entries = ref([])
const message = ref('')
const page = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 20, 50, 100]
const totalPages = ref(1)
const totalCount = ref(0)
const sortField = ref('created_at')
const sortOrder = ref('desc')
const loading = ref(false)

// 状态配置（与 StatusDropdown.vue 保持一致）
const statusConfig = {
  draft: { icon: '📝', label: '草稿', color: '#3498db' },
  pending: { icon: '⏳', label: '待审核', color: '#f39c12' },
  reviewed: { icon: '✅', label: '已审核', color: '#2ecc71' },
  rejected: { icon: '❌', label: '已拒绝', color: '#e74c3c' },
  published: { icon: '🚀', label: '已发布', color: '#9b59b6' },
  terminated: { icon: '🚫', label: '已终止', color: '#6c757d' }
}

// 获取状态配置的辅助函数
function getStatusConfig(status) {
  return statusConfig[status] || statusConfig.draft
}

async function fetchEntries() {
  try {
    loading.value = true
    const data = await getEntries({
      page: page.value,
      page_size: pageSize.value,
      sort: sortField.value,
      order: sortOrder.value
    })
    entries.value = data.results || []
    totalPages.value = data.total_pages || 1
    totalCount.value = data.count || 0
  } catch (error) {
    console.error('Failed to fetch entries:', error)
    message.value = '加载失败，请重试'
  } finally {
    loading.value = false
  }
}

function shortText(text) {
  if (!text) return ''
  return text.length > 15 ? text.slice(0, 15) + '...' : text
}

function changeSort(field, order) {
  sortField.value = field
  sortOrder.value = order
  fetchEntries()
}

function toggleSort(field) {
  if (sortField.value === field) {
    // 如果已经是当前排序列，切换排序方向
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    // 如果是新的排序列，使用降序（最新在前）
    sortField.value = field
    sortOrder.value = 'desc'
  }
  fetchEntries()
}

function getSortIcon(field) {
  if (sortField.value !== field) {
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 5L6 1L10 5" stroke="#adb5bd" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 11V1" stroke="#adb5bd" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  }
  if (sortOrder.value === 'asc') {
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 5L6 1L10 5" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 11V1" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  } else {
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 7L6 11L10 7" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 1V11" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  }
}

function handlePageSizeChange() {
  page.value = 1  // 重置到第一页
  fetchEntries()
}

onMounted(fetchEntries)
watch(page, fetchEntries)
watch(pageSize, handlePageSizeChange)
</script>

<style scoped>
@import '../../styles/admin.css';
@import '../../styles/tables.css';

/* 表格响应式容器 - 添加横向滚动 */
.table-responsive {
  overflow-x: auto;
  overflow-y: visible;
  -webkit-overflow-scrolling: touch; /* iOS 平滑滚动 */
}

/* 表格样式 */
.table {
  min-width: 100%; /* 确保表格占满容器 */
  border-collapse: separate;
  border-spacing: 0;
}

.table-hover th,
.table-hover td {
  vertical-align: middle;
}

/* 表格标题不换行 */
.table thead th {
  white-space: nowrap;
  text-align: center;
  vertical-align: bottom;
  position: sticky;
  top: 0;
  background-color: #f8f9fa;
  z-index: 10;
}

/* 表格单元格 */
.table tbody td {
  vertical-align: middle;
  text-align: center;
}

/* 标题列内容左对齐 */
.table tbody td:nth-child(2) {
  text-align: left;
}

/* 标题单元格 - 限制长度并显示省略号 */
.title-cell {
  max-width: 200px;
  min-width: 100px;
}

.title-cell a {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #667eea;
  text-decoration: none;
  transition: color 0.2s ease;
}

.title-cell a:hover {
  color: #5568d3;
  text-decoration: underline;
}

/* 时间单元格样式 */
.time-cell {
  white-space: nowrap;
}

.time-icon {
  margin-right: 6px;
  font-size: 1rem;
  display: inline-block;
  vertical-align: middle;
}

.time-text {
  display: inline-block;
  vertical-align: middle;
}

/* 操作列样式优化 */
.actions-cell {
  white-space: nowrap;
  min-width: 280px; /* 确保操作列有足够宽度显示两个按钮 */
}

.actions-cell > * {
  margin-right: 6px; /* 调整下拉按钮间距 */
}

.actions-cell > *:last-child {
  margin-right: 0;
}

/* 可排序的表头 */
.sortable-header {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
  position: relative;
  padding-right: 12px !important;
}

.sortable-header:hover {
  background-color: #e9ecef;
}

.sortable-header.active {
  color: #667eea;
  font-weight: 600;
}

.sortable-header .sort-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  opacity: 0.6;
}

.sortable-header:hover .sort-icon,
.sortable-header.active .sort-icon {
  opacity: 1;
}

/* Header content wrapper for proper alignment */
.header-content {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

/* 编号列居中 */
.table thead th.text-center {
  text-align: center !important;
}

.table tbody td.text-center {
  text-align: center !important;
}

/* 状态单元格 */
.status-cell {
  padding: 12px 16px;
}

/* 状态徽章 */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.status-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-icon {
  font-size: 1rem;
  line-height: 1;
}

.status-label {
  line-height: 1;
}
</style>
