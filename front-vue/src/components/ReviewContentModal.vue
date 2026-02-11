<template>
  <teleport to="body">
    <div v-if="isOpen" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-content review-modal">
        <div class="modal-header">
          <h3>审核内容</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>

        <div class="modal-body">
          <LoadingSpinner v-if="isLoading" />

          <div v-else>
            <!-- 内容展示区域（参考 ManageReview 左侧卡片） -->
            <div class="content-preview-section">
              <table class="detail-table">
                <tbody>
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
                      <StatusBadge :status="entryData.status" size="medium" />
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
                      <span v-else class="empty-text">未描述</span>
                    </td>
                  </tr>
                  <tr>
                    <th class="label">标签</th>
                    <td class="value">
                      <span v-if="displayTags" class="tags">{{ displayTags }}</span>
                      <span v-else class="empty-text">无</span>
                    </td>
                  </tr>
                  <tr v-if="entryData.deadline">
                    <th class="label">截止日期</th>
                    <td class="value">{{ entryData.formatted_deadline }}</td>
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
                </tbody>
              </table>

              <div class="content-section">
                <h4>详细内容</h4>
                <div class="content-box">
                  {{ entryData.content }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="modal-action-btn secondary" @click="closeModal">取消</button>
          <button
            class="modal-action-btn edit"
            @click="handleModify"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? '提交中...' : '修改内容' }}
          </button>
          <button
            class="modal-action-btn danger"
            @click="handleReject"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? '提交中...' : '拒绝' }}
          </button>
          <button
            class="modal-action-btn primary"
            @click="handleApprove"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? '提交中...' : '通过审核' }}
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getEntryDetail } from '../api/content.js'
import { reviewEntry } from '../api/review.js'
import LoadingSpinner from './admin/LoadingSpinner.vue'
import StatusBadge from './StatusBadge.vue'

const props = defineProps({
  entryId: { type: Number, required: true }
})

const emit = defineEmits(['close', 'reviewed', 'modify'])

const isOpen = ref(true)
const isLoading = ref(true)
const isSubmitting = ref(false)
const entryData = ref({})
const displayTags = ref('')

// 加载条目详情
async function loadEntry() {
  isLoading.value = true
  try {
    const data = await getEntryDetail(props.entryId)
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
    console.error('Failed to load entry:', err)
  } finally {
    isLoading.value = false
  }
}

// 通过审核
async function handleApprove() {
  isSubmitting.value = true
  try {
    await reviewEntry(props.entryId, { action: 'approve' })
    emit('reviewed')
    closeModal()
  } catch (err) {
    console.error('Failed to approve:', err)
    alert('审核失败：' + (err.response?.data?.detail || err.message))
  } finally {
    isSubmitting.value = false
  }
}

// 拒绝
async function handleReject() {
  isSubmitting.value = true
  try {
    await reviewEntry(props.entryId, { action: 'reject' })
    emit('reviewed')
    closeModal()
  } catch (err) {
    console.error('Failed to reject:', err)
    alert('操作失败：' + (err.response?.data?.detail || err.message))
  } finally {
    isSubmitting.value = false
  }
}

// 修改内容
function handleModify() {
  emit('modify', props.entryId)
  closeModal()
}

// 关闭弹窗
function closeModal() {
  isOpen.value = false
  setTimeout(() => {
    emit('close')
  }, 200) // 等待动画完成
}

// 类型样式
function getTypeClass(type) {
  const classes = {
    '教务': 'badge-primary',
    '科研': 'badge-success',
    '活动': 'badge-info',
    '通知': 'badge-warning',
    '招聘': 'badge-danger',
    '其他': 'badge-secondary',
  }
  return classes[type] || 'badge-secondary'
}

// 监听 entryId 变化重新加载数据
watch(() => props.entryId, loadEntry, { immediate: true })
</script>

<style scoped>
/* 弹窗样式 - 参考 AdminUsers.vue */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
  padding: 20px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.75rem;
  line-height: 1;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #f1f3f4;
  color: #495057;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #e9ecef;
  flex-shrink: 0;
}

/* 内容预览区域 - 参考 ManageReview.vue */
.content-preview-section {
  animation: fadeIn 0.2s ease;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.detail-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 10px 16px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
  width: 120px;
}

.detail-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #e9ecef;
  color: #212529;
}

.detail-table tbody tr:last-child th,
.detail-table tbody tr:last-child td {
  border-bottom: none;
}

.content-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.content-section h4 {
  color: #333;
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 600;
}

.content-box {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  color: #495057;
}

/* 标签样式 */
.tags {
  color: #667eea;
  font-weight: 500;
}

.empty-text {
  color: #adb5bd;
  font-style: italic;
}

.highlight {
  color: #667eea;
  font-weight: 600;
}

.link {
  color: #667eea;
  text-decoration: none;
  word-break: break-all;
}

.link:hover {
  text-decoration: underline;
}

/* 按钮样式 - 参考 AdminUsers.vue */
.modal-action-btn {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 20px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1.5px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  white-space: nowrap;
  background: transparent;
}

/* 主按钮 - 绿色 */
.modal-action-btn.primary {
  color: #27ae60;
  background: rgba(39, 174, 96, 0.08);
  border-color: rgba(39, 174, 96, 0.2);
}

.modal-action-btn.primary:hover {
  background: rgba(39, 174, 96, 0.12);
  border-color: rgba(39, 174, 96, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.15);
}

.modal-action-btn.primary:active {
  transform: translateY(0);
}

/* 危险按钮 - 红色 */
.modal-action-btn.danger {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.08);
  border-color: rgba(231, 76, 60, 0.2);
}

.modal-action-btn.danger:hover {
  background: rgba(231, 76, 60, 0.12);
  border-color: rgba(231, 76, 60, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.15);
}

.modal-action-btn.danger:active {
  transform: translateY(0);
}

/* 编辑按钮 - 橙色 */
.modal-action-btn.edit {
  color: #f39c12;
  background: rgba(243, 156, 18, 0.08);
  border-color: rgba(243, 156, 18, 0.2);
}

.modal-action-btn.edit:hover {
  background: rgba(243, 156, 18, 0.12);
  border-color: rgba(243, 156, 18, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(243, 156, 18, 0.15);
}

.modal-action-btn.edit:active {
  transform: translateY(0);
}

/* 次要按钮 - 蓝色 */
.modal-action-btn.secondary {
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.2);
}

.modal-action-btn.secondary:hover {
  background: rgba(102, 126, 234, 0.12);
  border-color: rgba(102, 126, 234, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.modal-action-btn.secondary:active {
  transform: translateY(0);
}

/* 禁用状态 */
.modal-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .modal-content {
    max-height: 95vh;
  }

  .modal-header {
    padding: 16px;
  }

  .modal-header h3 {
    font-size: 1.1rem;
  }

  .modal-body {
    padding: 16px;
  }

  .modal-footer {
    padding: 12px 16px;
    flex-wrap: wrap;
  }

  .modal-action-btn {
    flex: 1 1 auto;
    min-width: 0;
    padding: 10px 16px;
  }

  .detail-table th {
    width: 100px;
    padding: 8px 12px;
  }

  .detail-table td {
    padding: 8px 12px;
  }
}

@media (max-width: 480px) {
  .modal-content {
    max-width: 100%;
  }

  .detail-table th,
  .detail-table td {
    display: block;
    padding: 6px 8px;
  }

  .detail-table th {
    background-color: transparent;
    padding-bottom: 2px;
    color: #6c757d;
    font-size: 0.85rem;
  }
}
</style>
