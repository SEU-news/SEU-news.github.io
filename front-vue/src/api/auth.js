import api from './index'

/**
 * 用户登录
 * @param {Object} credentials - { username, password }
 */
export const login = async (credentials) => {
  const formData = new URLSearchParams()
  formData.append('username', credentials.username)
  formData.append('password', credentials.password)

  const response = await api.post('/auth/login/', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
  return response.data
}

/**
 * 用户注册
 * @param {Object} userData - { username, password, realname, student_id }
 */
export const register = async (userData) => {
  const response = await api.post('/auth/register/', userData)
  return response.data
}

/**
 * 用户登出
 */
export const logout = async () => {
  const response = await api.post('/auth/logout/')
  return response.data
}

/**
 * 修改密码
 * @param {Object} data - { old_password, new_password }
 */
export const changePassword = async (data) => {
  const response = await api.post('/auth/password/', data)
  return response.data
}

/**
 * 获取当前用户信息
 */
export const getCurrentUser = async () => {
  const response = await api.get('/auth/user/')
  return response.data
}