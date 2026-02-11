/**
 * Status Configuration Composable
 * 状态配置组合式函数
 *
 * Provides centralized status configuration for content entries.
 * 与 StatusDropdown.vue 和其他组件保持一致的状态配置。
 */

import { computed } from 'vue'

// 状态配置映射（与 StatusDropdown.vue:54-61 保持一致）
const statusConfig = {
  draft: { icon: '📝', label: '草稿', color: '#3498db' },
  pending: { icon: '⏳', label: '待审核', color: '#f39c12' },
  reviewed: { icon: '✅', label: '已审核', color: '#2ecc71' },
  rejected: { icon: '❌', label: '已拒绝', color: '#e74c3c' },
  published: { icon: '🚀', label: '已发布', color: '#9b59b6' },
  terminated: { icon: '🚫', label: '已终止', color: '#6c757d' }
}

/**
 * Status configuration composable
 * @returns {Object} Status configuration utilities
 */
export function useStatusConfig() {
  /**
   * Get status configuration by status key
   * @param {string} status - Status key (draft, pending, etc.)
   * @returns {Object} Status configuration object
   */
  function getStatusConfig(status) {
    return statusConfig[status] || statusConfig.draft
  }

  /**
   * Status options for dropdowns/selects
   * Computed on each call to ensure reactivity
   */
  const statusOptions = computed(() => {
    return Object.entries(statusConfig).map(([value, config]) => ({
      value,
      label: config.label,
      icon: config.icon,
      color: config.color
    }))
  })

  /**
   * Get all status keys
   */
  function getStatusKeys() {
    return Object.keys(statusConfig)
  }

  /**
   * Get status label
   * @param {string} status - Status key
   * @returns {string} Status label
   */
  function getStatusLabel(status) {
    return getStatusConfig(status).label
  }

  /**
   * Get status icon
   * @param {string} status - Status key
   * @returns {string} Status icon emoji
   */
  function getStatusIcon(status) {
    return getStatusConfig(status).icon
  }

  /**
   * Get status color
   * @param {string} status - Status key
   * @returns {string} Status color hex code
   */
  function getStatusColor(status) {
    return getStatusConfig(status).color
  }

  return {
    statusConfig,
    getStatusConfig,
    statusOptions,
    getStatusKeys,
    getStatusLabel,
    getStatusIcon,
    getStatusColor
  }
}
