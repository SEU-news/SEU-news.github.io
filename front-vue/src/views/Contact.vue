<template>
  <div class="contact">
    <h1>联系我们</h1>
    <p class="subtitle">如果您有任何问题或建议，请通过以下方式与我们联系：</p>

    <form class="contact-form" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="name">姓名</label>
        <input id="name" v-model="form.name" type="text" placeholder="请输入您的姓名" required />
      </div>

      <div class="form-group">
        <label for="email">邮箱</label>
        <input id="email" v-model="form.email" type="email" placeholder="请输入您的邮箱" required />
      </div>

      <div class="form-group">
        <label for="message">留言</label>
        <textarea
          id="message"
          v-model="form.message"
          placeholder="请输入您的留言"
          rows="5"
          required
        ></textarea>
      </div>

      <button type="submit" class="btn">提交</button>

      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
    </form>

    <div class="info">
      <h3>其他联系方式</h3>
      <p>📧 邮箱：support@zhishannews.edu.cn</p>
      <p>📞 电话：(+86) 025-1234-5678</p>
      <p>📍 地址：南京市四牌楼校区 至善新声工作室</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 表单数据
const form = ref({
  name: '',
  email: '',
  message: ''
})

// 提交状态
const successMessage = ref('')

// 处理提交
async function handleSubmit() {
  try {
    // 这里发送请求到 Django 后端的 API，例如 /api/contact/
    const response = await fetch('/api/contact/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })

    if (response.ok) {
      successMessage.value = '感谢您的留言，我们会尽快回复您！'
      form.value = { name: '', email: '', message: '' }
    } else {
      successMessage.value = '提交失败，请稍后重试。'
    }
  } catch (err) {
    console.error(err)
    successMessage.value = '网络错误，请检查连接。'
  }
}
</script>

<style scoped>
/* 引入基础样式 */
@import '../styles/layout.css';
@import '../styles/buttons.css';
@import '../styles/forms.css';

/* 组件特有样式 */
.contact {
  max-width: 600px;
  margin: 3rem auto;
  padding: 2rem;
  text-align: left;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.subtitle {
  color: #555;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

input,
textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

input:focus,
textarea:focus {
  border-color: #007bff;
  outline: none;
}

.btn {
  display: block;
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  font-size: 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn:hover {
  background-color: #0056b3;
}

.success-message {
  margin-top: 1rem;
  color: green;
  font-weight: 600;
}

.info {
  margin-top: 3rem;
  border-top: 1px solid #eee;
  padding-top: 1rem;
  color: #444;
}

.info p {
  margin: 0.5rem 0;
}
</style>
