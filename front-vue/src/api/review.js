import api from './index'

/**
 * 审核内容
 * @param {number} entryId - 内容ID
 * @param {Object} data - { action } - action: 'approve'|'reject'
 */
export const reviewEntry = async (entryId, data) => {
  const response = await api.post(`/content/${entryId}/review/`, data)
  return response.data
}

/**
 * 预览编辑
 * @param {Object} data - { content_ids }
 */
export const previewEdit = async (data) => {
  const response = await api.post('/preview/', data)
  return response.data
}
