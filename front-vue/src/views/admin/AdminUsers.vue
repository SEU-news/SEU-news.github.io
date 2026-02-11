<template>
  <div>
    <div class="admin-header">
      <h2>用户管理</h2>
      <p>管理系统用户与权限</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-spinner">
      <span>加载中...</span>
    </div>

    <!-- Toolbar -->
    <div class="users-toolbar">
      <select v-model="roleFilter" class="form-select" @change="filterUsers">
        <option value="">全部权限</option>
        <option value="0">普通用户</option>
        <option value="1">编辑</option>
        <option value="2">管理员</option>
        <option value="3">超级管理员</option>
      </select>
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索用户名或学号..."
          @input="filterUsers"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && users.length === 0" class="empty-state">
      <i>👥</i>
      <h3>暂无用户</h3>
      <p>没有找到符合条件的用户</p>
    </div>

    <!-- Users Table & Pagination -->
    <template v-if="!loading && users.length > 0">
      <!-- Users Table -->
      <div class="users-table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th @click="handleSort('id')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'id' }">
                <span class="header-content">
                  ID
                  <span class="sort-icon" v-html="getSortIcon('id')"></span>
                </span>
              </th>
              <th @click="handleSort('username')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'username' }">
                <span class="header-content">
                  用户名
                  <span class="sort-icon" v-html="getSortIcon('username')"></span>
                </span>
              </th>
              <th @click="handleSort('realname')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'realname' }">
                <span class="header-content">
                  真实姓名
                  <span class="sort-icon" v-html="getSortIcon('realname')"></span>
                </span>
              </th>
              <th @click="handleSort('student_id')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'student_id' }">
                <span class="header-content">
                  学号
                  <span class="sort-icon" v-html="getSortIcon('student_id')"></span>
                </span>
              </th>
              <th @click="handleSort('role')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'role' }">
                <span class="header-content">
                  权限
                  <span class="sort-icon" v-html="getSortIcon('role')"></span>
                </span>
              </th>
              <th @click="handleSort('created_at')" class="sortable-header sortable-header-center" :class="{ active: sortField === 'created_at' }">
                <span class="header-content">
                  创建时间
                  <span class="sort-icon" v-html="getSortIcon('created_at')"></span>
                </span>
              </th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.realname || '-' }}</td>
              <td>{{ user.student_id || '-' }}</td>
              <td>
                <RoleBadge :user="user" />
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <div class="action-buttons-group">
                  <!-- 信息编辑按钮 -->
                  <button
                    class="action-toggle info"
                    @click="openInfoSelector(user)"
                  >
                    📝 信息编辑
                  </button>
                  <!-- 权限管理按钮 -->
                  <button
                    class="action-toggle permission"
                    @click="openPermissionModal(user)"
                  >
                    🔐 权限管理
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <Pagination
        v-if="!loading && users.length > 0"
        :page="page"
        :page-size="pageSize"
        :total-count="totalCount"
        :total-pages="totalPages"
        :page-size-options="pageSizeOptions"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      />
    </template>


    <!-- Password Change Modal - 优化版 -->
    <div v-if="showPasswordModal" class="modal-backdrop modal-backdrop-high" @click.self="closePasswordModal">
      <div class="modal-content password-modal">
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="close-btn" @click="closePasswordModal">&times;</button>
        </div>
        <div class="modal-body">
          <!-- User Info Preview -->
          <div class="password-user-info">
            <div class="user-avatar">👤</div>
            <div class="user-preview-info">
              <span class="preview-username">{{ passwordUser?.username }}</span>
              <span class="preview-label">正在修改密码</span>
            </div>
          </div>

          <!-- Password Form -->
          <div class="password-form">
            <div class="form-group">
              <label>新密码</label>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                class="form-control"
                placeholder="输入新密码（至少6位）"
                autocomplete="new-password"
              />
            </div>
            <div class="form-group">
              <label>确认新密码</label>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                class="form-control"
                placeholder="再次输入新密码"
                autocomplete="new-password"
              />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-action-btn secondary" @click="closePasswordModal">取消</button>
          <button class="modal-action-btn primary" @click="savePassword">保存</button>
        </div>
      </div>
    </div>

    <!-- Info Edit Selector Modal - 信息展示 + 可编辑表单 -->
    <div v-if="showInfoSelectorModal" class="modal-backdrop" @click.self="closeInfoSelector">
      <div class="modal-content user-info-modal">
        <div class="modal-header">
          <h3>信息编辑</h3>
          <button class="close-btn" @click="closeInfoSelector">&times;</button>
        </div>
        <div class="modal-body">
          <!-- User Info Section - 可编辑 -->
          <div class="user-info-section editable">
            <div class="user-info-header">
              <span class="user-avatar">👤</span>
              <div class="user-header-info">
                <h4 class="user-name">{{ infoSelectorUser?.username }}</h4>
                <RoleBadge :user="infoSelectorUser" />
              </div>
            </div>

            <div class="user-info-grid">
              <div class="info-item">
                <label>用户名</label>
                <span class="info-value disabled">{{ infoSelectorUser?.username || '-' }}</span>
              </div>
              <div class="info-item">
                <label>真实姓名</label>
                <input
                  v-model="editForm.realname"
                  type="text"
                  class="form-control info-input"
                  placeholder="输入真实姓名"
                />
              </div>
              <div class="info-item">
                <label>学号</label>
                <input
                  v-model="editForm.student_id"
                  type="text"
                  class="form-control info-input"
                  placeholder="输入学号"
                />
              </div>
              <div class="info-item">
                <label>创建时间</label>
                <span class="info-value disabled">{{ formatDate(infoSelectorUser?.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="modal-actions">
            <button class="modal-action-btn primary" @click="saveUserInfo">
              ✅ 保存修改
            </button>
            <button
              v-if="infoSelectorUser && canChangePassword(infoSelectorUser)"
              class="modal-action-btn secondary"
              @click="openPasswordModalFromInfo"
            >
              🔒 修改密码
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Permission Management Modal -->
    <div v-if="showPermissionModal" class="modal-backdrop" @click.self="closePermissionModal">
      <div class="modal-content permission-modal">
        <div class="modal-header">
          <h3>权限管理</h3>
          <button class="close-btn" @click="closePermissionModal">&times;</button>
        </div>
        <div class="modal-body">
          <!-- User Info Preview -->
          <div class="permission-user-info">
            <div class="user-avatar">👤</div>
            <div class="user-preview-info">
              <h4 class="preview-username">{{ permissionUser?.username }}</h4>
              <RoleBadge :user="permissionUser" />
            </div>
          </div>

          <!-- Constraint Message -->
          <div v-if="getConstraintMessage" class="constraint-message">
            <i class="constraint-icon">⚠️</i>
            <span>{{ getConstraintMessage }}</span>
          </div>

          <!-- Permission Toggles -->
          <div class="permission-toggles">
            <!-- Editor Toggle -->
            <div
              class="permission-toggle-item"
              :class="{ 'disabled': !canToggleEditor(permissionUser) }"
              @click="handleEditorToggle"
            >
              <div class="toggle-header">
                <span class="toggle-icon">📝</span>
                <span class="toggle-label">编辑权限</span>
              </div>
              <div class="toggle-switch-wrapper">
                <div
                  class="toggle-switch"
                  :class="{
                    'enabled': tempEditorPerm,
                    'disabled': !canToggleEditor(permissionUser)
                  }"
                >
                  <div class="toggle-slider"></div>
                </div>
                <span class="toggle-status" :class="tempEditorPerm ? 'enabled' : 'disabled'">
                  {{ tempEditorPerm ? '已启用' : '未启用' }}
                </span>
              </div>
              <div v-if="!canToggleEditor(permissionUser)" class="disabled-hint">
                {{ getEditorConstraintReason(permissionUser) }}
              </div>
            </div>

            <!-- Admin Toggle -->
            <div
              class="permission-toggle-item"
              :class="{ 'disabled': !canToggleAdmin(permissionUser) }"
              @click="handleAdminToggle"
            >
              <div class="toggle-header">
                <span class="toggle-icon">👤</span>
                <span class="toggle-label">管理员权限</span>
              </div>
              <div class="toggle-switch-wrapper">
                <div
                  class="toggle-switch"
                  :class="{
                    'enabled': tempAdminPerm,
                    'disabled': !canToggleAdmin(permissionUser)
                  }"
                >
                  <div class="toggle-slider"></div>
                </div>
                <span class="toggle-status" :class="tempAdminPerm ? 'enabled' : 'disabled'">
                  {{ tempAdminPerm ? '已启用' : '未启用' }}
                </span>
              </div>
              <div v-if="!canToggleAdmin(permissionUser)" class="disabled-hint">
                {{ getAdminConstraintReason(permissionUser) }}
              </div>
            </div>
          </div>

          <!-- Permission Description -->
          <div class="permission-description">
            <p><strong>编辑权限：</strong>可以创建、编辑、删除内容</p>
            <p><strong>管理员权限：</strong>可以管理用户权限和系统设置</p>
            <p><strong>超级管理员：</strong>同时拥有编辑和管理员权限。超级管理员可以单独移除任一权限，但不能同时移除两个权限</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-action-btn secondary" @click="closePermissionModal">取消</button>
          <button
            class="modal-action-btn primary"
            @click="savePermissions"
            :disabled="!hasPermissionChanges"
          >
            保存修改
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { getUsers, editUserRole, editUser } from '../../api/user'
import Pagination from '../../components/Pagination.vue'
import { useNotification } from '../../composables/useNotification'
import RoleBadge from '../../components/RoleBadge.vue'

const authStore = useAuthStore()
const { success, error, warning } = useNotification()

// State
const loading = ref(true)
const users = ref([])  // 改为当前页数据
const searchQuery = ref('')
const roleFilter = ref('')

// Server-side pagination state
const page = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const totalPages = ref(1)
const pageSizeOptions = [10, 20, 50, 100]

// Sorting state
const sortField = ref('created_at')
const sortOrder = ref('desc')  // 'asc' | 'desc'

// Edit Form (for info editing modal)
const editForm = ref({
  realname: '',
  student_id: ''
})

// Password Modal
const showPasswordModal = ref(false)
const passwordUser = ref(null)
const passwordForm = ref({
  newPassword: '',
  confirmPassword: ''
})

// Info Edit Selector Modal
const showInfoSelectorModal = ref(false)
const infoSelectorUser = ref(null)

// Permission Modal State
const showPermissionModal = ref(false)
const permissionUser = ref(null)

// Temporary permission states (before saving)
const tempEditorPerm = ref(false)
const tempAdminPerm = ref(false)

// Computed: can't modify self
const canModifySelf = computed(() => (userId) => {
  return userId !== authStore.user?.id
})

// Get editor constraint reason
function getEditorConstraintReason(user) {
  if (!user) return ''
  if (user.id === authStore.user?.id) return '不能修改自己的权限'
  // Super admin can toggle editor as long as they keep admin permission
  if (user.role === 3 && !user.has_admin_perm) return '超级管理员至少保留一个权限'
  return ''
}

// Get admin constraint reason
function getAdminConstraintReason(user) {
  if (!user) return ''
  if (user.id === authStore.user?.id) return '不能修改自己的权限'
  const adminCount = users.value.filter(u => u.has_admin_perm).length
  // Super admin can toggle admin as long as they keep editor permission
  if (user.role === 3 && !user.has_editor_perm) return '超级管理员至少保留一个权限'
  // Can't remove admin if only one admin left
  if (user.has_admin_perm && adminCount <= 1) return '至少保留一个管理员'
  return ''
}

// Get overall constraint message
const getConstraintMessage = computed(() => {
  if (!permissionUser.value) return ''
  const editorReason = getEditorConstraintReason(permissionUser.value)
  const adminReason = getAdminConstraintReason(permissionUser.value)
  if (editorReason && adminReason) {
    return '此用户的权限不可修改'
  }
  if (editorReason || adminReason) {
    return editorReason || adminReason
  }
  return ''
})

// Check if there are pending changes
const hasPermissionChanges = computed(() => {
  if (!permissionUser.value) return false
  return tempEditorPerm.value !== permissionUser.value.has_editor_perm ||
         tempAdminPerm.value !== permissionUser.value.has_admin_perm
})

// Check if can toggle editor permission
function canToggleEditor(user) {
  if (!user) return false
  // Can't modify self
  if (user.id === authStore.user?.id) return false

  // Super admin logic: can remove editor if they keep admin permission
  if (user.role === 3 && permissionUser.value === user) {
    // Check if toggling editor would remove both permissions
    const wouldHaveAdmin = tempAdminPerm.value
    const wouldHaveEditor = !tempEditorPerm.value
    // If after toggle they'd have neither permission, block it
    if (!wouldHaveAdmin && !wouldHaveEditor) return false
  }
  return true
}

// Check if can toggle admin permission
function canToggleAdmin(user) {
  if (!user) return false
  // Can't modify self
  if (user.id === authStore.user?.id) return false

  // Super admin logic: can remove admin if they keep editor permission
  if (user.role === 3 && permissionUser.value === user) {
    // Check if toggling admin would remove both permissions
    const wouldHaveEditor = tempEditorPerm.value
    const wouldHaveAdmin = !tempAdminPerm.value
    // If after toggle they'd have neither permission, block it
    if (!wouldHaveEditor && !wouldHaveAdmin) return false
  }

  // Can't remove admin if only one admin left
  const adminCount = users.value.filter(u => u.has_admin_perm).length
  // Check if we're trying to remove admin permission
  const isRemovingAdmin = user.has_admin_perm && !tempAdminPerm.value
  if (permissionUser.value === user && isRemovingAdmin && adminCount <= 1) return false

  return true
}

// Check if can change password (admin or self)
function canChangePassword(user) {
  // Can change any user's password if admin
  if (authStore.hasAdminPerm) return true
  // Can change own password
  if (user.id === authStore.user?.id) return true
  return false
}

// 获取排序图标
function getSortIcon(field) {
  if (sortField.value !== field) {
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 5L6 1L10 5" stroke="#adb5bd" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 11V1" stroke="#adb5bd" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  }
  if (sortOrder.value === 'asc') {
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 5L6 1L10 5" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 11V1" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  } else {
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 7L6 11L10 7" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 1V11" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  }
}

// 切换排序
function handleSort(field) {
  if (sortField.value === field) {
    // 同一字段：切换升序/降序/默认
    if (sortOrder.value === 'desc') {
      sortOrder.value = 'asc'
    } else {
      // 切换到默认（created_at desc）
      sortField.value = 'created_at'
      sortOrder.value = 'desc'
    }
  } else {
    // 新字段：默认降序
    sortField.value = field
    sortOrder.value = 'desc'
  }
  page.value = 1  // 排序后重置到第一页
  fetchUsers()
}

// 分页大小变更
function handlePageSizeChange() {
  page.value = 1
  fetchUsers()
}

// 跳转到指定页码
function handlePageChange(newPage) {
  page.value = newPage
  fetchUsers()
}

// 防抖定时器
let debounceTimer = null

// 触发服务端查询（带防抖）
function filterUsers() {
  // 清除之前的定时器
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  // 延迟 500ms 后执行搜索
  debounceTimer = setTimeout(() => {
    page.value = 1  // 筛选后重置到第一页
    fetchUsers()
  }, 500)
}

// Format date
function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}


// Close password modal
function closePasswordModal() {
  showPasswordModal.value = false
  passwordUser.value = null
  passwordForm.value = {
    newPassword: '',
    confirmPassword: ''
  }
  // 不关闭信息编辑弹窗，保持上下文
}

// Save password
async function savePassword() {
  if (!passwordUser.value) return

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    error('两次输入的密码不一致')
    return
  }
  if (passwordForm.value.newPassword.length < 6) {
    warning('密码长度至少为 6 位')
    return
  }

  try {
    // For now, we'll need to add password support to backend
    // Check if backend supports password field
    await editUser(passwordUser.value.id, {
      password: passwordForm.value.newPassword
    })
    success('密码已修改')
    closePasswordModal()
  } catch (error) {
    console.error('Failed to change password:', error)
    // Check if it's a validation error (password not supported)
    if (error.response?.data?.password) {
      error('修改密码失败：' + error.response.data.password.join(', '))
    } else {
      error('修改密码失败，请检查后端是否支持密码字段')
    }
  }
}

// Open info edit selector
function openInfoSelector(user) {
  infoSelectorUser.value = user
  editForm.value = {
    realname: user.realname || '',
    student_id: user.student_id || ''
  }
  showInfoSelectorModal.value = true
}

// Close info edit selector
function closeInfoSelector() {
  showInfoSelectorModal.value = false
  infoSelectorUser.value = null
}

// 直接保存用户信息（在信息编辑弹窗中）
async function saveUserInfo() {
  if (!infoSelectorUser.value) return

  try {
    await editUser(infoSelectorUser.value.id, editForm.value)
    await fetchUsers()  // 等待刷新完成

    // 更新弹窗中的用户数据引用
    const updatedUser = users.value.find(u => u.id === infoSelectorUser.value.id)
    if (updatedUser) {
      infoSelectorUser.value = updatedUser
    }

    success('用户信息已更新')
    closeInfoSelector()
  } catch (error) {
    console.error('Failed to edit user:', error)
    error('更新用户信息失败')
  }
}

// 从信息编辑弹窗打开密码修改弹窗
function openPasswordModalFromInfo() {
  if (infoSelectorUser.value) {
    passwordUser.value = infoSelectorUser.value
    passwordForm.value = {
      newPassword: '',
      confirmPassword: ''
    }
    // 不关闭信息编辑弹窗，保持上下文
    showPasswordModal.value = true
  }
}

// Open permission management modal
function openPermissionModal(user) {
  permissionUser.value = user
  tempEditorPerm.value = user.has_editor_perm
  tempAdminPerm.value = user.has_admin_perm
  showPermissionModal.value = true
}

// Close permission modal
function closePermissionModal() {
  showPermissionModal.value = false
  permissionUser.value = null
  tempEditorPerm.value = false
  tempAdminPerm.value = false
}

// Handle editor toggle click
function handleEditorToggle() {
  if (!canToggleEditor(permissionUser.value)) return
  tempEditorPerm.value = !tempEditorPerm.value
}

// Handle admin toggle click
function handleAdminToggle() {
  if (!canToggleAdmin(permissionUser.value)) return
  tempAdminPerm.value = !tempAdminPerm.value
}

// Save permissions
async function savePermissions() {
  if (!permissionUser.value) return
  if (!hasPermissionChanges.value) {
    closePermissionModal()
    return
  }

  const user = permissionUser.value
  const changes = []

  // Editor permission change
  if (tempEditorPerm.value !== user.has_editor_perm) {
    changes.push({
      permission: 'editor',
      action: tempEditorPerm.value ? 'add' : 'remove'
    })
  }

  // Admin permission change
  if (tempAdminPerm.value !== user.has_admin_perm) {
    changes.push({
      permission: 'admin',
      action: tempAdminPerm.value ? 'add' : 'remove'
    })
  }

  try {
    // Apply all changes
    for (const change of changes) {
      await editUserRole(user.id, change.action, change.permission)
    }

    await fetchUsers()  // 等待刷新完成

    // 更新弹窗中的用户数据引用
    const updatedUser = users.value.find(u => u.id === user.id)
    if (updatedUser) {
      permissionUser.value = updatedUser
      tempEditorPerm.value = updatedUser.has_editor_perm
      tempAdminPerm.value = updatedUser.has_admin_perm
    }

    success('权限已更新')
    closePermissionModal()
  } catch (error) {
    console.error('Failed to update permissions:', error)
    error('更新权限失败')
  }
}

// Fetch users
async function fetchUsers() {
  try {
    loading.value = true
    const params = {
      page: page.value,
      page_size: pageSize.value,
      sort: sortField.value,
      order: sortOrder.value
    }

    // 添加搜索参数
    if (searchQuery.value) {
      params.q = searchQuery.value
    }

    // 添加权限筛选
    if (roleFilter.value !== '') {
      params.role = roleFilter.value
    }

    const data = await getUsers(params)
    users.value = data.results || []
    totalCount.value = data.count || 0
    totalPages.value = data.total_pages || 1
  } catch (error) {
    console.error('Failed to fetch users:', error)
    users.value = []
    totalCount.value = 0
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

onMounted(fetchUsers)
watch([page, pageSize], () => {
  // Scroll to top when page changes
  window.scrollTo({ top: 0, behavior: 'smooth' })
  // Refetch data when page or page size changes
  fetchUsers()
})
</script>

<style scoped>
@import '../../styles/utilities.css';
@import '../../styles/admin.css';

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 12px 15px;
  text-align: center; /* Center align all cells */
  border-bottom: 1px solid #dee2e6;
}

.users-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
}

.users-table tbody tr:hover {
  background-color: #f8f9fa;
}

/* 操作按钮组样式 */
.action-buttons-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 操作按钮样式 - 与 StatusDropdown/DeadlineDropdown 保持一致 */
.action-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1.5px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  white-space: nowrap;
  min-width: 85px;
  justify-content: center;
  background: transparent;
  color: #667eea;
}

/* 信息编辑按钮样式 */
.action-toggle.info {
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.2);
}

.action-toggle.info:hover {
  background: rgba(102, 126, 234, 0.12);
  border-color: rgba(102, 126, 234, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.action-toggle.info:active {
  transform: translateY(0);
}

/* 权限管理按钮样式 */
.action-toggle.permission {
  color: #f39c12;
  background: rgba(243, 156, 18, 0.08);
  border-color: rgba(243, 156, 18, 0.2);
}

.action-toggle.permission:hover {
  background: rgba(243, 156, 18, 0.12);
  border-color: rgba(243, 156, 18, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(243, 156, 18, 0.15);
}

.action-toggle.permission:active {
  transform: translateY(0);
}

/* 工具栏样式 */
.users-toolbar {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
  border: 1px solid #e9ecef;
}

/* 搜索输入框容器 */
.search-input-wrapper {
  position: relative;
  flex: 1 1 auto;
  min-width: 200px;
  max-width: calc(100% - 150px);
  overflow: hidden;
}

.search-input {
  width: 100%;
  max-width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #fafafa;
  color: #2c3e50;
  box-sizing: border-box;
}

.search-input:hover {
  border-color: #b0b0b0;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15), 0 4px 12px rgba(102, 126, 234, 0.1);
  background-color: #fff;
}

.search-input::placeholder {
  color: #adb5bd;
  font-weight: 400;
  transition: color 0.3s ease;
}

.search-input:focus::placeholder {
  color: #d0d3d4;
}

/* 搜索图标 */
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.95rem;
  color: #adb5bd;
  pointer-events: none;
  transition: color 0.3s ease;
}

.search-input:focus ~ .search-icon {
  color: #667eea;
}

/* 下拉选择框 */
.users-toolbar .form-select {
  flex: 0 0 auto;
  min-width: 150px;
  padding: 10px 12px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #fafafa;
  color: #2c3e50;
}

.users-toolbar .form-select:hover {
  border-color: #b0b0b0;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.users-toolbar .form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15), 0 4px 12px rgba(102, 126, 234, 0.1);
  background-color: #fff;
}

/* 操作栏最小宽度 */
.users-table td:nth-child(7) {
  min-width: 180px;
}

/* 选择弹框样式 */
.action-selector-modal .modal-content {
  max-width: 380px;
}

.action-selector-btn {
  width: 100%;
  margin-bottom: 10px;
  text-align: left;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.action-selector-btn:last-child {
  margin-bottom: 0;
}

.action-selector-btn:hover {
  transform: translateX(4px);
}

.action-arrow {
  font-style: normal;
  opacity: 0.6;
  transition: transform 0.2s ease;
}

.action-selector-btn:hover .action-arrow {
  transform: translateX(4px);
  opacity: 1;
}

.permission-status {
  font-size: 0.8rem;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.permission-status.status-enabled {
  background-color: rgba(46, 204, 113, 0.15);
  color: #27ae60;
}

.permission-status.status-disabled {
  background-color: rgba(149, 165, 166, 0.15);
  color: #7f8c8d;
}

/* 权限按钮禁用状态 */
.action-selector-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 用户信息弹窗样式 */
.user-info-modal {
  max-width: 480px;
}

.user-info-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.user-info-section.editable {
  background: #fff;
  border: 2px solid #e9ecef;
}

.user-info-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #dee2e6;
}

.user-avatar {
  font-size: 2.5rem;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

.user-header-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
  line-height: 1.4;
  align-self: flex-start;
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

.user-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item label {
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 500;
}

.info-value {
  font-size: 0.95rem;
  color: #2c3e50;
  font-weight: 500;
  padding: 8px 0;
}

.info-value.disabled {
  color: #adb5bd;
  font-weight: 400;
}

.info-input {
  font-size: 0.9rem;
  padding: 8px 10px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #fafafa;
  color: #2c3e50;
  font-weight: 400;
  min-height: 36px;
  box-sizing: border-box;
}

.info-input:hover {
  border-color: #b0b0b0;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15), 0 4px 12px rgba(102, 126, 234, 0.1);
  background-color: #fff;
  transform: translateY(-1px);
}

.info-input::placeholder {
  color: #adb5bd;
  font-weight: 400;
  transition: color 0.3s ease;
}

.info-input:focus::placeholder {
  color: #d0d3d4;
}

.modal-actions {
  display: flex;
  gap: 10px;
}

/* 模态框操作按钮 - 淡雅风格 */
.modal-action-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1.5px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  white-space: nowrap;
  background: transparent;
}

/* 主按钮 - 绿色 */
.modal-action-btn.primary {
  color: #27ae60;
  background: rgba(39, 174, 96, 0.08);
  border-color: rgba(39, 174, 96, 0.2);
}

.modal-action-btn.primary:hover {
  background: rgba(39, 174, 96, 0.12);
  border-color: rgba(39, 174, 96, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.15);
}

.modal-action-btn.primary:active {
  transform: translateY(0);
}

/* 次要按钮 - 蓝色 */
.modal-action-btn.secondary {
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.2);
}

.modal-action-btn.secondary:hover {
  background: rgba(102, 126, 234, 0.12);
  border-color: rgba(102, 126, 234, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.modal-action-btn.secondary:active {
  transform: translateY(0);
}

/* 密码弹窗样式 */
.password-modal {
  max-width: 420px;
  z-index: 2000;
}

.password-user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.password-user-info .user-avatar {
  width: 48px;
  height: 48px;
  font-size: 2rem;
}

.preview-username {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0 0 8px 0;
}

.preview-label {
  font-size: 0.8rem;
  color: #6c757d;
}

.password-form .form-group {
  margin-bottom: 16px;
}

.password-form .form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.9rem;
}

.password-form .form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.password-form .form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 权限管理弹窗样式 */
.permission-modal {
  max-width: 500px;
}

.permission-user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.permission-user-info .user-avatar {
  width: 56px;
  height: 56px;
  font-size: 2.5rem;
}

.permission-user-info .user-preview-info {
  display: block;
  min-width: 0;
}

.permission-user-info .preview-username {
  display: block;
}

.constraint-message {
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 6px;
  padding: 10px 14px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #856404;
}

.constraint-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

.permission-toggles {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.permission-toggle-item {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.permission-toggle-item:hover:not(.disabled) {
  background: #e9ecef;
  border-color: #ced4da;
  transform: translateY(-2px);
}

.permission-toggle-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.toggle-icon {
  font-size: 1.2rem;
}

.toggle-label {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
}

.toggle-switch-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.toggle-switch {
  width: 50px;
  height: 26px;
  background-color: #ccc;
  border-radius: 13px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s ease;
  flex-shrink: 0;
}

.toggle-switch.enabled {
  background-color: #2ecc71;
}

.toggle-switch.disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.toggle-slider {
  width: 22px;
  height: 22px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch.enabled .toggle-slider {
  transform: translateX(24px);
}

.toggle-switch.disabled .toggle-slider {
  background-color: #bdc3c7;
}

.toggle-status {
  font-size: 0.85rem;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 4px;
  min-width: 60px;
  text-align: center;
}

.toggle-status.enabled {
  background-color: rgba(46, 204, 113, 0.15);
  color: #27ae60;
}

.toggle-status.disabled {
  background-color: rgba(149, 165, 166, 0.15);
  color: #7f8c8d;
}

.disabled-hint {
  margin-top: 8px;
  font-size: 0.8rem;
  color: #e74c3c;
  padding: 6px 10px;
  background-color: rgba(231, 76, 60, 0.1);
  border-radius: 4px;
}

.permission-description {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border-left: 3px solid #3498db;
}

.permission-description p {
  margin: 6px 0;
  font-size: 0.85rem;
  color: #6c757d;
  line-height: 1.5;
}

.permission-description p:first-child {
  margin-top: 0;
}

.permission-description p:last-child {
  margin-bottom: 0;
}

.modal-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.modal-footer .modal-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .user-info-modal,
  .password-modal,
  .permission-modal {
    max-width: 100%;
  }

  .user-info-grid {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column;
  }

  .toggle-switch-wrapper {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

/* 密码弹窗背景高优先级 - 确保覆盖信息编辑弹窗 */
.modal-backdrop-high {
  z-index: 2000 !important;
}

/* 排序列头样式 */
.users-table th.sortable-header {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
  padding-right: 12px !important;
}

.users-table th.sortable-header:hover {
  background-color: #e9ecef;
}

.users-table th.sortable-header.active {
  color: #667eea;
  font-weight: 600;
}

/* Header content wrapper for proper alignment */
.header-content {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

/* Sort icon styling */
.sort-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  opacity: 0.6;
}

.users-table th.sortable-header:hover .sort-icon,
.users-table th.sortable-header.active .sort-icon {
  opacity: 1;
}
</style>
