import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAdminLayoutStore = defineStore('adminLayout', () => {
  const isSidebarCollapsed = ref(false)

  function restoreSidebarState() {
    const savedState = localStorage.getItem('adminSidebarCollapsed')
    isSidebarCollapsed.value = savedState === 'true'
  }

  function toggleSidebar() {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
    localStorage.setItem('adminSidebarCollapsed', isSidebarCollapsed.value)
  }

  const sidebarWidth = computed(() => {
    return isSidebarCollapsed.value ? '64px' : '220px'
  })

  const sidebarTextVisible = computed(() => {
    return !isSidebarCollapsed.value
  })

  return {
    isSidebarCollapsed,
    toggleSidebar,
    restoreSidebarState,
    sidebarWidth,
    sidebarTextVisible
  }
})
