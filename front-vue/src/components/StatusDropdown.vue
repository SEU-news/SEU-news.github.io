<template>
  <div class="status-dropdown" :class="{ 'is-open': isOpen }" ref="dropdownRef">
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
              v-for="option in statusOptions"
              :key="option.value"
              class="dropdown-item"
              :class="`status-${option.value}`"
              @click="handleStatusChange(option.value)"
            >
              <span class="item-icon">{{ option.icon }}</span>
              <span class="item-label">{{ option.label }}</span>
              <svg class="chevron-right" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 2L8 6L4 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { cancelEntry, recallEntry } from '../api/content'
import { publishContent } from '../api/publish'
import { reviewEntry } from '../api/review'

const props = defineProps({
  entryId: { type: Number, required: true },
  currentStatus: { type: String, required: true }
})

const emit = defineEmits(['status-changed'])

const isOpen = ref(false)
const dropdownRef = ref(null)

// 状态配置
const statusConfig = {
  draft: { icon: '📝', label: '草稿', color: '#3498db' },
  pending: { icon: '⏳', label: '待审核', color: '#f39c12' },
  reviewed: { icon: '✅', label: '已审核', color: '#2ecc71' },
  rejected: { icon: '❌', label: '已拒绝', color: '#e74c3c' },
  published: { icon: '🚀', label: '已发布', color: '#9b59b6' },
  terminated: { icon: '🚫', label: '已终止', color: '#6c757d' }
}

const currentStatusConfig = computed(() => statusConfig[props.currentStatus] || statusConfig.draft)
const currentStatusIcon = computed(() => currentStatusConfig.value.icon)
const currentStatusText = computed(() => currentStatusConfig.value.label)

// 状态转换规则
const statusTransitions = {
  draft: [
    { value: 'terminated', label: '终止', icon: '🚫' },
    { value: 'pending', label: '提交审核', icon: '⏳' }
  ],
  pending: [
    { value: 'draft', label: '撤回草稿', icon: '📝' },
    { value: 'reviewed', label: '审核通过', icon: '✅' },
    { value: 'rejected', label: '审核拒绝', icon: '❌' },
    { value: 'terminated', label: '终止', icon: '🚫' }
  ],
  reviewed: [
    { value: 'draft', label: '退回草稿', icon: '📝' },
    { value: 'published', label: '发布', icon: '🚀' },
    { value: 'terminated', label: '终止', icon: '🚫' }
  ],
  rejected: [
    { value: 'draft', label: '修改重提', icon: '📝' },
    { value: 'terminated', label: '终止', icon: '🚫' }
  ],
  published: [
    { value: 'terminated', label: '终止', icon: '🚫' }
  ],
  terminated: [
    { value: 'draft', label: '恢复草稿', icon: '📝' }
  ]
}

const statusOptions = computed(() => {
  return statusTransitions[props.currentStatus] || []
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

async function handleStatusChange(newStatus) {
  const targetConfig = statusConfig[newStatus]
  if (confirm(`确定将状态更改为 "${targetConfig.label}"？\n\n此操作不可撤销。`)) {
    try {
      // 根据当前状态和目标状态选择正确的 API 操作
      const { currentStatus, entryId } = props

      // 终止操作 - 所有状态都可以终止
      if (newStatus === 'terminated') {
        await cancelEntry(entryId)
      }
      // 撤回操作 - reviewed/pending → draft
      else if (newStatus === 'draft' && (currentStatus === 'reviewed' || currentStatus === 'pending')) {
        await recallEntry(entryId)
      }
      // 发布操作 - reviewed → published
      else if (newStatus === 'published' && currentStatus === 'reviewed') {
        await publishContent({ content_ids: [entryId] })
      }
      // 审核操作 - pending → reviewed/rejected
      else if ((newStatus === 'reviewed' || newStatus === 'rejected') && currentStatus === 'pending') {
        await reviewEntry(entryId, { approved: newStatus === 'reviewed' })
      }
      // 提交审核 - draft → pending (需要内容数据，由父组件处理)
      else if (newStatus === 'pending' && currentStatus === 'draft') {
        emit('submit-for-review', entryId)
        isOpen.value = false
        return
      }
      // 重新编辑 - rejected → draft (需要内容数据，由父组件处理)
      else if (newStatus === 'draft' && currentStatus === 'rejected') {
        emit('re-edit', entryId)
        isOpen.value = false
        return
      }

      isOpen.value = false
      emit('status-changed')
    } catch (error) {
      console.error('Failed to update status:', error)
      alert('状态更新失败，请重试')
    }
  }
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
.status-dropdown {
  position: relative;
  display: inline-block;
}

/* 触发按钮 - 调整宽度更紧凑 */
.status-toggle {
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
</style>
