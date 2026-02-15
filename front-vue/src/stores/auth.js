import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref({
    id: null,
    username: null,
    role: null,
    realname: null,
    student_id: null,
    avatar: null,
    has_editor_perm: false,
    has_admin_perm: false
  })
  const token = ref(localStorage.getItem('token') || null)
  const isLoggedIn = ref(false)

  // Actions
  function setUser(userData) {
    user.value = userData
    isLoggedIn.value = true
    if (userData.token) {
      token.value = userData.token
      localStorage.setItem('token', userData.token)
    }
  }

  function clearUser() {
    user.value = {
      id: null,
      username: null,
      role: null,
      realname: null,
      student_id: null,
      avatar: null,
      has_editor_perm: false,
      has_admin_perm: false
    }
    token.value = null
    isLoggedIn.value = false
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  function restoreState() {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
      isLoggedIn.value = true
    }
  }

  // Getters - 直接使用 API 返回的权限字段
  const hasEditorPerm = computed(() => {
    return !!user.value.has_editor_perm
  })

  const hasAdminPerm = computed(() => {
    return !!user.value.has_admin_perm
  })

  return {
    user,
    token,
    isLoggedIn,
    hasEditorPerm,
    hasAdminPerm,
    setUser,
    clearUser,
    restoreState
  }
})