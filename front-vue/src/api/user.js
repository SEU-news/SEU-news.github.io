// 命名导出
export const login = async (credentials) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ success: true, user: { id: 1, name: '测试用户' } })
    }, 1000)
  })
}

export const logout = async () => {
  return Promise.resolve({ success: true })
}
