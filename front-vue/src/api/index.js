import axios from 'axios'
import { useAuthStore } from '../stores/auth'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  withCredentials: true, // 支持跨域携带 cookies
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const authStore = useAuthStore()

    // 401 未授权 → 自动登出
    if (error.response && error.response.status === 401) {
      authStore.clearUser()
      localStorage.removeItem('user')
      window.location.href = '/login'
    }

    // 403 权限不足 → 显示提示
    if (error.response && error.response.status === 403) {
      alert('权限不足')
    }

    return Promise.reject(error)
  }
)

export default apiClient
