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

    // 调试日志
    console.log('=== API 请求 ===')
    console.log('URL:', config.baseURL + config.url)
    console.log('Method:', config.method)
    console.log('Headers:', config.headers)
    console.log('Data:', config.data)
    console.log('BaseURL:', config.baseURL)
    console.log('================')

    return config
  },
  (error) => {
    console.error('=== 请求错误 ===', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 调试日志
    console.log('=== API 响应 ===')
    console.log('URL:', response.config.url)
    console.log('Status:', response.status)
    console.log('Data:', response.data)
    console.log('Headers:', response.headers)
    console.log('================')

    return response
  },
  (error) => {
    // 调试日志
    console.error('=== API 错误 ===')
    console.error('URL:', error.config?.url)
    console.error('Status:', error.response?.status)
    console.error('Data:', error.response?.data)
    console.error('Message:', error.message)
    console.error('================')

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
