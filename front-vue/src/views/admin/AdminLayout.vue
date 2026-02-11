<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="admin-sidebar" :class="{ collapsed: adminLayoutStore.isSidebarCollapsed }">
      <!-- 收缩按钮 -->
      <button
        class="sidebar-toggle"
        @click="adminLayoutStore.toggleSidebar"
        :title="adminLayoutStore.isSidebarCollapsed ? '展开侧边栏' : '收缩侧边栏'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="toggle-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <!-- 用户信息 -->
      <div class="admin-sidebar-header" >
        <h3 class="sidebar-text">超级管理后台</h3>
        <p class="sidebar-text">欢迎您，管理员 {{ adminUsername }}</p>
      </div>

      <!-- 导航 -->
      <nav class="admin-sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.id"
          :to="item.route"
          class="admin-nav-item"
          active-class="active"
        >
          <i>{{ item.icon }}</i>
          <span class="nav-text">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- 底部按钮 -->
      <div class="admin-sidebar-footer">
        <router-link
          v-for="item in footerItems"
          :key="item.id"
          :to="item.route"
          class="footer-link"
          active-class="active"
          :title="adminLayoutStore.isSidebarCollapsed ? item.label : ''"
        >
          <i>{{ item.icon }}</i>
          <span class="footer-text">{{ item.label }}</span>
        </router-link>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="admin-main" :style="{ marginLeft: adminLayoutStore.sidebarWidth }">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useAdminLayoutStore } from '../../stores/admin-layout.js'

const authStore = useAuthStore()
const adminLayoutStore = useAdminLayoutStore()

const adminUsername = computed(() => {
  return authStore.user?.realname || authStore.user?.username || '管理员'
})

// 导航配置
const navItems = [
  {
    id: 'dashboard',
    label: '仪表板',
    icon: '📊',
    route: '/manage/admin/dashboard'
  },
  {
    id: 'users',
    label: '用户管理',
    icon: '🧑',
    route: '/manage/admin/users'
  },
  {
    id: 'entries',
    label: '条目管理',
    icon: '📋',
    route: '/manage/admin/entries'
  }
]

const footerItems = [
  {
    id: 'manage-quick',
    label: '管理中心',
    icon: '🗃️',
    route: '/manage'
  },
  {
    id: 'home',
    label: '返回主页',
    icon: '🌈',
    route: '/'
  }
]

onMounted(() => {
  adminLayoutStore.restoreSidebarState()
})
</script>

<style scoped>
@import '../../styles/admin.css';

/* Ensure router-link-active works with scoped styles */
.admin-sidebar-nav :deep(.router-link-active),
.admin-sidebar-nav :deep(.active) {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-left-color: #3498db;
  font-weight: 500;
}

</style>
