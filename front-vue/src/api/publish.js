import api from './index'

// ==================== 内容查询（使用 ContentListAPIView） ====================

/**
 * 按日期范围查询已发布内容
 * @param {string} startDate - 开始日期 (YYYY-MM-DD)
 * @param {string} endDate - 结束日期 (YYYY-MM-DD)
 */
export const queryPublishedByDateRange = async (startDate, endDate) => {
  const response = await api.get('/contents/', {
    params: {
      publish_start_date: startDate,
      publish_end_date: endDate,
      only_published: 'true',
      page_size: 1000
    }
  })
  return response.data
}

/**
 * 查询 DDL 内容（基于结束日期）
 * @param {string} endDate - 结束日期 (YYYY-MM-DD)
 */
export const queryDDLByDate = async (endDate) => {
  const response = await api.get('/contents/', {
    params: {
      deadline_end_date: endDate,
      only_published: 'true',
      page_size: 1000
    }
  })
  return response.data
}

// ==================== 文档导出 ====================

/**
 * 生成 PDF（支持按日期或按选中内容）
 * @param {Object} options - { date?: string, content_ids?: number[] }
 */
export const generatePDF = async (options) => {
  const response = await api.post('/v1/export/pdf/', options)
  return response.data
}

/**
 * 生成 Typst 格式文档
 * @param {string} date - 日期 (YYYY-MM-DD)
 */
export const generateTypst = async (date) => {
  const response = await api.get('/v1/export/typst/', { params: { date } })
  return response.data
}

/**
 * 生成 LaTeX 格式文档
 * @param {string} date - 日期 (YYYY-MM-DD)
 */
export const generateLatex = async (date) => {
  const response = await api.get('/v1/export/latex/', { params: { date } })
  return response.data
}

/**
 * 获取导出数据
 * @param {string} date - 日期 (YYYY-MM-DD)
 */
export const getExportData = async (date) => {
  const response = await api.get('/v1/export/data/', { params: { date } })
  return response.data
}

// ==================== 发布管理 ====================

/**
 * 发布内容（批量）
 * @param {Object} data - { content_ids: number[] }
 */
export const publishContent = async (data) => {
  const response = await api.post('/publish/', data)
  return response.data
}
