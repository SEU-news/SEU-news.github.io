<template>
  <nav class="navbar">
    <div class="nav-links">
      <router-link to="/" class="nav-link">首页</router-link>
      <router-link to="/news" class="nav-link">至善新生</router-link>
      <router-link to="/about" class="nav-link">关于</router-link>
    </div>

    <div
      class="user-info-wrapper"
      v-if="authStore.isLoggedIn"
      @mouseenter="showTooltip = true"
      @mouseleave="showTooltip = false"
    >
      <div class="user-avatar">
        {{ getInitial }}
      </div>

      <div class="tooltip-bridge"></div>

      <div class="tooltip" v-show="showTooltip">
        <div class="tooltip-header">
          <div class="tooltip-avatar">{{ getInitial }}</div>
          <div class="tooltip-header-info">
            <h4 class="tooltip-username">{{ authStore.user.username }}</h4>
            <span :class="['user-role-badge', getRoleBadgeClass]">
              {{ getRoleText }}
            </span>
          </div>
        </div>

        <hr class="tooltip-divider" />

        <div class="user-info-grid">
          <div class="info-item">
            <label>用户名</label>
            <div class="info-value">{{ authStore.user.username }}</div>
          </div>
          <div class="info-item">
            <label>真实姓名</label>
            <div class="info-value">{{ authStore.user.realname || '-' }}</div>
          </div>
          <div class="info-item">
            <label>学号</label>
            <div class="info-value">{{ authStore.user.student_id || '-' }}</div>
          </div>
          <div class="info-item info-item-role">
            <label>权限</label>
            <RoleBadge :user="authStore.user" />
          </div>
        </div>

        <button class="logout-btn" @click="handleLogout">
          <span>退出登录</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { logout } from '@/api/auth'
import RoleBadge from './RoleBadge.vue'

const router = useRouter()
const authStore = useAuthStore()
const showTooltip = ref(false)

const getInitial = computed(() => {
  return authStore.user.username ? authStore.user.username.charAt(0).toUpperCase() : '?'
})

const getRoleText = computed(() => {
  if (authStore.hasAdminPerm && authStore.hasEditorPerm) return '超级管理员'
  if (authStore.hasAdminPerm) return '管理员'
  if (authStore.hasEditorPerm) return '编辑'
  return '普通用户'
})

const getRoleBadgeClass = computed(() => {
  if (authStore.hasAdminPerm && authStore.hasEditorPerm) return 'badge-super'
  if (authStore.hasAdminPerm) return 'badge-admin'
  if (authStore.hasEditorPerm) return 'badge-editor'
  return 'badge-user'
})

const handleLogout = async () => {
  try {
    await logout()
    authStore.clearUser()
    showTooltip.value = false
    router.push('/')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

<style scoped>
.navbar {
  padding: 1rem 2rem;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-links {
  display: flex;
  align-items: center;
}

.nav-link {
  margin: 0 1rem;
  text-decoration: none;
  color: #666;
  font-weight: 500;
  transition: color 0.2s;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.nav-link:hover {
  color: #667eea;
  background: #fafafa;
}

.nav-link.router-link-active {
  color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 1px 3px rgba(102, 126, 234, 0.1);
}

.user-info-wrapper {
  position: relative;
  cursor: pointer;
}

.user-avatar {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
  color: white;
  transition: transform 0.2s, box-shadow 0.2s;
  transform-origin: top center;
}

.user-avatar:hover {
  transform: scale(1.20);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.tooltip-bridge {
  position: absolute;
  top: 40px;
  right: 0;
  width: 40px;
  height: 8px;
  cursor: pointer;
}

.tooltip {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 20px;
  z-index: 1000;
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 16px;
}

.tooltip-avatar {
  font-size: 2rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
  color: white;
}

.tooltip-header-info {
  flex: 1;
  min-width: 0;
}

.tooltip-username {
  margin: 0 0 6px 0;
  font-size: 1.1rem;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.user-role-badge.badge-editor {
  background-color: #3498db;
  color: white;
}

.user-role-badge.badge-admin {
  background-color: #e74c3c;
  color: white;
}

.user-role-badge.badge-super {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.user-role-badge.badge-user {
  background-color: #95a5a6;
  color: white;
}

.tooltip-divider {
  border: none;
  border-top: 1px solid #e9ecef;
  margin: 0 0 16px 0;
}

.user-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 500;
}

.info-value {
  font-size: 0.9rem;
  color: #2c3e50;
  font-weight: 500;
  padding: 6px 0;
}

.info-item-role {
  align-items: flex-start;
}

.info-item-role :deep(.role-badge) {
  margin-top: 4px;
}

.logout-btn {
  width: 100%;
  padding: 10px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.logout-btn:active {
  transform: translateY(0);
}
</style>
