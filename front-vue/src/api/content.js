import api from './index'

/**
 * 获取内容列表（分页）
 * 支持普通用户和管理员：
 * - 普通用户：只能看到活跃状态（排除 terminated）
 * - 管理员：可以看到所有状态（包括 terminated）
 * @param {Object} params - { page, page_size, q, sort, order, status, type }
 */
export const getEntries = async (params = {}) => {
  const { page = 1, page_size = 10, q = '', sort = 'created_at', order = 'desc', ...rest } = params
  const response = await api.get('/contents/', {
    params: { page, page_size, q, sort, order, ...rest }
  })
  return response.data
}

/**
 * 上传纯文本内容（创建内容）
 * @param {Object} data - { title, short_title, content, link, type, tag, deadline }
 */
export const uploadText = async (data) => {
  console.log('uploadText API call with data:', data)
  try {
    const response = await api.post('/content/create/', data)
    console.log('uploadText full response:', response)
    console.log('uploadText response.data:', response.data)
    console.log('uploadText response.data type:', typeof response.data)
    return response.data
  } catch (error) {
    console.error('uploadText error:', error)
    console.error('uploadText error response:', error.response?.data)
    throw error
  }
}

/**
 * 更新内容
 * @param {number} entryId - 内容ID
 * @param {Object} data - { title, short_title, content, link, type, tag, deadline }
 */
export const updateEntry = async (entryId, data) => {
  console.log(`updateEntry API call with id=${entryId}, data:`, data)
  try {
    const response = await api.patch(`/content/${entryId}/modify/`, data)
    console.log('updateEntry full response:', response)
    console.log('updateEntry response.data:', response.data)
    return response.data
  } catch (error) {
    console.error('updateEntry error:', error)
    console.error('updateEntry error response:', error.response?.data)
    throw error
  }
}

/**
 * 上传图片
 * @param {FormData} formData - 包含图片文件的表单数据
 */
export const uploadImage = async (formData) => {
  formData.append('upload_type', 'image')
  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

/**
 * 粘贴 URL
 * @param {Object} data - { url }
 */
export const pasteUrl = async (data) => {
  const response = await api.post('/upload/', {
    upload_type: 'url',
    ...data
  })
  return response.data
}

/**
 * 撤回内容
 * @param {number} entryId - 内容ID
 */
export const recallEntry = async (entryId) => {
  const response = await api.post(`/content/${entryId}/recall/`)
  return response.data
}

/**
 * 取消内容（终止流程）
 * @param {number} entryId - 内容ID
 */
export const cancelEntry = async (entryId) => {
  const response = await api.post(`/content/${entryId}/cancel/`)
  return response.data
}

/**
 * 获取内容详情
 * @param {number} entryId - 内容ID
 */
export const getEntryDetail = async (entryId) => {
  const response = await api.get(`/content/${entryId}/`)
  return response.data
}

/**
 * 搜索内容
 * @param {string} query - 搜索关键词
 */
export const searchEntries = async (query) => {
  const response = await api.post('/search/', { q: query })
  return response.data
}

/**
 * 提交审核（纯状态转换）
 * @param {number} entryId - 内容ID
 * @returns {Promise<{success: boolean, message: string}>}
 */
export const submitEntry = async (entryId) => {
  const response = await api.post(`/content/${entryId}/submit/`)
  return response.data
}

/**
 * 统一上传 API
 * @param {FormData} formData - 上传数据
 */
export const unifiedUpload = async (formData) => {
  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

/**
 * 管理员强制修改内容状态
 * @param {number} entryId - 内容ID
 * @param {string} status - 新状态值 (draft/pending/reviewed/rejected/published/terminated)
 * @param {string} reason - 状态变更原因（可选）
 * @returns {Promise<{success: boolean, message: string, data: Object}>}
 */
export const adminStatusUpdate = async (entryId, status, reason = '') => {
  const response = await api.post(`/content/${entryId}/admin_status/`, {
    status,
    reason
  })
  return response.data
}
