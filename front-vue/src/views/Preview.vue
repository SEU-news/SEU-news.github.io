<template>
  <div class="container mt-5">
    <h2>预览编辑</h2>

    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <!-- 工具栏 -->
    <div class="card mb-4">
      <div class="card-body d-flex justify-content-between align-items-center">
        <div>
          <h5 class="mb-1">预览格式：{{ currentFormat }}</h5>
          <p class="mb-0 text-muted">{{ selectedEntries.length }} 条内容</p>
        </div>
        <div class="d-flex gap-2">
          <button
            type="button"
            class="btn btn-outline-primary"
            @click="changeFormat('typst')"
            :class="{ active: currentFormat === 'typst' }"
          >
            Typst
          </button>
          <button
            type="button"
            class="btn btn-outline-primary"
            @click="changeFormat('latex')"
            :class="{ active: currentFormat === 'latex' }"
          >
            LaTeX
          </button>
          <button
            type="button"
            class="btn btn-outline-primary"
            @click="changeFormat('pdf')"
            :class="{ active: currentFormat === 'pdf' }"
          >
            PDF
          </button>
        </div>
      </div>
    </div>

    <!-- 预览内容 -->
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">内容预览</h5>
        <button
          type="button"
          class="btn btn-sm btn-outline-secondary"
          @click="togglePreview"
        >
          {{ showPreview ? '隐藏预览' : '显示预览' }}
        </button>
      </div>
      <div v-if="showPreview" class="card-body">
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">生成中...</span>
          </div>
        </div>

        <div v-else-if="previewContent" class="preview-content">
          <pre v-if="currentFormat !== 'pdf'">{{ previewContent }}</pre>
          <div v-else class="pdf-preview">
            <p class="text-muted">PDF 预览将在新窗口打开</p>
          </div>
        </div>

        <div v-else class="text-center py-5 text-muted">
          点击下方按钮生成预览
        </div>
      </div>
    </div>

    <!-- 内容列表 -->
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">已选内容</h5>
      </div>
      <div class="card-body">
        <div v-if="isLoadingList" class="text-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>

        <div v-else-if="entries.length > 0" class="list-group">
          <div
            v-for="(entry, index) in entries"
            :key="entry.id"
            class="list-group-item"
          >
            <div class="d-flex justify-content-between align-items-start">
              <div class="ms-2 me-auto">
                <div class="fw-bold">{{ index + 1 }}. {{ entry.title }}</div>
                <small class="text-muted">
                  {{ entry.type }} - {{ entry.describer_username }}
                </small>
              </div>
              <span class="badge bg-primary rounded-pill">{{ entry.type }}</span>
            </div>
            <div v-if="entry.content" class="mt-2 text-muted small">
              {{ entry.content.slice(0, 200) }}...
            </div>
          </div>
        </div>

        <div v-else class="text-center py-5 text-muted">
          没有选中任何内容
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="card">
      <div class="card-body">
        <div class="d-flex gap-2 justify-content-center">
          <button
            type="button"
            class="btn btn-primary"
            @click="handlePublish"
            :disabled="isPublishing || entries.length === 0"
          >
            {{ isPublishing ? '发布中...' : '确认发布' }}
          </button>
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="generatePreview"
            :disabled="isGenerating || entries.length === 0"
          >
            {{ isGenerating ? '生成中...' : '生成预览' }}
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getEntries } from '../api/content.js'
import { previewEdit, generateTypst, generateLatex, publishContent } from '../api/publish.js'

const router = useRouter()
const route = useRoute()

// 从查询参数获取数据
const selectedEntries = computed(() => {
  const entries = route.query.entries
  return entries ? entries.split(',').map(Number) : []
})

// 状态
const currentFormat = ref('typst')
const showPreview = ref(true)
const previewContent = ref('')
const entries = ref([])

const message = ref('')
const messageClass = ref('alert-info')
const isLoading = ref(false)
const isLoadingList = ref(false)
const isGenerating = ref(false)
const isPublishing = ref(false)

// 加载选中内容的详情
async function loadEntries() {
  if (selectedEntries.value.length === 0) {
    return
  }

  isLoadingList.value = true
  try {
    const data = await getEntries({
      page: 1,
      page_size: 100,
    })

    // 筛选出选中的条目
    entries.value = (data.entries || []).filter(entry =>
      selectedEntries.value.includes(entry.id)
    )
  } catch (err) {
    showMessage('加载失败：' + err.message, 'alert-danger')
  } finally {
    isLoadingList.value = false
  }
}

// 生成预览
async function generatePreview() {
  if (entries.value.length === 0) {
    showMessage('请先选择内容', 'alert-warning')
    return
  }

  isGenerating.value = true
  message.value = ''

  try {
    const date = route.query.date || new Date().toISOString().split('T')[0]

    let content = ''
    if (currentFormat.value === 'typst') {
      const result = await generateTypst(date)
      content = result.content || JSON.stringify(result, null, 2)
    } else if (currentFormat.value === 'latex') {
      const result = await generateLatex(date)
      content = result.content || JSON.stringify(result, null, 2)
    } else {
      content = 'PDF 格式请直接下载查看'
    }

    previewContent.value = content
  } catch (err) {
    showMessage('生成预览失败：' + err.message, 'alert-danger')
  } finally {
    isGenerating.value = false
  }
}

// 切换格式
function changeFormat(format) {
  currentFormat.value = format
  previewContent.value = ''
}

// 切换预览显示
function togglePreview() {
  showPreview.value = !showPreview.value
}

// 发布
async function handlePublish() {
  if (entries.value.length === 0) {
    showMessage('请先选择内容', 'alert-warning')
    return
  }

  isPublishing.value = true
  message.value = ''

  try {
    await publishContent({
      format: currentFormat.value,
      date: route.query.date || new Date().toISOString().split('T')[0],
      template: route.query.template || 'default',
      entries: selectedEntries.value,
    })

    showMessage('发布成功！', 'alert-success')

    // 3秒后返回主页
    setTimeout(() => {
      router.push('/manage')
    }, 3000)
  } catch (err) {
    showMessage('发布失败：' + err.message, 'alert-danger')
  } finally {
    isPublishing.value = false
  }
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

onMounted(loadEntries)
</script>

<style scoped>
@import '../styles/layout.css';
@import '../styles/utilities.css';
@import '../styles/buttons.css';
@import '../styles/forms.css';
@import '../styles/alerts.css';

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

.gap-2 {
  gap: 0.5rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.preview-content {
  max-height: 500px;
  overflow-y: auto;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.preview-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-size: 0.875rem;
}

.pdf-preview {
  padding: 2rem;
  text-align: center;
}

.btn.active {
  background-color: #0d6efd;
  color: white;
}

.list-group-item {
  border: 1px solid rgba(0, 0, 0, 0.125);
}
</style>
