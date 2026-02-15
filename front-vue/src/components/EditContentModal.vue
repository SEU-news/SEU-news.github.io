<template>
  <teleport to="body">
    <div v-if="isOpen" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-content edit-modal">
        <div class="modal-header">
          <h3>编辑内容</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>

        <div class="modal-body">
          <LoadingSpinner v-if="isLoading" />

          <form v-else @submit.prevent="handleSubmit" class="edit-form">
            <!-- 表单字段 -->
            <div class="form-group">
              <label class="form-label">标题 <span class="required-mark">*</span></label>
              <input
                v-model="formData.title"
                type="text"
                class="form-control"
                placeholder="请输入标题"
                required
                maxlength="200"
              />
            </div>

            <div class="form-group">
              <label class="form-label">链接 <span class="required-mark">*</span></label>
              <input
                v-model="formData.link"
                type="url"
                class="form-control"
                placeholder="https://example.com"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">短标题</label>
              <input
                v-model="formData.short_title"
                type="text"
                class="form-control"
                placeholder="请输入短标题"
                maxlength="100"
              />
            </div>

            <div class="form-group">
              <label class="form-label">内容 <span class="required-mark">*</span></label>
              <textarea
                v-model="formData.content"
                class="form-control"
                rows="6"
                placeholder="请输入内容描述..."
                required
              ></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">类型 <span class="required-mark">*</span></label>
                <select v-model="formData.type" class="form-select" required>
                  <option value="">请选择类型</option>
                  <option value="教务">教务</option>
                  <option value="科研">科研</option>
                  <option value="活动">活动</option>
                  <option value="通知">通知</option>
                  <option value="招聘">招聘</option>
                  <option value="其他">其他</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">标签</label>
                <input
                  v-model="formData.tag"
                  type="text"
                  class="form-control"
                  placeholder="多个标签用逗号分隔（可选）"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">截止日期</label>
              <input
                v-model="formData.deadline"
                type="date"
                class="form-control"
              />
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button class="modal-action-btn secondary" @click="closeModal">取消</button>
          <button
            class="modal-action-btn primary"
            @click="handleSubmit"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? '提交中...' : '保存修改' }}
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getEntryDetail, updateEntry } from '../api/content.js'
import LoadingSpinner from './admin/LoadingSpinner.vue'

const props = defineProps({
  entryId: { type: Number, required: true }
})

const emit = defineEmits(['close', 'updated'])

const isOpen = ref(true)
const isLoading = ref(true)
const isSubmitting = ref(false)
const entryData = ref({})
const formData = ref({
  title: '',
  short_title: '',
  content: '',
  type: '',
  tag: '',
  deadline: '',
  link: ''
})

// 加载条目详情
async function loadEntry() {
  isLoading.value = true
  try {
    const data = await getEntryDetail(props.entryId)
    entryData.value = data

    // 处理 tag：将 JSON 数组转换为逗号分隔的字符串
    let tags = ''
    try {
      if (data.tag) {
        const tagArray = JSON.parse(data.tag)
        if (Array.isArray(tagArray) && tagArray.length > 0) {
          tags = tagArray.join(',')
        }
      }
    } catch (e) {
      console.warn('Failed to parse tags:', e)
    }

    // 填充表单
    formData.value.title = data.title
    formData.value.short_title = data.short_title
    formData.value.content = data.content
    formData.value.type = data.type
    formData.value.tag = tags
    formData.value.deadline = data.deadline || ''
    formData.value.link = data.link || ''
  } catch (err) {
    console.error('Failed to load entry:', err)
    alert('加载失败：' + (err.response?.data?.detail || err.message))
  } finally {
    isLoading.value = false
  }
}

// 提交表单
async function handleSubmit() {
  // 验证必填字段
  if (!formData.value.title.trim()) {
    alert('请输入标题')
    return
  }
  if (!formData.value.link.trim()) {
    alert('请输入链接')
    return
  }
  if (!formData.value.content.trim()) {
    alert('请输入内容')
    return
  }
  if (!formData.value.type) {
    alert('请选择类型')
    return
  }

  isSubmitting.value = true

  // 处理 tag：将逗号分隔的字符串转换为 JSON 数组
  let tagValue = null
  if (formData.value.tag && formData.value.tag.trim()) {
    const tags = formData.value.tag
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0)
    if (tags.length > 0) {
      tagValue = JSON.stringify(tags)
    }
  }

  try {
    await updateEntry(props.entryId, {
      title: formData.value.title,
      short_title: formData.value.short_title,
      content: formData.value.content,
      type: formData.value.type,
      tag: tagValue,
      deadline: formData.value.deadline || null,
      link: formData.value.link || '',
    })

    emit('updated')
    closeModal()
  } catch (err) {
    console.error('Failed to update entry:', err)
    alert('修改失败：' + (err.response?.data?.detail || err.message))
  } finally {
    isSubmitting.value = false
  }
}

// 关闭弹窗
function closeModal() {
  isOpen.value = false
  setTimeout(() => {
    emit('close')
  }, 200) // 等待动画完成
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
  max-width: 700px;
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

/* 表单样式 */
.edit-form {
  animation: fadeIn 0.2s ease;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label,
.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
  font-size: 0.9rem;
}

.required-mark {
  color: #dc3545;
  margin-left: 4px;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #fafafa;
  color: #2c3e50;
  box-sizing: border-box;
  font-family: inherit;
}

.form-control:hover {
  border-color: #b0b0b0;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15), 0 4px 12px rgba(102, 126, 234, 0.1);
  background-color: #fff;
}

.form-control::placeholder {
  color: #adb5bd;
  font-weight: 400;
  transition: color 0.3s ease;
}

.form-control:focus::placeholder {
  color: #d0d3d4;
}

.form-control:disabled {
  background-color: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
}

textarea.form-control {
  resize: vertical;
  min-height: 120px;
  line-height: 1.5;
}

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #fafafa;
  color: #2c3e50;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='%236c757d' d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 12px;
  padding-right: 36px;
  cursor: pointer;
}

.form-select:hover {
  border-color: #b0b0b0;
  background-color: #fff;
}

.form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15), 0 4px 12px rgba(102, 126, 234, 0.1);
  background-color: #fff;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .form-group {
    margin-bottom: 1rem;
  }
}

@media (max-width: 480px) {
  .modal-content {
    max-width: 100%;
  }

  .modal-footer {
    flex-wrap: wrap;
  }

  .modal-action-btn {
    flex: 1 1 auto;
    min-width: 0;
    padding: 10px 16px;
  }
}
</style>
