<template>
  <div>
    <div class="admin-header">
      <h2>条目管理</h2>
      <p>管理系统所有内容条目</p>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Empty State -->
    <EmptyState
      v-else-if="entries.length === 0"
      icon="📝"
      title="暂无条目"
      description="系统中还没有内容条目"
    />

    <!-- 表格 -->
    <div v-else class="table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th @click="toggleSort('id', fetchEntries)" class="sortable-header sortable-header-center" :class="{ active: sortField === 'id' }">
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
            <th @click="toggleSort('created_at', fetchEntries)" class="sortable-header sortable-header-center" :class="{ active: sortField === 'created_at' }">
              <span class="header-content">
                上传时间
                <span class="sort-icon" v-html="getSortIcon('created_at')"></span>
              </span>
            </th>
            <th @click="toggleSort('deadline', fetchEntries)" class="sortable-header sortable-header-center" :class="{ active: sortField === 'deadline' }">
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
              <StatusBadge :status="entry.status" />
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
              <AdminStatusDropdown :entry-id="entry.id" :current-status="entry.status" @status-changed="fetchEntries" />
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
import AdminStatusDropdown from '../../components/AdminStatusDropdown.vue'
import DeadlineDropdown from '../../components/DeadlineDropdown.vue'
import Pagination from '../../components/Pagination.vue'
import { useTableSort } from '../../composables/useTableSort'

const entries = ref([])
const message = ref('')
const page = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 20, 50, 100]
const totalPages = ref(1)
const totalCount = ref(0)
const loading = ref(false)

// Use table sort composable
const { sortField, sortOrder, getSortIcon, toggleSort } = useTableSort({
  defaultField: 'created_at',
  defaultOrder: 'desc'
})

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
  // Use composable's setSort if needed
  sortField.value = field
  sortOrder.value = order
  fetchEntries()
}

function handleSortChange(field, order) {
  fetchEntries()
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
@import '../../styles/admin-components.css';

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

/* 操作列样式优化 */
.actions-cell {
  white-space: nowrap;
  min-width: 280px;
}

.actions-cell > * {
  margin-right: 6px;
}

.actions-cell > *:last-child {
  margin-right: 0;
}

/* 状态单元格 */
.status-cell {
  padding: 12px 16px;
}
</style>
