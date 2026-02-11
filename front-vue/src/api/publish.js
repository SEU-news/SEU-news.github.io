import api from './index'

/**
 * 根据选中的内容ID生成PDF
 * @param {Array<number>} contentIds - 内容ID列表
 */
export const generatePDFFromSelection = async (contentIds) => {
  const response = await api.post('/publish/pdf_from_selection/', { content_ids: contentIds })
  return response.data
}

/**
 * 按日期查询已发布内容
 * @param {string} date - 日期 (YYYY-MM-DD)
 */
export const queryPublishedByDate = async (date) => {
  const response = await api.get(`/publish/query/${date}/`)
  return response.data
}

/**
 * 按日期范围查询已发布内容
 * @param {string} startDate - 开始日期 (YYYY-MM-DD)
 * @param {string} endDate - 结束日期 (YYYY-MM-DD)
 */
export const queryPublishedByDateRange = async (startDate, endDate) => {
  const response = await api.get(`/publish/query/`, {
    params: {
      start_date: startDate,
      end_date: endDate
    }
  })
  return response.data
}

/**
 * 查询DDL内容（基于结束日期，用于预览）
 * @param {string} endDate - 结束日期 (YYYY-MM-DD)
 */
export const queryDDLByDate = async (endDate) => {
  const response = await api.get('/publish/ddl/', {
    params: {
      end_date: endDate
    }
  })
  return response.data
}

/**
 * 发布内容（保留用于管理页面）
 * @param {Object} data - { content_ids, entries }
 */
export const publishContent = async (data) => {
  const response = await api.post('/publish/', data)
  return response.data
}
