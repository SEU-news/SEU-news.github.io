import api from './index'

/**
 * 发布内容
 * @param {Object} data - { format, entries, template }
 */
export const publishContent = async (data) => {
  const response = await api.post('/publish/', data)
  return response.data
}

/**
 * 生成 Typst 格式
 * @param {string} date - 日期
 */
export const generateTypst = async (date) => {
  const response = await api.get(`/typst/${date}/`)
  return response.data
}

/**
 * 生成 LaTeX 格式
 * @param {string} date - 日期
 */
export const generateLatex = async (date) => {
  const response = await api.get(`/latex/${date}/`)
  return response.data
}
