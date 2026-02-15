<template>
  <div class="pagination-container" v-if="totalPages > 0">
    <div class="pagination-wrapper">
      <!-- 每页条数选择器（可选） -->
      <div v-if="showPageSizeSelector" class="page-size-wrapper">
        <span class="label">每页显示</span>
        <select v-model="internalPageSize" @change="handlePageSizeChange" class="page-size-select">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">
            {{ size }} 条
          </option>
        </select>
      </div>

      <!-- 页码按钮组 -->
      <div class="page-buttons">
        <!-- 上一页按钮 -->
        <button
          class="page-btn nav-btn"
          :class="{ 'disabled': page === 1 }"
          :disabled="page === 1"
          @click="prevPage">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15 19L8 12L15 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          上一页
        </button>

        <!-- 页码按钮 -->
        <button
          v-for="p in displayPages"
          :key="p"
          class="page-btn"
          :class="{ 'active': p === page, 'ellipsis': p === '...' }"
          :disabled="p === '...'"
          @click="goToPage(p)">
          {{ p }}
        </button>

        <!-- 下一页按钮 -->
        <button
          class="page-btn nav-btn"
          :class="{ 'disabled': page === totalPages }"
          :disabled="page === totalPages"
          @click="nextPage">
          下一页
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 5L16 12L9 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- 跳转输入框（可选） -->
      <div v-if="showJumpInput" class="jump-wrapper">
        <span class="label">跳至</span>
        <input
          v-model.number="jumpPage"
          type="number"
          :min="1"
          :max="totalPages"
          class="jump-input"
          @keyup.enter="handleJump"
        />
        <span class="label">页</span>
        <button class="jump-btn" @click="handleJump">跳转</button>
      </div>
    </div>

    <!-- 分页信息 -->
    <div class="pagination-info">
      第 <span class="current-page">{{ page }}</span> / {{ totalPages }} 页，共 {{ totalCount }} 条
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  pageSize: { type: Number, default: 10 },
  totalCount: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  pageSizeOptions: { type: Array, default: () => [10, 20, 50, 100] },
  showPageSizeSelector: { type: Boolean, default: true },
  showJumpInput: { type: Boolean, default: false }
})

const emit = defineEmits(['page-change', 'page-size-change'])

const internalPageSize = ref(props.pageSize)
const jumpPage = ref(props.page)

// 智能显示页码数组（带省略号）
const displayPages = computed(() => {
  const current = props.page
  const total = props.totalPages
  const pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    pages.push(1)
    if (current > 3) {
      pages.push('...')
    }
    let start = Math.max(2, current - 1)
    let end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    if (current < total - 2) {
      pages.push('...')
    }
    pages.push(total)
  }

  return pages
})

function prevPage() {
  if (props.page > 1) {
    emit('page-change', props.page - 1)
  }
}

function nextPage() {
  if (props.page < props.totalPages) {
    emit('page-change', props.page + 1)
  }
}

function goToPage(pageNum) {
  if (pageNum >= 1 && pageNum <= props.totalPages && pageNum !== '...') {
    emit('page-change', pageNum)
  }
}

function handlePageSizeChange() {
  emit('page-size-change', internalPageSize.value)
}

function handleJump() {
  if (jumpPage.value >= 1 && jumpPage.value <= props.totalPages) {
    emit('page-change', jumpPage.value)
    jumpPage.value = props.page
  }
}

watch(() => props.page, (newPage) => {
  jumpPage.value = newPage
})
</script>

<style scoped>
/* 主容器 */
.pagination-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px 0;
}

/* 分页控制包装器 */
.pagination-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

/* 每页条数选择器 */
.page-size-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size-wrapper .label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.page-size-select {
  padding: 6px 10px;
  min-width: 70px;
  font-size: 0.875rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background: #fff;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-size-select:hover {
  border-color: #3498db;
}

.page-size-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

/* 页码按钮组 */
.page-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 页码按钮 */
.page-btn {
  min-width: 36px;
  height: 36px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid #dee2e6;
  background: #fff;
  color: #495057;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled):not(.ellipsis) {
  border-color: #3498db;
  color: #3498db;
  background: #f8f9fa;
}

.page-btn:active:not(:disabled):not(.ellipsis) {
  background: #e9ecef;
}

.page-btn.active {
  background: #3498db;
  border-color: #3498db;
  color: #fff;
}

.page-btn.ellipsis {
  border-color: transparent;
  background: transparent;
  color: #adb5bd;
  cursor: default;
  font-weight: 400;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 导航按钮（上一页/下一页） */
.nav-btn {
  min-width: 90px;
  gap: 6px;
  padding: 0 12px;
}

.nav-btn svg {
  color: #6c757d;
  transition: color 0.2s ease;
}

.nav-btn:hover:not(:disabled) svg {
  color: #3498db;
}

/* 跳转输入框 */
.jump-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.jump-wrapper .label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.jump-input {
  width: 60px;
  padding: 6px 8px;
  font-size: 0.875rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  text-align: center;
  transition: all 0.2s ease;
}

.jump-input:hover {
  border-color: #3498db;
}

.jump-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.jump-btn {
  padding: 6px 12px;
  font-size: 0.875rem;
  font-weight: 500;
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.jump-btn:hover {
  background: #2c3e50;
}

.jump-btn:active {
  background: #1a252f;
}

/* 分页信息 */
.pagination-info {
  font-size: 0.875rem;
  color: #6c757d;
  text-align: center;
}

.pagination-info .current-page {
  color: #3498db;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pagination-wrapper {
    flex-direction: column;
    gap: 12px;
  }

  .nav-btn {
    min-width: auto;
    width: 100%;
  }

  .page-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
