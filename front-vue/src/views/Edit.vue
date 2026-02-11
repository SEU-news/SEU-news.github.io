<template>
  <div class="container mt-5" style="max-width: 800px">
    <h2>编辑内容</h2>

    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>

    <form v-else @submit.prevent="handleSubmit">
      <div class="form-group mb-3">
        <label>标题 <span class="text-danger">*</span></label>
        <input
          v-model="formData.title"
          type="text"
          class="form-control"
          required
          maxlength="200"
        />
      </div>

      <div class="form-group mb-3">
        <label>短标题</label>
        <input
          v-model="formData.short_title"
          type="text"
          class="form-control"
          maxlength="100"
        />
      </div>

      <div class="form-group mb-3">
        <label>链接 <span class="text-danger">*</span></label>
        <input
          v-model="formData.link"
          type="url"
          class="form-control"
          required
        />
      </div>

      <div class="form-group mb-3">
        <label>内容 <span class="text-danger">*</span></label>
        <textarea
          v-model="formData.content"
          class="form-control"
          rows="8"
          required
        ></textarea>
      </div>

      <div class="form-group mb-3">
        <label>类型 <span class="text-danger">*</span></label>
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

      <div class="form-group mb-3">
        <label>标签</label>
        <input
          v-model="formData.tag"
          type="text"
          class="form-control"
          placeholder="多个标签用逗号分隔（可选）"
        />
        <small class="text-muted">例如：活动, 公告, 通知</small>
      </div>

      <div class="form-group mb-3">
        <label>截止日期</label>
        <input
          v-model="formData.deadline"
          type="date"
          class="form-control"
        />
      </div>

      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? '保存中...' : '保存修改' }}
        </button>
        <button type="button" class="btn btn-secondary" @click="goBack">
          取消
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getEntryDetail, updateEntry } from '../api/content.js'

const router = useRouter()
const route = useRoute()
const entryId = route.params.id

// 表单数据
const formData = ref({
  title: '',
  short_title: '',
  link: '',
  content: '',
  type: '',
  tag: '',
  deadline: '',
})

// 状态
const message = ref('')
const messageClass = ref('alert-info')
const isLoading = ref(true)
const isSubmitting = ref(false)

// 加载条目详情
async function loadEntry() {
  try {
    const data = await getEntryDetail(entryId)

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
    formData.value = {
      title: data.title,
      short_title: data.short_title,
      link: data.link,
      content: data.content,
      type: data.type,
      tag: tags,
      deadline: data.deadline || '',
    }
  } catch (err) {
    showMessage('加载失败：' + err.message, 'alert-danger')
  } finally {
    isLoading.value = false
  }
}

// 提交表单
async function handleSubmit() {
  isSubmitting.value = true
  message.value = ''

  // 处理 tag：将逗号分隔的字符串转换为数组
  let tags = []
  if (formData.value.tag && formData.value.tag.trim()) {
    tags = formData.value.tag
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0)
  }

  try {
    // 使用 updateEntry API 更新内容
    await updateEntry(entryId, {
      title: formData.value.title,
      short_title: formData.value.short_title || formData.value.title.slice(0, 100),
      link: formData.value.link,
      content: formData.value.content,
      type: formData.value.type,
      tag: JSON.stringify(tags),
      deadline: formData.value.deadline || null,
    })

    alert('保存成功！')

    // 2秒后返回
    setTimeout(() => {
      router.push('/manage')
    }, 2000)
  } catch (err) {
    showMessage('保存失败：' + err.message, 'alert-danger')
  } finally {
    isSubmitting.value = false
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

onMounted(loadEntry)
</script>

<style scoped>
@import '../styles/layout.css';
@import '../styles/utilities.css';
@import '../styles/buttons.css';
@import '../styles/forms.css';
@import '../styles/alerts.css';

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

form {
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
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
</style>
