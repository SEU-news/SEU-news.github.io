<template>
  <span :class="['role-badge', badgeClass]">{{ roleText }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // User object with role properties
  user: {
    type: Object,
    default: null
  },
  // Role number (0-3)
  role: {
    type: Number,
    default: null
  },
  // Individual permission flags
  hasEditorPerm: {
    type: Boolean,
    default: false
  },
  hasAdminPerm: {
    type: Boolean,
    default: false
  }
})

// Compute role text
const roleText = computed(() => {
  // Priority: user object -> role number -> permission flags
  let editor = props.hasEditorPerm
  let admin = props.hasAdminPerm

  if (props.user) {
    editor = props.user.has_editor_perm || false
    admin = props.user.has_admin_perm || false
  } else if (props.role !== null) {
    editor = (props.role & 1) === 1
    admin = (props.role & 2) === 2
  }

  if (admin && editor) return '超级管理员'
  if (admin) return '管理员'
  if (editor) return '编辑'
  return '普通用户'
})

// Compute badge class
const badgeClass = computed(() => {
  // Priority: user object -> role number -> permission flags
  let editor = props.hasEditorPerm
  let admin = props.hasAdminPerm

  if (props.user) {
    editor = props.user.has_editor_perm || false
    admin = props.user.has_admin_perm || false
  } else if (props.role !== null) {
    editor = (props.role & 1) === 1
    admin = (props.role & 2) === 2
  }

  if (admin && editor) return 'badge-super'
  if (admin) return 'badge-admin'
  if (editor) return 'badge-editor'
  return 'badge-user'
})
</script>

<style scoped>
.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.role-badge.badge-editor {
  background-color: #3498db;
  color: white;
}

.role-badge.badge-admin {
  background-color: #e74c3c;
  color: white;
}

.role-badge.badge-super {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.role-badge.badge-user {
  background-color: #95a5a6;
  color: white;
}
</style>
