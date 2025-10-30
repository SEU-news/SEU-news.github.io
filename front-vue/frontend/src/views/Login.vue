<template>
  <head>
    <title>Login</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/css/bootstrap.min.css">
  </head>

  <div class="container mt-5" style="max-width: 500px">
    <h2>登录</h2>

    <!-- 提示信息 -->
    <div v-if="message" class="alert alert-info">
      {{ message }}
    </div>

    <form @submit.prevent="handleSubmit">
      <div class="form-group mb-3">
        <label>用户名</label>
        <input v-model="username" type="text" class="form-control" required />
      </div>

      <div class="form-group mb-3">
        <label>密码</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>

      <button type="submit" class="btn btn-primary">登录</button>
      <RouterLink to="/register" class="btn btn-secondary ms-2">
        注册
      </RouterLink>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/user.js'

const router = useRouter()
const username = ref('')
const password = ref('')
const message = ref('')

async function handleSubmit() {
  try {
    const res = await login(username.value, password.value)
    if (res.success) {
      message.value = '登录成功！'
      // 例如保存 token
      localStorage.setItem('token', res.token)
      // 跳转主页
      router.push('/')
    } else {
      message.value = '用户名或密码错误'
    }
  } catch (err) {
    message.value = '服务器连接失败'
  }
}
</script>

<style>
body {
  background-color: #f8f9fa;
}
</style>
