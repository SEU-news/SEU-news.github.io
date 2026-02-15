<template>
  <div class="container mt-5" style="max-width: 500px">
    <h2>用户注册</h2>

    <!-- 提示信息 -->
    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <form @submit.prevent="handleSubmit">
      <div class="form-group mb-3">
        <label>用户名 <span class="text-danger">*</span></label>
        <input v-model="username" type="text" class="form-control" required minlength="3" maxlength="30" />
        <small class="form-text text-muted">3-30 个字符</small>
      </div>

      <div class="form-group mb-3">
        <label>真实姓名 <span class="text-danger">*</span></label>
        <input v-model="realname" type="text" class="form-control" required />
      </div>

      <div class="form-group mb-3">
        <label>学号 <span class="text-danger">*</span></label>
        <input v-model="studentId" type="text" class="form-control" required />
      </div>

      <div class="form-group mb-3">
        <label>密码 <span class="text-danger">*</span></label>
        <input v-model="password" type="password" class="form-control" required minlength="6" />
        <small class="form-text text-muted">至少 6 个字符</small>
      </div>

      <div class="form-group mb-3">
        <label>确认密码 <span class="text-danger">*</span></label>
        <input v-model="confirmPassword" type="password" class="form-control" required />
        <small v-if="passwordMismatch" class="text-danger">密码不一致</small>
      </div>

      <button type="submit" class="btn btn-primary" :disabled="isLoading || passwordMismatch">
        {{ isLoading ? '注册中...' : '注册' }}
      </button>
      <RouterLink to="/login" class="btn btn-secondary ms-2">
        返回登录
      </RouterLink>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/auth.js'

const router = useRouter()
const username = ref('')
const realname = ref('')
const studentId = ref('')
const password = ref('')
const confirmPassword = ref('')
const message = ref('')
const isLoading = ref(false)

// 密码是否匹配
const passwordMismatch = computed(() => {
  return password.value && confirmPassword.value && password.value !== confirmPassword.value
})

// 消息类型
const messageClass = ref('alert-info')

async function handleSubmit() {
  if (passwordMismatch.value) {
    message.value = '密码不一致，请检查'
    messageClass.value = 'alert-danger'
    return
  }

  isLoading.value = true
  message.value = ''

  try {
    await register({
      username: username.value,
      realname: realname.value,
      student_id: studentId.value,
      password: password.value,
    })

    message.value = '注册成功！请等待管理员审核'
    messageClass.value = 'alert-success'

    // 3秒后跳转到登录页
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (err) {
    message.value = err.message || '注册失败，请稍后重试'
    messageClass.value = 'alert-danger'
  } finally {
    isLoading.value = false
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

.text-danger {
  color: #dc3545;
}
</style>
