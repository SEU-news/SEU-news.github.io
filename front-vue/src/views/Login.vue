<template>
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
import { useRouter, useRoute } from 'vue-router'
import { login } from '../api/auth.js'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const message = ref('')

async function handleSubmit() {
  try {
    const res = await login({ username: username.value, password: password.value })

    if (res.success) {
      // 使用 Notification API 显示成功消息
      showNotification('登录成功！')

      // 保存用户信息到 Pinia Store
      authStore.setUser(res.user)

      // 保存到 localStorage（用于刷新后恢复）
      localStorage.setItem('user', JSON.stringify(res.user))

      // 跳转到首页或 redirect 目标
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      message.value = '用户名或密码错误'
    }
  } catch (err) {
    message.value = '服务器连接失败'
  }
}

// 显示通知消息的函数
function showNotification(text) {
  // 检查浏览器是否支持 Notification API
  if ('Notification' in window) {
    // 请求通知权限
    if (Notification.permission === 'granted') {
      new Notification(text)
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification(text)
        }
      })
    }
  } else {
    // 如果浏览器不支持 Notification API，回退到 alert
    alert(text)
  }
}
</script>

<style scoped>
/* 引入基础样式 */
@import '../styles/layout.css';
@import '../styles/utilities.css';
@import '../styles/buttons.css';
@import '../styles/forms.css';
@import '../styles/alerts.css';

/* 组件特有样式 */
.container {
  background: #fafafa;
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #666;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e9ecef;
}
</style>