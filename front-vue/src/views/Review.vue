<template>
  <div class="review-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>审核内容</h1>
    </div>

    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 主内容区 -->
    <div v-else class="main-content">
      <div class="content-card">
        <div class="card-header">
          <h2>内容详情</h2>
        </div>

        <div class="card-body">
          <table class="detail-table">
            <tr v-if="entryData.title">
              <th class="label">标题</th>
              <td class="value">{{ entryData.title }}</td>
            </tr>
            <tr v-if="entryData.short_title">
              <th class="label">短标题</th>
              <td class="value">{{ entryData.short_title }}</td>
            </tr>
            <tr v-if="entryData.type">
              <th class="label">类型</th>
              <td class="value">
                <span class="badge" :class="getTypeClass(entryData.type)">
                  {{ entryData.type }}
                </span>
              </td>
            </tr>
            <tr v-if="entryData.status">
              <th class="label">状态</th>
              <td class="value">
                <span class="badge" :class="getStatusClass(entryData.status)">
                  {{ entryData.status_display }}
                </span>
              </td>
            </tr>
            <tr v-if="entryData.creator_username">
              <th class="label">创建者</th>
              <td class="value">{{ entryData.creator_username }}</td>
            </tr>
            <tr v-if="entryData.describer_username">
              <th class="label">描述者</th>
              <td class="value">
                <span v-if="entryData.describer_username" class="highlight">{{ entryData.describer_username }}</span>
                <span v-else class="empty">未描述</span>
              </td>
            </tr>
            <tr>
              <th class="label">标签</th>
              <td class="value">
                <span v-if="displayTags" class="tags">{{ displayTags }}</span>
                <span v-else class="empty">无</span>
              </td>
            </tr>
            <tr v-if="entryData.deadline">
              <th class="label">截止日期</th>
              <td class="value">{{ entryData.deadline }}</td>
            </tr>
            <tr v-if="entryData.link">
              <th class="label">链接</th>
              <td class="value">
                <a :href="entryData.link" target="_blank" rel="noopener noreferrer" class="link">
                  {{ entryData.link }}
                </a>
              </td>
            </tr>
            <tr>
              <th class="label">上传时间</th>
              <td class="value">{{ entryData.formatted_created_at }}</td>
            </tr>
          </table>

          <div class="content-section">
            <h3>详细内容</h3>
            <div class="content-box">
              {{ entryData.content }}
            </div>
          </div>
        </div>
      </div>

      <!-- 审核表单 -->
      <div class="review-card">
        <div class="card-header">
          <h2>审核操作</h2>
        </div>

        <div class="card-body">
          <div class="form-group">
            <label>审核意见 <span class="required">*</span></label>
            <textarea
              v-model="reviewComment"
              class="form-control"
              rows="6"
              placeholder="请填写审核意见..."
            ></textarea>
          </div>

          <div class="action-buttons">
            <button
              type="button"
              class="btn btn-success"
              @click="handleApprove"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? '提交中...' : '通过审核' }}
            </button>
            <button
              type="button"
              class="btn btn-danger"
              @click="handleReject"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? '提交中...' : '拒绝' }}
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              @click="handleModify"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? '提交中...' : '修改内容' }}
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              @click="goBack"
            >
              返回
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getEntryDetail } from '../api/content.js'
import { reviewEntry, describeEntry } from '../api/review.js'

const router = useRouter()
const route = useRoute()
const entryId = route.params.id

// 数据
const entryData = ref({})
const reviewComment = ref('')
const displayTags = ref('')  // 用于显示的标签（逗号分隔）

// 状态
const message = ref('')
const messageClass = ref('alert-info')
const isLoading = ref(true)
const isSubmitting = ref(false)

// 加载条目详情
async function loadEntry() {
  try {
    const data = await getEntryDetail(entryId)
    entryData.value = data

    // 处理 tag：将 JSON 数组转换为逗号分隔的字符串用于显示
    if (data.tag) {
      try {
        const tagArray = JSON.parse(data.tag)
        if (Array.isArray(tagArray) && tagArray.length > 0) {
          displayTags.value = tagArray.join(', ')
        } else {
          displayTags.value = ''
        }
      } catch (e) {
        console.warn('Failed to parse tags:', e)
        displayTags.value = data.tag || ''
      }
    } else {
      displayTags.value = ''
    }
  } catch (err) {
    showMessage('加载失败：' + err.message, 'alert-danger')
  } finally {
    isLoading.value = false
  }
}

// 通过审核
async function handleApprove() {
  if (!reviewComment.value) {
    showMessage('请填写审核意见', 'alert-warning')
    return
  }

  isSubmitting.value = true
  message.value = ''

  try {
    await reviewEntry(entryId, {
      action: 'approve',
      comment: reviewComment.value,
    })

    alert('审核通过！')
    setTimeout(() => router.push('/manage'), 1500)
  } catch (err) {
    showMessage('审核失败：' + err.message, 'alert-danger')
  } finally {
    isSubmitting.value = false
  }
}

// 拒绝
async function handleReject() {
  if (!reviewComment.value) {
    showMessage('请填写审核意见', 'alert-warning')
    return
  }

  isSubmitting.value = true
  message.value = ''

  try {
    await reviewEntry(entryId, {
      action: 'reject',
      comment: reviewComment.value,
    })

    alert('已拒绝该内容')
    setTimeout(() => router.push('/manage'), 1500)
  } catch (err) {
    showMessage('操作失败：' + err.message, 'alert-danger')
  } finally {
    isSubmitting.value = false
  }
}

// 修改（跳转到描述页面）
function handleModify() {
  router.push(`/manage/describe/${entryId}`)
}

// 返回
function goBack() {
  router.back()
}

// 显示消息
function showMessage(msg, cls = 'alert-info') {
  message.value = msg
  messageClass.value = cls
  setTimeout(() => { message.value = '' }, 3000)
}

// 类型样式
function getTypeClass(type) {
  const classes = {
    '教务': 'type-primary',
    '科研': 'type-success',
    '活动': 'type-info',
    '通知': 'type-warning',
    '招聘': 'type-danger',
    '其他': 'type-secondary',
  }
  return classes[type] || 'type-secondary'
}

// 状态样式
function getStatusClass(status) {
  const classes = {
    'draft': 'status-info',
    'pending': 'status-secondary',
    'reviewed': 'status-success',
    'rejected': 'status-danger',
    'published': 'status-primary',
  }
  return classes[status] || 'status-secondary'
}

onMounted(loadEntry)
</script>

<style scoped>
/* 页面容器 - 简洁白色背景 */
.review-page {
  min-height: 100vh;
  background: #fafafa;
  padding: 2rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  color: #333;
  margin: 0;
  font-size: 2rem;
  font-weight: 400;
}

/* 主内容区 - 网格布局 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

/* 移动端适配 */
@media (max-width: 992px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

/* 卡片样式 - 简洁白色 */
.content-card,
.review-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e9ecef;
  overflow: hidden;
}

.card-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e9ecef;
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
  font-weight: 500;
}

.card-body {
  padding: 2rem;
}

/* 详情表格 - 简洁设计 */
.detail-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0;
}

.detail-table th.label {
  width: 140px;
  padding: 1rem;
  text-align: right;
  font-weight: 500;
  color: #666;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.detail-table td.value {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
  line-height: 1.8;
}

/* 徽章样式 - 柔和的圆角 */
.badge {
  padding: 0.3rem 0.8rem;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  display: inline-block;
}

/* 类型徽章颜色 - 柔和的 */
.type-primary { background: #667eea; color: white; }
.type-success { background: #28a745; color: white; }
.type-info { background: #17a2b8; color: white; }
.type-warning { background: #f59e0b; color: white; }
.type-danger { background: #dc3545; color: white; }
.type-secondary { background: #adb5bd; color: #666; }

/* 状态徽章颜色 - 柔和的 */
.status-primary { background: #667eea; color: white; }
.status-success { background: #28a745; color: white; }
.status-info { background: #17a2b8; color: white; }
.status-secondary { background: #adb5bd; color: white; }
.status-danger { background: #dc3545; color: white; }

/* 高亮和空值 */
.highlight {
  color: #28a745;
  font-weight: 600;
}

.empty {
  color: #adb5bd;
  font-style: italic;
}

/* 标签样式 */
.tags {
  color: #667eea;
  font-weight: 500;
}

/* 内容区域 */
.content-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e9ecef;
}

.content-section h3 {
  color: #333;
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 500;
}

.content-box {
  background: #fafafa;
  padding: 1.5rem;
  border-radius: 8px;
  line-height: 1.8;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
}

/* 链接样式 */
.link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.2s;
}

.link:hover {
  color: #4a55c6;
  text-decoration: underline;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #666;
}

.required {
  color: #dc3545;
  margin-left: 4px;
}

.form-control {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 2px 4px rgba(102, 126, 234, 0.1);
}

/* 按钮样式 - 柔和简约 */
.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  flex: 1;
  min-width: 120px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-success {
  background: #28a745;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.15);
}

.btn-danger {
  background: #dc3545;
}

.btn-danger:hover:not(:disabled) {
  background: #b71c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.15);
}

.btn-secondary {
  background: #6c757d;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(92, 107, 114, 0.1);
}

/* 提示信息样式 */
.alert {
  padding: 1rem 1.5rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  border-left: 4px solid;
}

.alert-info {
  background: #e3f2fd;
  border-left-color: #667eea;
  color: #1a56db;
}

.alert-warning {
  background: #fff3cd;
  border-left-color: #f59e0b;
  color: #b45309;
}

.alert-danger {
  background: #f8d7da;
  border-left-color: #dc3545;
  color: #721c24;
}

.alert-success {
  background: #d1e7dd;
  border-left-color: #28a745;
  color: #0f5132;
}

/* 加载动画 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
