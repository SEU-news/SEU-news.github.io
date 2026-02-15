<template>
  <div class="manage-page">
    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]" class="mb-3">
      {{ message }}
    </div>

    <!-- 操作按钮区 -->
    <div class="manage-actions">
      <div class="text-muted">
        共 {{ total }} 条{{ query ? '（包含过滤结果）' : '' }}
      </div>
      <div>
        <!-- <button class="btn btn-outline-primary" @click="handlePreview">预览</button> -->
        <button v-if="editorFlag" class="btn btn-success" @click="goPublish">发布</button>
      </div>
    </div>

    <!-- 快速上传卡片（可折叠） -->
    <div class="collapsible-upload-card">
      <div class="collapsible-header" @click="toggleUploadPanel">
        <div class="header-left">
          <span class="collapse-icon">{{ isUploadPanelOpen ? '▲' : '▼' }}</span>
          <span class="header-text">快速上传</span>
        </div>
        <span class="header-hint">文本 · URL · 图片</span>
      </div>

      <div v-if="isUploadPanelOpen" class="collapsible-content">
        <!-- 标签页导航 -->
        <div class="upload-tabs">
          <button v-for="tab in uploadTabs" :key="tab.id" :class="['tab-button', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id">
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <!-- 标签页内容 -->
        <div class="tab-content">
          <!-- 纯文本消息表单 -->
          <div v-show="activeTab === 'text'" class="tab-pane">
            <form @submit.prevent="handleUploadText">
              <div class="form-row">
                <div class="form-group flex-grow">
                  <label class="form-label">标题 <span class="required-mark">*</span></label>
                  <input type="text" class="form-control" v-model="textForm.title" placeholder="请输入标题" required
                    maxlength="200" />
                </div>
                <div class="form-group type-select">
                  <label class="form-label">类型 <span class="required-mark">*</span></label>
                  <select v-model="textForm.type" class="form-control" required>
                    <option value="">选择类型</option>
                    <option value="教务">教务</option>
                    <option value="科研">科研</option>
                    <option value="活动">活动</option>
                    <option value="通知">通知</option>
                    <option value="招聘">招聘</option>
                    <option value="其他">其他</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">链接 <span class="required-mark">*</span></label>
                <div class="input-with-icon">
                  <span class="input-icon">🔗</span>
                  <input type="url" class="form-control" v-model="textForm.link" placeholder="https://example.com"
                    required />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">内容 <span class="required-mark">*</span></label>
                <textarea class="form-control" v-model="textForm.content" rows="4" placeholder="请输入内容描述..."></textarea>
              </div>
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="resetTextForm">重置</button>
                <button type="submit" class="btn btn-primary">
                  <span class="btn-icon">📤</span> 上传
                </button>
              </div>
            </form>
          </div>

          <!-- URL 粘贴表单 -->
          <div v-show="activeTab === 'url'" class="tab-pane">
            <form @submit.prevent="handlePasteUrl">
              <div class="url-upload-container">
                <div class="upload-icon">🔗</div>
                <div class="upload-content">
                  <h3 class="upload-title">快速添加链接</h3>
                  <p class="upload-desc">粘贴 URL 即可快速创建内容项</p>
                  <div class="input-with-icon">
                    <span class="input-icon">🌐</span>
                    <input type="url" class="form-control" v-model="urlForm.url" placeholder="https://..." required />
                  </div>
                  <button type="submit" class="btn btn-primary btn-lg">
                    <span class="btn-icon">➕</span> 添加 URL
                  </button>
                </div>
              </div>
            </form>
          </div>

          <!-- 图片上传表单 -->
          <div v-show="activeTab === 'image'" class="tab-pane">
            <form @submit.prevent="handleUploadImages">
              <div class="image-upload-container"
                :class="{ 'has-files': selectedImages.length > 0, 'drag-over': isDragOver }"
                @dragover.prevent="isDragOver = true" @dragleave.prevent="isDragOver = false"
                @drop.prevent="handleDrop">
                <div class="upload-area" @click="$refs.imageInput.click()">
                  <div class="upload-icon">📷</div>
                  <h3 class="upload-title">{{ selectedImages.length > 0 ? '继续选择' : '点击或拖拽上传图片' }}</h3>
                  <p class="upload-desc">支持 JPG、PNG、GIF 格式，可一次选择多张</p>
                  <input ref="imageInput" type="file" class="file-input" @change="onImagesChange" accept="image/*"
                    multiple />
                </div>
              </div>

              <!-- 已选图片预览 -->
              <div v-if="selectedImages.length > 0" class="selected-images-preview">
                <div class="preview-header">
                  <span class="preview-title">已选择 {{ selectedImages.length }} 张图片</span>
                  <button type="button" class="btn btn-sm btn-danger" @click="clearSelectedImages">清空</button>
                </div>
                <div class="preview-grid">
                  <div v-for="(file, index) in selectedImages.slice(0, 6)" :key="index" class="preview-item">
                    <img :src="getImagePreview(file)" :alt="file.name" />
                    <button type="button" class="remove-btn" @click="removeImage(index)">✕</button>
                  </div>
                  <div v-if="selectedImages.length > 6" class="preview-item more-items">
                    <span>+{{ selectedImages.length - 6 }}</span>
                  </div>
                </div>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="clearSelectedImages">清空</button>
                <button type="submit" class="btn btn-primary" :disabled="selectedImages.length === 0">
                  <span class="btn-icon">🖼️</span> 上传 {{ selectedImages.length }} 张图片
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <LoadingSpinner v-if="isLoading" />

    <!-- 空状态 -->
    <EmptyState v-else-if="entries.length === 0" icon="📝" title="暂无内容" description="请先上传内容" />

    <!-- 表格 -->
    <div v-else class="table-responsive">
      <!-- 搜索工具栏 -->
      <div class="search-toolbar">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input v-model="query" class="search-input" placeholder="搜索内容..." @keyup.enter="fetchEntries" />
        </div>
      </div>
      <table class="table table-hover fixed-table">
        <thead>
          <tr>
            <th>编号</th>
            <th>标题</th>
            <th>状态</th>
            <th>刊载版块</th>
            <th>上工者</th>
            <th>锁定者</th>
            <th>审核人</th>
            <th @click="toggleSort('created_at', fetchEntries)" class="sortable-header"
              :class="{ active: isSortedBy('created_at') }">
              <span class="header-content">上传时间</span>
              <span class="sort-icon" v-html="getSortIcon('created_at')"></span>
            </th>
            <th>截止时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(entry, index) in entries" :key="entry.id">
            <td>{{ entry.id }}</td>
            <td><a :href="entry.link" target="_blank" rel="noopener noreferrer">{{ shortText(entry.title) }}</a></td>
            <td>
              <StatusBadge :status="entry.status" size="small" />
            </td>
            <td>{{ entry.type }}</td>
            <td :class="entry.describer_username === username ? 'highlight' : ''">{{ entry.describer_username }}</td>
            <td></td>
            <td>{{ entry.reviewer_username }}</td>
            <td class="time-cell">{{ entry.formatted_created_at || '-' }}</td>
            <td class="time-cell">{{ entry.formatted_deadline || '未设置' }}</td>
            <td class="actions-cell">
              <!-- 预览按钮 -->
              <button class="preview-btn" @click="handlePreview(entry)" title="预览内容">
                <span class="preview-icon">👁️</span>
                <span class="preview-label">预览</span>
              </button>
              <!-- 操作下拉菜单 -->
              <ActionsDropdown :entry-id="entry.id" :status="entry.status" :creator-username="entry.creator_username"
                :editor-flag="editorFlag" :current-username="username" :entry-data="entry"
                @action-complete="fetchEntries" @edit="openEditModal" @review="openReviewModal" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <Pagination :page="page" :page-size="pageSize" :total-count="total" :total-pages="totalPages"
      :show-page-size-selector="true" @page-change="page = $event" @page-size-change="pageSize = $event" />

    <!-- 编辑内容弹窗 -->
    <EditContentModal v-if="showEditModal" :entry-id="editEntryId" @updated="handleEditUpdated"
      @close="closeEditModal" />

    <!-- 审核内容弹窗 -->
    <ReviewContentModal v-if="showReviewModal" :entry-id="reviewEntryId" @reviewed="handleReviewComplete"
      @modify="handleReviewModify" @close="closeReviewModal" />

    <!-- 预览内容弹窗 -->
    <PreviewContentModal v-if="showPreviewModal" :entry-id="previewEntryId" @close="closePreviewModal" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getEntries, unifiedUpload } from '../../api/content.js'
import { logout } from '../../api/auth.js'
import { useAuthStore } from '../../stores/auth'
import { useTableSort } from '../../composables/useTableSort.js'
import LoadingSpinner from '../../components/admin/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import Pagination from '../../components/Pagination.vue'
import ActionsDropdown from '../../components/ActionsDropdown.vue'
import ReviewContentModal from '../../components/ReviewContentModal.vue'
import EditContentModal from '../../components/EditContentModal.vue'
import PreviewContentModal from '../../components/PreviewContentModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const { toggleSort, getSortIcon, isSortedBy, sortField, sortOrder } = useTableSort({ defaultField: 'created_at', defaultOrder: 'desc' })

// 数据
const entries = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const totalPages = ref(1)
const query = ref('')
const username = ref('')
const adminFlag = ref(false)
const editorFlag = ref(false)
const message = ref('')
const messageClass = ref('alert-info')
const isLoading = ref(false)
const isUploadPanelOpen = ref(false)

// 弹窗状态
const showEditModal = ref(false)
const showReviewModal = ref(false)
const showPreviewModal = ref(false)
const editEntryId = ref(null)
const reviewEntryId = ref(null)
const previewEntryId = ref(null)

// 上传标签页
const activeTab = ref('text')
const isDragOver = ref(false)
const imageInput = ref(null)

// 上传标签页配置
const uploadTabs = [
  { id: 'text', label: '文本消息', icon: '📝' },
  { id: 'url', label: 'URL 粘贴', icon: '🔗' },
  { id: 'image', label: '图片上传', icon: '🖼️' },
]

// 表单数据
const textForm = ref({
  title: '',
  link: '',
  content: '',
  type: '',
})

const urlForm = ref({
  url: '',
})

const selectedImages = ref([])

// 工具函数
function shortText(text) {
  if (!text) return ''
  return text.length > 15 ? text.slice(0, 15) + '...' : text
}

// 获取条目列表
async function fetchEntries() {
  isLoading.value = true
  try {
    const data = await getEntries({
      page: page.value,
      page_size: pageSize.value,
      q: query.value,
      sort: sortField.value,
      order: sortOrder.value,
    })

    entries.value = data.results || []
    total.value = data.count || 0
    totalPages.value = data.total_pages || 1
  } catch (err) {
    showMessage('加载失败：' + err.message, 'alert-danger')
  } finally {
    isLoading.value = false
  }
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

function goPublish() {
  router.push('/manage/publish')
}

async function handleLogout() {
  try {
    await logout()
    authStore.clearUser()
    localStorage.removeItem('token')
    router.push('/')
  } catch (err) {
    showMessage('登出失败：' + err.message, 'alert-danger')
  }
}

function handlePreview(entry) {
  previewEntryId.value = entry.id
  showPreviewModal.value = true
}

function toggleUploadPanel() {
  isUploadPanelOpen.value = !isUploadPanelOpen.value
}

// 打开编辑弹窗
function openEditModal(entryId) {
  editEntryId.value = entryId
  showEditModal.value = true
}

// 关闭编辑弹窗
function closeEditModal() {
  showEditModal.value = false
  editEntryId.value = null
}

// 处理编辑完成
function handleEditUpdated() {
  closeEditModal()
  fetchEntries()
  showMessage('修改已保存', 'alert-success')
}

// 打开审核弹窗
function openReviewModal(entryId) {
  reviewEntryId.value = entryId
  showReviewModal.value = true
}

// 关闭审核弹窗
function closeReviewModal() {
  showReviewModal.value = false
  reviewEntryId.value = null
}

// 处理审核完成
function handleReviewComplete() {
  closeReviewModal()
  fetchEntries()
  showMessage('审核已完成', 'alert-success')
}

// 处理审核中的修改内容
function handleReviewModify(entryId) {
  // 关闭审核弹窗，打开编辑弹窗
  closeReviewModal()
  openEditModal(entryId)
}

// 打开预览弹窗
function openPreviewModal(entryId) {
  previewEntryId.value = entryId
  showPreviewModal.value = true
}

// 关闭预览弹窗
function closePreviewModal() {
  showPreviewModal.value = false
  previewEntryId.value = null
}

// 纯文本消息上传
async function handleUploadText() {
  try {
    const formData = new FormData()
    formData.append('upload_type', 'text')
    formData.append('title', textForm.value.title)
    formData.append('link', textForm.value.link)
    formData.append('content', textForm.value.content)
    formData.append('type', textForm.value.type)

    await unifiedUpload(formData)
    showMessage('纯文本消息上传成功', 'alert-success')
    textForm.value = { title: '', link: '', content: '', type: '' }
    fetchEntries()
  } catch (err) {
    showMessage('上传失败：' + err.message, 'alert-danger')
  }
}

function resetTextForm() {
  textForm.value = { title: '', link: '', content: '', type: '' }
}

// URL 粘贴上传
async function handlePasteUrl() {
  try {
    const formData = new FormData()
    formData.append('upload_type', 'url')
    formData.append('url', urlForm.value.url)

    await unifiedUpload(formData)
    showMessage('URL 添加成功', 'alert-success')
    urlForm.value.url = ''
    fetchEntries()
  } catch (err) {
    showMessage('URL 添加失败：' + err.message, 'alert-danger')
  }
}

// 图片上传（支持多图）
function onImagesChange(e) {
  const files = Array.from(e.target.files)
  selectedImages.value = [...selectedImages.value, ...files]
  isDragOver.value = false
}

function handleDrop(e) {
  isDragOver.value = false
  const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
  if (files.length > 0) {
    selectedImages.value = [...selectedImages.value, ...files]
  }
}

function getImagePreview(file) {
  return URL.createObjectURL(file)
}

function removeImage(index) {
  selectedImages.value = selectedImages.value.filter((_, i) => i !== index)
}

function clearSelectedImages() {
  selectedImages.value = []
}

async function handleUploadImages() {
  if (selectedImages.value.length === 0) return

  try {
    const formData = new FormData()
    formData.append('upload_type', 'image')

    // 添加所有图片文件
    selectedImages.value.forEach(file => {
      formData.append('images', file)
    })

    await unifiedUpload(formData)
    showMessage(`成功上传 ${selectedImages.value.length} 张图片`, 'alert-success')
    selectedImages.value = []
    fetchEntries()
  } catch (err) {
    showMessage('图片上传失败：' + err.message, 'alert-danger')
  }
}

onMounted(() => {
  username.value = authStore.user.username || ''
  adminFlag.value = authStore.hasAdminPerm || false
  editorFlag.value = authStore.hasEditorPerm || false

  fetchEntries()
})

watch([page, pageSize], fetchEntries)
</script>

<style scoped>
@import '../../styles/layout.css';
@import '../../styles/utilities.css';
@import '../../styles/buttons.css';
@import '../../styles/forms.css';
@import '../../styles/tables.css';
@import '../../styles/alerts.css';
@import '../../styles/manage.css';

.table-hover th,
.table-hover td {
  vertical-align: middle;
}

/* 编号列宽度控制 */
thead th:nth-child(1),
tbody td:nth-child(1) {
  width: 60px;
  min-width: 60px;
  max-width: 60px;
}

/* 上工者列最小宽度 */
thead th:nth-child(5),
tbody td:nth-child(5) {
  min-width: 80px;
}

/* 锁定者列最小宽度 */
thead th:nth-child(6),
tbody td:nth-child(6) {
  min-width: 80px;
}

/* 审核人列最小宽度 */
thead th:nth-child(7),
tbody td:nth-child(7) {
  min-width: 80px;
}

/* 表头居中（排除标题） */
thead th:nth-child(1),
thead th:nth-child(3),
thead th:nth-child(4),
thead th:nth-child(5),
thead th:nth-child(6),
thead th:nth-child(7),
thead th:nth-child(8),
thead th:nth-child(9),
thead th:nth-child(10) {
  text-align: center;
}

/* 表格内容居中（排除标题） */
tbody td:nth-child(1),
tbody td:nth-child(3),
tbody td:nth-child(4),
tbody td:nth-child(5),
tbody td:nth-child(6),
tbody td:nth-child(7),
tbody td:nth-child(8),
tbody td:nth-child(9),
tbody td:nth-child(10) {
  text-align: center;
}

/* 时间单元格样式 - 防止换行 */
.time-cell {
  white-space: nowrap;
}

.me-2 {
  margin-right: 0.5rem;
}

/* ==================== 快速上传优化样式 ==================== */

/* 折叠标题栏优化 */
.collapsible-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-hint {
  font-size: 0.85rem;
  letter-spacing: 0.05em;
}

/* 标签页导航 */
.upload-tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: #f1f3f4;
  border-radius: 8px;
  margin-bottom: 20px;
}

.tab-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-button:hover {
  background: rgba(102, 126, 234, 0.08);
  color: #2c3e50;
}

.tab-button.active {
  background: white;
  color: #667eea;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tab-icon {
  font-size: 1.1rem;
}

.tab-label {
  font-size: 0.9rem;
}

/* 标签页内容 */
.tab-content {
  min-height: 300px;
}

.tab-pane {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

/* 文本表单布局 */
.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-row .type-select {
  flex: 0 0 140px;
}

@media (max-width: 640px) {
  .form-row {
    flex-direction: column;
  }

  .form-row .type-select {
    flex: 1;
  }
}

/* 带图标的输入框 */
.input-with-icon {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  pointer-events: none;
}

.input-with-icon .form-control {
  padding-left: 40px;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.btn-icon {
  margin-right: 4px;
}

.btn-lg {
  padding: 10px 24px;
  font-size: 1rem;
}

/* URL 上传容器 */
.url-upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.8;
}

.upload-title {
  margin: 0 0 8px;
  font-size: 1.1rem;
  color: #2c3e50;
}

.upload-desc {
  margin: 0 0 20px;
  color: #6c757d;
  font-size: 0.9rem;
}

.upload-content {
  text-align: center;
  width: 100%;
  max-width: 500px;
}

.upload-content .form-control {
  margin-bottom: 16px;
}

/* 图片上传容器 */
.image-upload-container {
  border: 2px dashed #dee2e6;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 20px;
}

.image-upload-container:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.02);
}

.image-upload-container.drag-over {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  transform: scale(1.01);
}

.upload-area {
  pointer-events: none;
}

.image-upload-container .upload-icon {
  font-size: 4rem;
  opacity: 0.6;
}

.image-upload-container .upload-title {
  font-size: 1rem;
  margin-bottom: 8px;
}

.image-upload-container .upload-desc {
  font-size: 0.875rem;
  margin-bottom: 0;
}

.file-input {
  display: none;
}

/* 图片预览 */
.selected-images-preview {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-title {
  font-size: 0.875rem;
  color: #6c757d;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: #e9ecef;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-item .remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  padding: 0;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 50%;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.preview-item:hover .remove-btn {
  opacity: 1;
}

.preview-item.more-items {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #dee2e6;
  color: #6c757d;
  font-weight: 500;
  font-size: 0.9rem;
}

/* 小按钮 */
.btn-sm {
  padding: 4px 12px;
  font-size: 0.8rem;
}

/* 禁用状态 */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 改进的下拉选择框 */
select.form-control {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='%236c757d' d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 12px;
  padding-right: 36px;
}

/* ==================== 预览按钮样式 ==================== */
.actions-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.preview-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 36px;
  padding: 0 20px;
  min-width: 100px;
  border: 1.5px solid rgba(23, 162, 184, 0.2);
  border-radius: 6px;
  background: rgba(23, 162, 184, 0.08);
  color: #17a2b8;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.preview-icon {
  font-size: 1rem;
}

.preview-label {
  font-size: 0.8125rem;
}

.preview-btn:hover {
  background: rgba(23, 162, 184, 0.12);
  border-color: rgba(23, 162, 184, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(23, 162, 184, 0.15);
}

.preview-btn:active {
  transform: translateY(0);
}
</style>
