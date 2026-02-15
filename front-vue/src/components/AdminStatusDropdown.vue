<template>
  <div class="admin-status-dropdown" :class="{ 'is-open': isOpen }" ref="dropdownRef">
    <button class="status-toggle" @click="toggleDropdown">
      <span class="toggle-icon">⚙️</span>
      <span>状态调整</span>
      <svg class="arrow-icon" :class="{ 'rotate': isOpen }" width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M1 3L5 7L9 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <teleport to="body">
      <transition name="dropdown">
        <div v-if="isOpen" class="dropdown-menu" :style="dropdownStyles">
          <div class="dropdown-header">
            <span class="header-icon">{{ currentStatusIcon }}</span>
            <span class="header-text">当前: {{ currentStatusText }}</span>
          </div>
          <div class="dropdown-body">
            <div
              v-for="option in allStatusOptions"
              :key="option.value"
              class="dropdown-item"
              :class="`status-${option.value}`"
              @click="handleStatusChange(option.value)"
            >
              <span class="item-icon">{{ option.icon }}</span>
              <span class="item-label">{{ option.label }}</span>
            </div>
          </div>
        </div>
      </transition>
    </teleport>

    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click.self="cancelChange">
      <div class="modal-content" @click.stop>
        <h3>确认状态变更</h3>
        <p>确定将状态更改为 <strong>{{ targetStatusLabel }}</strong>？</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="cancelChange">取消</button>
          <button class="btn-confirm" @click="confirmChange">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { adminStatusUpdate } from '../api/content'

const props = defineProps({
  entryId: { type: Number, required: true },
  currentStatus: { type: String, required: true }
})

const emit = defineEmits(['status-changed'])

const isOpen = ref(false)
const showConfirmDialog = ref(false)
const selectedStatus = ref('')
const dropdownRef = ref(null)

// 所有状态选项（不受状态流转限制）
const allStatusOptions = [
  { value: 'draft', icon: '📝', label: '草稿' },
  { value: 'pending', icon: '⏳', label: '待审核' },
  { value: 'reviewed', icon: '✅', label: '已审核' },
  { value: 'rejected', icon: '❌', label: '已拒绝' },
  { value: 'published', icon: '🚀', label: '已发布' },
  { value: 'terminated', icon: '🚫', label: '已终止' }
]

const currentStatusConfig = computed(() =>
  allStatusOptions.find(opt => opt.value === props.currentStatus) || allStatusOptions[0]
)
const currentStatusIcon = computed(() => currentStatusConfig.value.icon)
const currentStatusText = computed(() => currentStatusConfig.value.label)

const targetStatusLabel = computed(() => {
  const target = allStatusOptions.find(opt => opt.value === selectedStatus.value)
  return target ? target.label : ''
})

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

function handleStatusChange(newStatus) {
  if (newStatus === props.currentStatus) {
    // 相同状态，无需确认，直接关闭
    isOpen.value = false
    return
  }
  selectedStatus.value = newStatus
  showConfirmDialog.value = true
  isOpen.value = false
}

async function confirmChange() {
  try {
    await adminStatusUpdate(props.entryId, selectedStatus.value)
    showConfirmDialog.value = false
    selectedStatus.value = ''
    emit('status-changed')
  } catch (error) {
    console.error('状态更新失败:', error)
    alert('状态更新失败，请重试')
  }
}

function cancelChange() {
  showConfirmDialog.value = false
  selectedStatus.value = ''
}

function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false
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
.admin-status-dropdown {
  position: relative;
  display: inline-block;
}

/* 触发按钮 */
.status-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  border: 1.5px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  white-space: nowrap;
  min-width: 85px;
  justify-content: center;
}

.status-toggle:hover {
  background: rgba(102, 126, 234, 0.12);
  border-color: rgba(102, 126, 234, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.status-toggle:active {
  transform: translateY(0);
}

.toggle-icon {
  font-size: 0.9rem;
}

.arrow-icon {
  color: currentColor;
  transition: transform 0.3s ease;
}

.arrow-icon.rotate {
  transform: rotate(180deg);
}

/* 下拉菜单 */
.dropdown-menu {
  min-width: 160px;
  max-width: 240px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 10px;
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

/* 状态颜色 */
.dropdown-item.status-draft {
  border-left-color: #3498db;
}

.dropdown-item.status-pending {
  border-left-color: #f39c12;
}

.dropdown-item.status-reviewed {
  border-left-color: #2ecc71;
}

.dropdown-item.status-rejected {
  border-left-color: #e74c3c;
}

.dropdown-item.status-published {
  border-left-color: #9b59b6;
}

.dropdown-item.status-terminated {
  border-left-color: #6c757d;
}

/* 特殊状态样式 */
.dropdown-item.status-terminated {
  color: #6c757d;
}

.dropdown-item.status-terminated:hover {
  background: linear-gradient(135deg, rgba(108, 117, 125, 0.08) 0%, rgba(108, 117, 125, 0.04) 100%);
}

/* 确认对话框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.modal-content {
  background: white;
  padding: 18px;
  border-radius: 10px;
  max-width: 340px;
  width: 85%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  color: #495057;
  font-weight: 600;
}

.modal-content p {
  margin: 0 0 20px 0;
  color: #6c757d;
  line-height: 1.4;
  font-size: 0.9rem;
}

.modal-content p strong {
  color: #667eea;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  gap: 4px;
}

.modal-actions button {
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
  font-weight: 500;
  min-width: 80px;
}

.btn-cancel {
  background: #f8f9fa;
  color: #495057;
}

.btn-cancel:hover {
  background: #e9ecef;
}

.btn-confirm {
  background: #667eea;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-confirm:hover {
  background: #5568d3;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateY(-1px);
}

.btn-confirm:active {
  transform: translateY(0);
}
</style>
