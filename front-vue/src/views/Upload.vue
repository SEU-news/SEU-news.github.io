<template>
  <div class="container mt-5" style="max-width: 800px">
    <h2>上传纯文本消息</h2>

    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <form @submit.prevent="handleSubmit">
      <div class="form-group mb-3">
        <label>标题 <span class="text-danger">*</span></label>
        <input
          v-model="formData.title"
          type="text"
          class="form-control"
          required
          maxlength="200"
          placeholder="请输入标题"
        />
      </div>

      <div class="form-group mb-3">
        <label>短标题</label>
        <input
          v-model="formData.short_title"
          type="text"
          class="form-control"
          maxlength="100"
          placeholder="短标题（可选）"
        />
      </div>

      <div class="form-group mb-3">
        <label>链接 <span class="text-danger">*</span></label>
        <input
          v-model="formData.link"
          type="url"
          class="form-control"
          required
          placeholder="请输入相关链接"
        />
      </div>

      <div class="form-group mb-3">
        <label>内容 <span class="text-danger">*</span></label>
        <textarea
          v-model="formData.content"
          class="form-control"
          rows="8"
          required
          placeholder="请输入详细内容"
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
        <button type="submit" class="btn btn-primary" :disabled="isLoading">
          {{ isLoading ? '上传中...' : '上传' }}
        </button>
        <button type="button" class="btn btn-secondary" @click="goBack">
          返回
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadText } from '../api/content.js'

const router = useRouter()

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
const isLoading = ref(false)

// 提交表单
async function handleSubmit() {
  isLoading.value = true
  message.value = ''

  // 处理 tag：将逗号分隔的字符串转换为数组
  let tags = []
  if (formData.value.tag && formData.value.tag.trim()) {
    tags = formData.value.tag
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0)
  }

  const payload = {
    title: formData.value.title,
    short_title: formData.value.short_title || formData.value.title.slice(0, 100),
    link: formData.value.link,
    content: formData.value.content,
    type: formData.value.type,
    tag: JSON.stringify(tags),
    deadline: formData.value.deadline || null,
  }

  console.log('Upload payload:', payload)

  try {
    await uploadText(payload)

    alert('上传成功！')

    // 2秒后返回管理页
    setTimeout(() => {
      router.push('/manage')
    }, 2000)
  } catch (err) {
    showMessage('上传失败：' + err.message, 'alert-danger')
  } finally {
    isLoading.value = false
  }
}

// 返回上一页
function goBack() {
  router.back()
}

// 显示消息
function showMessage(msg, cls = 'alert-info') {
  message.value = msg
  messageClass.value = cls
  setTimeout(() => { message.value = '' }, 5000)
}
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
</style>
