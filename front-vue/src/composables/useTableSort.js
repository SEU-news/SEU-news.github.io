/**
 * Table Sorting Composable
 * 表格排序组合式函数
 *
 * Provides reusable table sorting logic with visual sort icons.
 * 参考 AdminEntries.vue:166-187 和 AdminUsers.vue:517-534。
 */

import { ref } from 'vue'

/**
 * Table sorting composable
 * @param {Object} options - Configuration options
 * @param {string} options.defaultField - Default sort field (default: 'created_at')
 * @param {string} options.defaultOrder - Default sort order (default: 'desc')
 * @returns {Object} Sorting utilities
 */
export function useTableSort(options = {}) {
  const {
    defaultField = 'created_at',
    defaultOrder = 'desc'
  } = options

  const sortField = ref(defaultField)
  const sortOrder = ref(defaultOrder)

  // Inactive sort icon (gray)
  const inactiveIcon = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 5L6 1L10 5" stroke="#adb5bd" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 11V1" stroke="#adb5bd" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

  // Ascending sort icon (blue, up)
  const ascIcon = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 5L6 1L10 5" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 11V1" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

  // Descending sort icon (blue, down)
  const descIcon = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 7L6 11L10 7" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 1V11" stroke="#667eea" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

  /**
   * Get sort icon for a field (returns SVG HTML)
   * @param {string} field - Field name
   * @returns {string} SVG HTML string
   */
  function getSortIcon(field) {
    if (sortField.value !== field) {
      return inactiveIcon
    }
    return sortOrder.value === 'asc' ? ascIcon : descIcon
  }

  /**
   * Toggle sort order for a field
   * - If clicking on a new field: set to desc (newest first)
   * - If clicking on same field: toggle asc/desc
   * @param {string} field - Field name to sort by
   * @param {Function} onSortChange - Callback when sort changes (optional)
   */
  function toggleSort(field, onSortChange) {
    if (sortField.value === field) {
      // Same field: toggle between asc/desc
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      // New field: use desc order (newest first)
      sortField.value = field
      sortOrder.value = 'desc'
    }

    // Call callback if provided
    if (onSortChange && typeof onSortChange === 'function') {
      onSortChange(sortField.value, sortOrder.value)
    }
  }

  /**
   * Set sort explicitly
   * @param {string} field - Field name
   * @param {string} order - Sort order ('asc' or 'desc')
   * @param {Function} onSortChange - Callback when sort changes (optional)
   */
  function setSort(field, order, onSortChange) {
    sortField.value = field
    sortOrder.value = order

    if (onSortChange && typeof onSortChange === 'function') {
      onSortChange(field, order)
    }
  }

  /**
   * Reset to default sort
   * @param {Function} onSortChange - Callback when sort changes (optional)
   */
  function resetSort(onSortChange) {
    sortField.value = defaultField
    sortOrder.value = defaultOrder

    if (onSortChange && typeof onSortChange === 'function') {
      onSortChange(defaultField, defaultOrder)
    }
  }

  /**
   * Check if a field is currently sorted
   * @param {string} field - Field name
   * @returns {boolean} True if this is the current sort field
   */
  function isSortedBy(field) {
    return sortField.value === field
  }

  /**
   * Check if sorting is ascending
   * @returns {boolean} True if current sort order is ascending
   */
  function isAscending() {
    return sortOrder.value === 'asc'
  }

  /**
   * Check if sorting is descending
   * @returns {boolean} True if current sort order is descending
   */
  function isDescending() {
    return sortOrder.value === 'desc'
  }

  return {
    // State
    sortField,
    sortOrder,

    // Actions
    toggleSort,
    setSort,
    resetSort,

    // Queries
    getSortIcon,
    isSortedBy,
    isAscending,
    isDescending
  }
}
