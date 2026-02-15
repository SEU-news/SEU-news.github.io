import api from './index'

/**
 * 获取用户列表
 * @param {Object} params - 分页和排序参数
 *   - page: 页码（默认 1）
 *   - page_size: 每页条数（默认 10）
 *   - sort: 排序字段（默认 'created_at'）
 *   - order: 排序方向 'asc'|'desc'（默认 'desc'）
 *   - q: 搜索关键词
 *   - role: 权限筛选
 */
export const getUsers = async (params = {}) => {
  const response = await api.get('/admin/users/', { params })
  return response.data
}

/**
 * 编辑用户权限
 * @param {number} userId - 用户ID
 * @param {string} action - 'add'|'remove'
 * @param {string} permission - 'editor'|'admin'
 */
export const editUserRole = async (userId, action, permission) => {
  const response = await api.post(`/admin/users/${userId}/role/`, {
    action,
    permission
  })
  return response.data
}

/**
 * 编辑用户信息
 * @param {number} userId - 用户ID
 * @param {Object} data - 用户信息
 */
export const editUser = async (userId, data) => {
  const response = await api.patch(`/admin/users/${userId}/info/`, data)
  return response.data
}

/**
 * 获取管理员面板数据
 */
export const getAdminData = async () => {
  const response = await api.get('/admin/dashboard/')
  return response.data
}
