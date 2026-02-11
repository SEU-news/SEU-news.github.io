import api from './index'

/**
 * 描述内容
 * @param {number} entryId - 内容ID
 * @param {Object} data - { title, short_title, content, type, tag }
 */
export const describeEntry = async (entryId, data) => {
  const response = await api.post(`/content/${entryId}/describe/`, data)
  return response.data
}

/**
 * 审核内容
 * @param {number} entryId - 内容ID
 * @param {Object} data - { action, comment } - action: 'approve'|'reject'
 */
export const reviewEntry = async (entryId, data) => {
  const response = await api.post(`/content/${entryId}/review/`, data)
  return response.data
}

/**
 * 取消内容
 * @param {number} entryId - 内容ID
 */
export const cancelEntry = async (entryId) => {
  const response = await api.post(`/content/${entryId}/cancel/`)
  return response.data
}

/**
 * 预览编辑
 * @param {Object} data - { entries }
 */
export const previewEdit = async (data) => {
  const response = await api.post('/preview/', data)
  return response.data
}
