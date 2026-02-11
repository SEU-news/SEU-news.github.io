import api from './index'

/**
 * 获取内容列表（分页）
 * /manage/list 页面使用，只显示活跃状态
 * @param {Object} params - { page, page_size, q, sort, order }
 */
export const getEntries = async (params = {}) => {
  const { page = 1, page_size = 10, q = '', sort = 'created_at', order = 'desc', ...rest } = params
  const response = await api.get('/content/', {
    params: { page, page_size, q, sort, order, ...rest }
  })
  return response.data
}

/**
 * 获取管理员内容列表（分页）
 * /manage/admin/entries 页面使用，显示所有状态
 * @param {Object} params - { page, page_size, q, sort, order }
 */
export const getAdminEntries = async (params = {}) => {
  const { page = 1, page_size = 10, q = '', sort = 'created_at', order = 'desc', ...rest } = params
  const response = await api.get('/admin/entries/', {
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
    const response = await api.post('/content/', data)
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
    const response = await api.patch(`/content/${entryId}/`, data)
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
  const response = await api.post('/upload_image/', formData, {
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
  const response = await api.post('/paste/', data)
  return response.data
}

/**
 * 删除内容
 * @param {number} entryId - 内容ID
 */
export const deleteEntry = async (entryId) => {
  const response = await api.delete(`/content/${entryId}/`)
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
 * 更新内容状态
 * @param {number} entryId - 内容ID
 * @param {string} status - 目标状态
 */
export const updateEntryStatus = async (entryId, status) => {
  const response = await api.post(`/content/${entryId}/status/`, { status })
  return response.data
}

/**
 * 修改内容（用于提交审核）
 * @param {number} entryId - 内容ID
 * @param {Object} data - { title, short_title, content, type, tag, deadline }
 */
export const modifyEntry = async (entryId, data = {}) => {
  console.log(`modifyEntry API call with id=${entryId}, data:`, data)
  try {
    const response = await api.post(`/content/${entryId}/modify/`, data)
    console.log('modifyEntry full response:', response)
    console.log('modifyEntry response.data:', response.data)
    return response.data
  } catch (error) {
    console.error('modifyEntry error:', error)
    console.error('modifyEntry error response:', error.response?.data)
    throw error
  }
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
