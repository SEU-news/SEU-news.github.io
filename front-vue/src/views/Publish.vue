<template>
  <div class="container mt-5">
    <h2>发布内容</h2>

    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <!-- 发布表单 -->
    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">发布配置</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="form-group mb-3">
                  <label>格式 <span class="text-danger">*</span></label>
                  <select v-model="publishForm.format" class="form-select" required>
                    <option value="pdf">PDF</option>
                    <option value="typst">Typst</option>
                    <option value="latex">LaTeX</option>
                  </select>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-group mb-3">
                  <label>日期 <span class="text-danger">*</span></label>
                  <input
                    v-model="publishForm.date"
                    type="date"
                    class="form-control"
                    required
                  />
                </div>
              </div>
            </div>

            <div class="form-group mb-3">
              <label>模板</label>
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
        </div>
      </div>
    </div>

    <!-- 已审核内容列表 -->
    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">待发布内容（已审核）</h5>
          </div>
          <div class="card-body">
            <div v-if="isLoading" class="text-center py-5">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">加载中...</span>
              </div>
            </div>

            <table v-else-if="reviewedEntries.length > 0" class="table table-hover">
              <thead>
                <tr>
                  <th width="50">选择</th>
                  <th>标题</th>
                  <th>类型</th>
                  <th>描述者</th>
                  <th>审核时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="entry in reviewedEntries" :key="entry.id">
                  <td>
                    <input
                      type="checkbox"
                      :value="entry.id"
                      v-model="selectedEntries"
                      class="form-check-input"
                    />
                  </td>
                  <td>{{ entry.title }}</td>
                  <td>
                    <span class="badge bg-primary">{{ entry.type }}</span>
                  </td>
                  <td>{{ entry.describer_username }}</td>
                  <td>{{ entry.formatted_updated_at }}</td>
                </tr>
              </tbody>
            </table>

            <div v-else class="text-center py-5 text-muted">
              没有待发布的内容
            </div>

            <div v-if="reviewedEntries.length > 0" class="mt-3">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getEntries } from '../api/content.js'
import { publishContent, generateTypst, generateLatex } from '../api/publish.js'

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
    reviewedEntries.value = (data.entries || []).filter(
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
@import '../styles/layout.css';
@import '../styles/utilities.css';
@import '../styles/buttons.css';
@import '../styles/forms.css';
@import '../styles/alerts.css';
@import '../styles/tables.css';

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.card {
  margin-bottom: 1.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
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

.text-danger {
  color: #dc3545;
}

.gap-2 {
  gap: 0.5rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.mt-3 {
  margin-top: 1rem;
}

.ms-3 {
  margin-left: 1rem;
}
</style>
