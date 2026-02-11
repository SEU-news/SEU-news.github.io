<template>
  <div class="manage-page">
    <h2>发布内容</h2>

    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <!-- 发布表单 -->
    <div class="manage-form-card">
      <div class="form-group mb-3">
        <label class="form-label">格式 <span class="required-mark">*</span></label>
        <select v-model="publishForm.format" class="form-select" required>
          <option value="pdf">PDF</option>
          <option value="typst">Typst</option>
          <option value="latex">LaTeX</option>
        </select>
      </div>

      <div class="form-group mb-3">
        <label class="form-label">日期 <span class="required-mark">*</span></label>
        <input
          v-model="publishForm.date"
          type="date"
          class="form-control"
          required
        />
      </div>

      <div class="form-group mb-3">
        <label class="form-label">模板</label>
        <select v-model="publishForm.template" class="form-select">
          <option value="default">默认模板</option>
          <option value="simple">简洁模板</option>
          <option value="detailed">详细模板</option>
        </select>
      </div>

      <div class="d-flex gap-2">
        <button
          type="button"
          class="btn btn-primary"
          @click="handlePublish"
          :disabled="isPublishing"
        >
          {{ isPublishing ? '发布中...' : '发布' }}
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="handlePreview"
          :disabled="isPublishing"
        >
          预览
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

    <!-- 已审核内容列表 -->
    <div class="manage-form-card">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3>待发布内容（已审核）</h3>
        <span class="text-muted">{{ reviewedEntries.length }} 条</span>
      </div>

      <LoadingSpinner v-if="isLoading" />

      <div v-else-if="reviewedEntries.length > 0">
        <div class="list-group">
          <div
            v-for="entry in reviewedEntries"
            :key="entry.id"
            class="list-group-item"
          >
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <input
                  type="checkbox"
                  :value="entry.id"
                  v-model="selectedEntries"
                  class="me-2"
                  id="checkbox-{{ entry.id }}"
                />
                <label :for="'checkbox-' + entry.id" class="fw-bold">
                  {{ entry.title }}
                </label>
              </div>
              <span class="badge badge-primary">{{ entry.type }}</span>
            </div>
            <div class="mt-2 text-muted small">
              描述者：{{ entry.describer_username }} | 审核时间：{{ entry.formatted_updated_at }}
            </div>
          </div>
        </div>

        <div class="mt-3 d-flex gap-2">
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
          <span class="ms-3 text-muted">
            已选择 {{ selectedEntries.length }} 条
          </span>
        </div>
      </div>

      <EmptyState
        v-else
        icon="📋"
        title="没有待发布的内容"
        description="请先审核内容"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getEntries } from '../../api/content.js'
import { publishContent, generateTypst, generateLatex } from '../../api/publish.js'
import LoadingSpinner from '../../components/admin/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'

const router = useRouter()

// 发布表单
const publishForm = ref({
  format: 'pdf',
  date: new Date().toISOString().split('T')[0], // 今天
  template: 'default',
})

// 数据
const reviewedEntries = ref([])
const selectedEntries = ref([])

// 状态
const message = ref('')
const messageClass = ref('alert-info')
const isLoading = ref(false)
const isPublishing = ref(false)

// 加载已审核内容
async function loadReviewedEntries() {
  isLoading.value = true
  try {
    const data = await getEntries({
      page: 1,
      page_size: 100,
      sort: 'updated_at',
      order: 'desc',
    })

    // 过滤出已审核的内容
    reviewedEntries.value = (data.results || []).filter(
      entry => entry.status === 'reviewed'
    )
  } catch (err) {
    showMessage('加载失败：' + err.message, 'alert-danger')
  } finally {
    isLoading.value = false
  }
}

// 全选
function selectAll() {
  selectedEntries.value = reviewedEntries.value.map(e => e.id)
}

// 取消全选
function selectNone() {
  selectedEntries.value = []
}

// 发布
async function handlePublish() {
  if (selectedEntries.value.length === 0) {
    showMessage('请至少选择一条内容', 'alert-warning')
    return
  }

  isPublishing.value = true
  message.value = ''

  try {
    await publishContent({
      format: publishForm.value.format,
      date: publishForm.value.date,
      template: publishForm.value.template,
      entries: selectedEntries.value,
    })

    showMessage('发布成功！', 'alert-success')

    // 3秒后返回
    setTimeout(() => {
      router.push('/manage')
    }, 3000)
  } catch (err) {
    showMessage('发布失败：' + err.message, 'alert-danger')
  } finally {
    isPublishing.value = false
  }
}

// 预览
async function handlePreview() {
  if (selectedEntries.value.length === 0) {
    showMessage('请至少选择一条内容', 'alert-warning')
    return
  }

  // 跳转到预览页面
  router.push({
    path: '/manage/preview',
    query: {
      entries: selectedEntries.value.join(','),
      format: publishForm.value.format,
      date: publishForm.value.date,
      template: publishForm.value.template,
    },
  })
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

onMounted(loadReviewedEntries)
</script>

<style scoped>
@import '../../styles/layout.css';
@import '../../styles/utilities.css';
@import '../../styles/buttons.css';
@import '../../styles/forms.css';
@import '../../styles/alerts.css';
@import '../../styles/manage.css';

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

h3 {
  margin: 0 0 1rem 0;
  color: #555;
  font-size: 1.25rem;
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

.required-mark {
  color: #dc3545;
  margin-left: 4px;
}
</style>
