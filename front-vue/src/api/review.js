import api from './index'

/**
 * 修改内容（pending 状态）
 * @param {number} entryId - 内容ID
 * @param {Object} data - { title, short_title, content, type, tag, deadline }
 */
export const modifyEntry = async (entryId, data) => {
  const response = await api.post(`/content/${entryId}/modify/`, data)
  return response.data
}

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
 * @param {Object} data - { entries }
 */
export const previewEdit = async (data) => {
  const response = await api.post('/preview/', data)
  return response.data
}
