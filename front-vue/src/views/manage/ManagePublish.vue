<template>
  <div class="publish-container">
    <!-- 左侧：操作面板 -->
    <div class="publish-sidebar">
      <h2>发布内容</h2>

      <!-- 提示信息 -->
      <div v-if="message" :class="['alert', messageClass]">
        {{ message }}
      </div>

      <!-- 日期范围选择和操作 -->
      <div class="manage-form-card">
        <div class="d-flex gap-2 flex-column">
          <div class="date-range-row">
            <div class="form-group mb-0">
              <label class="form-label">开始日期</label>
              <input
                v-model="startDate"
                type="date"
                class="form-control"
              />
            </div>
            <div class="form-group mb-0">
              <label class="form-label">结束日期</label>
              <input
                v-model="endDate"
                type="date"
                class="form-control"
                @change="checkArchivedPDF(endDate)"
              />
            </div>
          </div>
          <button
            type="button"
            class="btn btn-outline-primary"
            @click="loadPublishedContent"
            :disabled="isLoadingPublished"
          >
            查询/刷新内容
          </button>
        </div>
      </div>

      <!-- PDF操作 -->
      <div class="manage-form-card">
        <div class="d-flex gap-2 flex-column">
          <button
            type="button"
            class="btn btn-primary"
            @click="generatePDF"
            :disabled="isGeneratingPDF"
          >
            {{ isGeneratingPDF ? '生成中...' : '生成选中PDF' }}
          </button>
          <div class="d-flex gap-2">
            <button
              v-if="pdfExists"
              type="button"
              class="btn btn-success"
              @click="downloadPDF"
            >
              下载PDF
            </button>
            <button
              v-if="pdfExists"
              type="button"
              class="btn btn-outline-warning"
              @click="refreshPDF"
            >
              刷新PDF
            </button>
          </div>
        </div>
      </div>

      <!-- DDL内容 -->
      <div class="manage-form-card" v-if="ddlContent.length > 0">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h3>DDL内容 ({{ ddlContent.length }}条)</h3>
          <span class="text-muted">已选中: {{ selectedDDLIds.length }}条</span>
        </div>

        <div class="d-flex gap-2 mb-3">
          <button
            type="button"
            class="btn btn-sm btn-outline-primary"
            @click="selectAllDDL"
          >
            全选
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            @click="selectNoneDDL"
          >
            取消全选
          </button>
        </div>

        <div class="list-group">
          <div
            v-for="item in ddlContent"
            :key="item.id"
            class="list-group-item"
          >
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <input
                  type="checkbox"
                  :value="item.id"
                  v-model="selectedDDLIds"
                  class="me-2"
                  :id="'ddl-select-' + item.id"
                />
                <label :for="'ddl-select-' + item.id" class="fw-bold">
                  {{ item.title }}
                </label>
              </div>
              <div>
                <span class="badge badge-primary">{{ item.category }}</span>
              </div>
            </div>
            <div class="mt-2 text-muted small">
              截止时间：{{ formatDDLTime(item.due_time) }}
            </div>
            <div class="text-muted small">
              刊载时间：{{ formatPublishTime(item.publish_date) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 已发布内容 -->
      <div class="manage-form-card" v-if="publishedContent.length > 0">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h3>已发布内容 ({{ publishedContent.length }}条)</h3>
          <span class="text-muted">已选中: {{ selectedContentIds.length }}条</span>
        </div>

        <div class="d-flex gap-2 mb-3">
          <button
            type="button"
            class="btn btn-sm btn-outline-primary"
            @click="selectAll"
          >
            全选
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            @click="selectNone"
          >
            取消全选
          </button>
        </div>

        <div class="list-group">
          <div
            v-for="item in publishedContent"
            :key="item.id"
            class="list-group-item"
          >
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <input
                  type="checkbox"
                  :value="item.id"
                  v-model="selectedContentIds"
                  class="me-2"
                  :id="'select-' + item.id"
                />
                <label :for="'select-' + item.id" class="fw-bold">
                  {{ item.title }}
                </label>
              </div>
              <div>
                <span class="badge badge-primary me-2">{{ item.type }}</span>
                <span class="badge badge-secondary">{{ item.tag }}</span>
              </div>
            </div>
            <div class="mt-2 text-muted small">
              发布时间：{{ formatPublishTime(item.publish_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="manage-form-card" v-else-if="!isLoadingPublished">
        <EmptyState
          icon="📋"
          title="没有已发布的内容"
          :description="startDate && endDate ? `该日期范围内没有已发布的内容` : '请先选择日期范围'"
        />
      </div>

      <button
        type="button"
        class="btn btn-secondary mt-3"
        @click="goBack"
      >
        返回
      </button>
    </div>

    <!-- 右侧：PDF预览 -->
    <div class="pdf-preview-container">
      <div v-if="pdfExists" class="pdf-frame-wrapper">
        <iframe
          :key="pdfTimestamp"
          :src="fullPdfUrl"
          class="pdf-iframe"
          frameborder="0"
        ></iframe>
      </div>
      <EmptyState
        v-else
        icon="📄"
        title="暂无PDF预览"
        :description="startDate && endDate ? `请选择内容后生成 ${startDate} 至 ${endDate} 的PDF，或查看归档的PDF文件` : '请先选择日期范围'"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  queryPublishedByDateRange,
  queryDDLByDate,
  generatePDF as generatePDFAPI
} from '../../api/publish.js'
import EmptyState from '../../components/EmptyState.vue'

const router = useRouter()

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:42611/api'

// 日期范围选择
const startDate = ref(new Date().toISOString().split('T')[0])
const endDate = ref(new Date().toISOString().split('T')[0])

// 数据
const publishedContent = ref([])
const selectedContentIds = ref([])

// DDL内容数据
const ddlContent = ref([])
const selectedDDLIds = ref([])

// PDF相关
const pdfExists = ref(false)
const pdfUrl = ref('')
const pdfTimestamp = ref(0)

// 计算完整的PDF URL（添加时间戳以刷新缓存）
const fullPdfUrl = computed(() => {
  if (pdfUrl.value) {
    const baseUrl = API_BASE_URL.replace('/api', '')
    return `${baseUrl}${pdfUrl.value}?t=${pdfTimestamp.value}`
  }
  return ''
})

// 检查归档 PDF 是否存在
async function checkArchivedPDF(date) {
  const baseUrl = API_BASE_URL.replace('/api', '')
  const archivedUrl = `/static/pdfs/${date}.pdf`

  try {
    // 尝试发送 HEAD 请求检查文件是否存在
    const response = await fetch(`${baseUrl}${archivedUrl}`, { method: 'HEAD' })
    if (response.ok) {
      pdfUrl.value = archivedUrl
      pdfExists.value = true
    }
  } catch (err) {
    // 文件不存在或其他错误，保持 pdfExists = false
    console.log('归档PDF不存在，将显示空状态')
  }
}

// 状态
const message = ref('')
const messageClass = ref('alert-info')
const isLoadingPublished = ref(false)
const isGeneratingPDF = ref(false)

// 加载已发布内容（支持日期范围）
async function loadPublishedContent() {
  if (!startDate.value || !endDate.value) {
    showMessage('请选择开始日期和结束日期', 'alert-warning')
    return
  }

  if (startDate.value > endDate.value) {
    showMessage('开始日期不能晚于结束日期', 'alert-warning')
    return
  }

  isLoadingPublished.value = true
  try {
    // 并行请求已发布内容和DDL内容
    const [publishedData, ddlData] = await Promise.all([
      queryPublishedByDateRange(startDate.value, endDate.value),
      queryDDLByDate(endDate.value)
    ])

    // 适配新的返回格式
    publishedContent.value = publishedData.results || []
    selectedContentIds.value = publishedContent.value.map(e => e.id)

    // DDL 内容（后端已分类）
    ddlContent.value = ddlData.results || []
    selectedDDLIds.value = ddlContent.value.map(e => e.id)

    showMessage(`找到 ${publishedData.count} 条已发布内容，${ddlData.count} 条DDL内容`, 'alert-info')
  } catch (err) {
    publishedContent.value = []
    ddlContent.value = []
    pdfExists.value = false
    showMessage('查询失败：' + err.message, 'alert-danger')
  } finally {
    isLoadingPublished.value = false
  }
}

// 全选
function selectAll() {
  selectedContentIds.value = publishedContent.value.map(e => e.id)
}

// 取消全选
function selectNone() {
  selectedContentIds.value = []
}

// 全选DDL
function selectAllDDL() {
  selectedDDLIds.value = ddlContent.value.map(e => e.id)
}

// 取消全选DDL
function selectNoneDDL() {
  selectedDDLIds.value = []
}

// 生成PDF（基于选中的内容和日期范围）
async function generatePDF() {
  // 检查是否至少选中了普通内容或 DDL 内容
  const hasSelectedContent = selectedContentIds.value.length > 0
  const hasSelectedDDL = selectedDDLIds.value.length > 0

  if (!hasSelectedContent && !hasSelectedDDL) {
    showMessage('请至少选择一条内容或DDL', 'alert-warning')
    return
  }

  isGeneratingPDF.value = true
  try {
    // 如果只选中了 DDL 内容，只传递 date 参数，让后端自动查询
    // 如果选中了普通内容，传递 content_ids 和 date
    const params = hasSelectedContent
      ? { content_ids: selectedContentIds.value, date: endDate.value }
      : { date: endDate.value }

    const result = await generatePDFAPI(params)
    if (result.success) {
      // 更新DDL内容（使用后端返回的实际DDL）
      if (result.due_contents) {
        // 扁平化due_contents对象中的所有分类
        const allDue = []
        const categories = ['other', 'lecture', 'college', 'club']
        for (const cat of categories) {
          if (result.due_contents[cat]) {
            allDue.push(...result.due_contents[cat])
          }
        }
        ddlContent.value = allDue
        selectedDDLIds.value = allDue.map(e => e.id)
        showMessage(`PDF生成成功！共包含 ${result.count} 条内容，${allDue.length} 条DDL内容`, 'alert-success')
      } else {
        showMessage(`PDF生成成功！共包含 ${result.count} 条内容`, 'alert-success')
      }
      pdfExists.value = true
      pdfUrl.value = result.pdf_url
      // 更新时间戳以刷新iframe
      pdfTimestamp.value = Date.now()
    } else {
      showMessage('PDF生成失败：' + result.message, 'alert-danger')
    }
  } catch (err) {
    showMessage('PDF生成失败：' + (err.response?.data?.message || err.message), 'alert-danger')
  } finally {
    isGeneratingPDF.value = false
  }
}

// 下载PDF
function downloadPDF() {
  if (pdfUrl.value) {
    window.open(fullPdfUrl.value, '_blank')
  }
}

// 刷新PDF（更新时间戳）
function refreshPDF() {
  pdfTimestamp.value = Date.now()
  showMessage('PDF已刷新', 'alert-info')
}

// 返回
function goBack() {
  router.back()
}

// 显示消息
function showMessage(msg, cls = 'alert-info') {
  message.value = msg
  messageClass.value = cls
  setTimeout(() => { message.value = '' }, 5000)
}

// 格式化发布时间
function formatPublishTime(timeStr) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化DDL时间
function formatDDLTime(timeStr) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadPublishedContent()
  // 检查当天的归档 PDF
  checkArchivedPDF(endDate.value)
})
</script>

<style scoped>
@import '../../styles/layout.css';
@import '../../styles/utilities.css';
@import '../../styles/buttons.css';
@import '../../styles/forms.css';
@import '../../styles/alerts.css';
@import '../../styles/manage.css';

/* 布局容器 */
.publish-container {
  display: flex;
  min-height: 100vh;
  gap: 1rem;
}

/* 左侧操作面板 */
.publish-sidebar {
  width: 450px;
  min-width: 450px;
  padding: 1rem;
  overflow-y: auto;
  background-color: #f5f5f5;
}

/* 右侧PDF预览 */
.pdf-preview-container {
  flex: 1;
  height: 100vh;
  position: sticky;
  top: 0;
  background-color: #fff;
}

.pdf-frame-wrapper {
  width: 100%;
  height: 100%;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

h3 {
  margin: 0 0 1rem 0;
  color: #555;
  font-size: 1.1rem;
}

/* 日期范围行 */
.date-range-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.date-range-row .form-group {
  flex: 1;
  min-width: 140px;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

input[type="checkbox"] + label {
  cursor: pointer;
  display: inline;
  margin-bottom: 0;
}

.small {
  font-size: 0.875rem;
}

.btn {
  min-width: 100px;
}

.ms-3 {
  margin-left: 1rem;
}

.me-2 {
  margin-right: 0.5rem;
}

.mt-3 {
  margin-top: 1rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

.gap-2 {
  gap: 0.5rem;
}

.d-flex {
  display: flex;
}

.justify-content-between {
  justify-content: space-between;
}

.align-items-center {
  align-items: center;
}

.align-items-start {
  align-items: flex-start;
}

.badge {
  display: inline-block;
  padding: 0.25em 0.5em;
  font-size: 0.75em;
  font-weight: 700;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
}

.badge-primary {
  background-color: #0d6efd;
  color: #fff;
}

.badge-secondary {
  background-color: #6c757d;
  color: #fff;
}

/* 响应式布局 */
@media (max-width: 1024px) {
  .publish-container {
    flex-direction: column;
  }

  .publish-sidebar {
    width: 100%;
    min-width: unset;
    height: auto;
  }

  .pdf-preview-container {
    height: 60vh;
    position: relative;
    top: 0;
  }

  .date-range-row {
    flex-direction: column;
  }

  .date-range-row .form-group {
    min-width: unset;
  }
}
</style>
