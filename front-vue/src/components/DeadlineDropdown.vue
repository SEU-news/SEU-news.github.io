<template>
  <div class="deadline-dropdown" :class="{ 'is-open': isOpen }" ref="dropdownRef">
    <button class="deadline-toggle" @click="toggleDropdown">
      <span class="toggle-icon">📅</span>
      <span>截止日期</span>
      <svg class="arrow-icon" :class="{ 'rotate': isOpen }" width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M1 3L5 7L9 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <teleport to="body">
      <transition name="dropdown">
        <div v-if="isOpen" class="dropdown-menu" :style="dropdownStyles">
          <div class="dropdown-header">
            <span class="header-icon">📅</span>
            <span class="header-text">当前: {{ formattedDeadline || '未设置' }}</span>
          </div>
          <div class="dropdown-body">
            <div class="dropdown-item" @click="openDateInput">
              <span class="item-icon">📝</span>
              <span class="item-label">设置日期...</span>
              <svg class="chevron-right" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 2L8 6L4 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div v-if="currentDeadline" class="dropdown-item text-danger" @click="clearDeadline">
              <span class="item-icon">🗑️</span>
              <span class="item-label">清除截止日期</span>
              <svg class="chevron-right" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 2L8 6L4 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </transition>
    </teleport>

    <!-- 日期选择弹窗 -->
    <transition name="modal">
      <div v-if="showDateInput" class="modal-backdrop" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h3>设置截止日期</h3>
          <input v-model="newDeadline" type="date" class="form-control" />
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="closeModal">取消</button>
            <button class="btn btn-primary" @click="setDeadline">确认</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { updateEntry } from '../api/content'

const props = defineProps({
  entryId: { type: Number, required: true },
  currentDeadline: { type: String, default: '' },
  formattedDeadline: { type: String, default: '' }
})

const emit = defineEmits(['deadline-changed'])

const isOpen = ref(false)
const showDateInput = ref(false)
const dropdownRef = ref(null)
const newDeadline = ref(props.currentDeadline || '')

// 动态计算下拉菜单位置
const dropdownStyles = computed(() => {
  if (!dropdownRef.value || !isOpen.value) return {}

  const rect = dropdownRef.value.getBoundingClientRect()
  return {
    position: 'fixed',
    left: `${rect.left}px`,
    top: `${rect.bottom + 6}px`,
    zIndex: 2000
  }
})

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function closeDropdown() {
  isOpen.value = false
}

function openDateInput() {
  showDateInput.value = true
  closeDropdown()
}

function closeModal() {
  showDateInput.value = false
  newDeadline.value = props.currentDeadline || ''
}

async function setDeadline() {
  if (!newDeadline.value) {
    alert('请选择截止日期')
    return
  }

  try {
    await updateEntry(props.entryId, { deadline: newDeadline.value })
    emit('deadline-changed')
    closeModal()
  } catch (error) {
    console.error('设置截止日期失败:', error)
    alert('设置失败，请重试')
  }
}

async function clearDeadline() {
  if (!confirm('确定要清除截止日期吗？')) {
    return
  }

  try {
    await updateEntry(props.entryId, { deadline: null })
    emit('deadline-changed')
    closeDropdown()
  } catch (error) {
    console.error('清除截止日期失败:', error)
    alert('清除失败，请重试')
  }
}

function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.deadline-dropdown {
  position: relative;
  display: inline-block;
}

/* 触发按钮 - 调整宽度更紧凑 */
.deadline-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px; /* 减小内边距 */
  font-size: 0.8125rem; /* 稍微减小字体 */
  font-weight: 500;
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  border: 1.5px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px; /* 稍微减小圆角 */
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  white-space: nowrap; /* 防止按钮文字换行 */
  min-width: 85px; /* 设置最小宽度保持一致性 */
  justify-content: center;
}

.deadline-toggle:hover {
  background: rgba(102, 126, 234, 0.12);
  border-color: rgba(102, 126, 234, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.deadline-toggle:active {
  transform: translateY(0);
}

.toggle-icon {
  font-size: 0.9rem; /* 稍微减小图标 */
}

.arrow-icon {
  color: currentColor;
  transition: transform 0.3s ease;
}

.arrow-icon.rotate {
  transform: rotate(180deg);
}

/* 下拉菜单 - 调整宽度 */
.dropdown-menu {
  min-width: 160px; /* 减小最小宽度 */
  max-width: 240px; /* 添加最大宽度限制 */
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 10px; /* 稍微减小圆角 */
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 下拉菜单动画 */
.dropdown-enter-active {
  animation: dropdownIn 0.2s ease-out;
}

.dropdown-leave-active {
  animation: dropdownOut 0.15s ease-in;
}

@keyframes dropdownIn {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes dropdownOut {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(-5px) scale(0.95);
  }
}

/* 菜单头部 */
.dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e9ecef;
}

.header-icon {
  font-size: 1.2rem;
}

.header-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
}

/* 菜单主体 */
.dropdown-body {
  padding: 6px;
}

/* 菜单项 */
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  color: #495057;
  font-size: 0.9rem;
  border-radius: 6px;
  border-left: 3px solid transparent;
  position: relative;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(102, 126, 234, 0.04) 100%);
  transform: translateX(2px);
}

.dropdown-item.text-danger {
  color: #dc3545;
  border-left-color: #dc3545;
}

.dropdown-item.text-danger:hover {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.08) 0%, rgba(220, 53, 69, 0.04) 100%);
}

.item-icon {
  font-size: 1.1rem;
  width: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-label {
  flex: 1;
  font-weight: 500;
}

.chevron-right {
  opacity: 0.3;
  transition: all 0.2s ease;
}

.dropdown-item:hover .chevron-right {
  opacity: 1;
  transform: translateX(2px);
}

/* 日期选择弹窗样式 */
.modal-enter-active {
  animation: modalIn 0.2s ease-out;
}

.modal-leave-active {
  animation: modalOut 0.15s ease-in;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes modalOut {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.9);
  }
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  min-width: 320px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: modalContentIn 0.2s ease-out;
}

@keyframes modalContentIn {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-content h3 {
  margin: 0 0 16px 0;
  font-size: 1.25rem;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  margin-bottom: 16px;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
  transform: translateY(-1px);
}

.btn:active {
  transform: translateY(0);
}
</style>
