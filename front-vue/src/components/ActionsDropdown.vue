<template>
  <div class="actions-dropdown" :class="{ 'is-open': isOpen }" ref="dropdownRef">
    <button class="actions-toggle" @click="toggleDropdown">
      <span class="toggle-icon">⚙️</span>
      <span>操作</span>
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
            <div v-if="availableActions.length === 0" class="no-actions">
              <span class="no-actions-icon">🔒</span>
              <span class="no-actions-text">无可执行操作</span>
            </div>
            <div
              v-for="action in availableActions"
              :key="action.id"
              class="dropdown-item"
              :class="`action-${action.type}`"
              @click="handleAction(action)"
            >
              <span class="item-icon">{{ action.icon }}</span>
              <span class="item-label">{{ action.label }}</span>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStatusConfig } from '../composables/useStatusConfig.js'
import { recallEntry, submitEntry } from '../api/content.js'
import { publishContent } from '../api/publish.js'

const props = defineProps({
  entryId: { type: Number, required: true },
  status: { type: String, required: true },
  creatorUsername: { type: String, required: true },
  editorFlag: { type: Boolean, required: true },
  currentUsername: { type: String, required: true },
  entryData: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['action-complete', 'edit', 'review'])

const router = useRouter()
const { getStatusConfig } = useStatusConfig()

const isOpen = ref(false)
const dropdownRef = ref(null)

// 判断当前用户是否是创建者
const isCreator = computed(() => {
  return props.currentUsername === props.creatorUsername
})

// 当前状态配置
const currentStatusConfig = computed(() => getStatusConfig(props.status))
const currentStatusIcon = computed(() => currentStatusConfig.value.icon)
const currentStatusText = computed(() => currentStatusConfig.value.label)

// 可用操作列表
const availableActions = computed(() => {
  const actions = []
  const { status, editorFlag } = props

  if (!editorFlag) {
    return actions // 非编辑者无操作权限
  }

  // 编辑：草稿状态下的操作
  if (status === 'draft') {
    actions.push({
      id: 'edit',
      label: '编辑',
      icon: '✏️',
      type: 'edit'
    })
    actions.push({
      id: 'submit',
      label: '提交',
      icon: '📤',
      type: 'submit'
    })
  }

  // 审核：待审核状态下的操作（非创建者）
  if (status === 'pending' && !isCreator.value) {
    actions.push({
      id: 'review',
      label: '审核',
      icon: '✅',
      type: 'review'
    })
  }

  // 发布：已审核状态下的操作
  if (status === 'reviewed') {
    actions.push({
      id: 'publish',
      label: '发布',
      icon: '🚀',
      type: 'publish'
    })
  }

  // 撤回：待审核状态下的创建者专属操作
  if (status === 'pending' && isCreator.value) {
    actions.push({
      id: 'recall',
      label: '撤回',
      icon: '↩️',
      type: 'warning'
    })
  }

  return actions
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

async function handleAction(action) {
  const confirmMessages = {
    recall: '确定要撤回这条内容吗？状态将变为草稿。',
    publish: '确定要发布这条内容吗？',
    submit: '确定要提交这条内容吗？状态将变为待审核。'
  }

  // 危险操作需要确认
  if (confirmMessages[action.id] && !confirm(confirmMessages[action.id])) {
    return
  }

  try {
    switch (action.id) {
      case 'edit':
        emit('edit', props.entryId)
        break
      case 'submit':
        await submitEntry(props.entryId)
        break
      case 'review':
        emit('review', props.entryId)
        break
      case 'recall':
        await recallEntry(props.entryId)
        break
      case 'publish':
        await publishContent({ content_ids: [props.entryId] })
        break
    }

    // 如果是 API 操作，完成后刷新列表
    if (['recall', 'publish', 'submit'].includes(action.id)) {
      emit('action-complete')
    }

    isOpen.value = false
  } catch (error) {
    console.error(`Failed to perform action ${action.id}:`, error)
    alert('操作失败，请重试')
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
.actions-dropdown {
  position: relative;
  display: inline-block;
}

/* 触发按钮 */
.actions-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #495057;
  background: white;
  border: 1.5px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  white-space: nowrap;
  min-width: 85px;
  justify-content: center;
}

.actions-toggle:hover {
  background: #f8f9fa;
  border-color: #ced4da;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.actions-toggle:active {
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

/* 无操作状态 */
.no-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  color: #6c757d;
  font-size: 0.9rem;
}

.no-actions-icon {
  font-size: 2rem;
  opacity: 0.5;
}

.no-actions-text {
  font-weight: 500;
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

/* 操作类型样式 */
.dropdown-item.action-edit {
  border-left-color: #3498db;
}

.dropdown-item.action-submit {
  border-left-color: #00c853;
  color: #00c853;
}

.dropdown-item.action-submit:hover {
  background: linear-gradient(135deg, rgba(0, 200, 83, 0.1) 0%, rgba(0, 200, 83, 0.05) 100%);
}

.dropdown-item.action-review {
  border-left-color: #2ecc71;
}

.dropdown-item.action-publish {
  border-left-color: #00c853;
  color: #00c853;
}

.dropdown-item.action-publish:hover {
  background: linear-gradient(135deg, rgba(0, 200, 83, 0.1) 0%, rgba(0, 200, 83, 0.05) 100%);
}

.dropdown-item.action-warning {
  color: #f39c12;
  border-left-color: #f39c12;
}

.dropdown-item.action-warning:hover {
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.1) 0%, rgba(243, 156, 18, 0.05) 100%);
}

.dropdown-item.action-danger {
  color: #dc3545;
  border-left-color: #dc3545;
}

.dropdown-item.action-danger:hover {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(220, 53, 69, 0.05) 100%);
}
</style>
