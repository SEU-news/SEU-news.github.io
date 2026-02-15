import { ref, inject } from 'vue'

// Toast notification types
export const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
}

// Icon mapping for each toast type
const TYPE_ICONS = {
  [TOAST_TYPES.SUCCESS]: '✅',
  [TOAST_TYPES.ERROR]: '❌',
  [TOAST_TYPES.WARNING]: '⚠️',
  [TOAST_TYPES.INFO]: 'ℹ️'
}

// Browser Notification permission state
let notificationPermission = 'default'

// Request notification permission (once per session)
async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    return false
  }

  if (Notification.permission === 'granted') {
    notificationPermission = 'granted'
    return true
  }

  if (Notification.permission === 'denied') {
    notificationPermission = 'denied'
    return false
  }

  const permission = await Notification.requestPermission()
  notificationPermission = permission
  return permission === 'granted'
}

// Show browser notification
function showBrowserNotification(title, body = '') {
  if (!('Notification' in window)) {
    return false
  }

  // Request permission on first call if not granted
  if (Notification.permission === 'default') {
    requestNotificationPermission()
  }

  if (Notification.permission === 'granted') {
    new Notification(title, {
      body,
      icon: '/favicon.ico',
      badge: '/favicon.ico'
    })
    return true
  }

  return false
}

// Global notification state management
const toasts = ref([])
let toastIdCounter = 0

/**
 * Show a toast notification with optional browser notification
 * @param {string} message - The message to display
 * @param {string} type - Toast type (success, error, warning, info)
 * @param {number} duration - Auto-dismiss duration in ms (default: 5000)
 * @param {boolean} showBrowserNotif - Whether to show browser notification
 * @returns {number} The toast ID
 */
function showToast(message, type = TOAST_TYPES.INFO, duration = 5000, showBrowserNotif = false) {
  const id = ++toastIdCounter
  const toast = {
    id,
    message,
    type,
    duration,
    remaining: duration,
    paused: false,
    createdAt: Date.now()
  }

  toasts.value.push(toast)

  // Auto-dismiss countdown
  const startTime = Date.now()
  let pausedAt = null
  let pausedDuration = 0

  const updateRemaining = () => {
    if (!toast.paused) {
      const elapsed = Date.now() - startTime - pausedDuration
      toast.remaining = Math.max(0, duration - elapsed)

      if (toast.remaining <= 0) {
        removeToast(id)
      } else {
        requestAnimationFrame(updateRemaining)
      }
    }
  }

  requestAnimationFrame(updateRemaining)

  // Show browser notification for important messages
  if (showBrowserNotif) {
    showBrowserNotification(message)
  }

  return id
}

/**
 * Remove a toast by ID
 * @param {number} id - The toast ID to remove
 */
function removeToast(id) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

/**
 * Pause auto-dismiss for a toast
 * @param {number} id - The toast ID to pause
 */
function pauseToast(id) {
  const toast = toasts.value.find(t => t.id === id)
  if (toast) {
    toast.paused = true
  }
}

/**
 * Resume auto-dismiss for a toast
 * @param {number} id - The toast ID to resume
 */
function resumeToast(id) {
  const toast = toasts.value.find(t => t.id === id)
  if (toast) {
    toast.paused = false
  }
}

/**
 * Clear all toasts
 */
function clearAllToasts() {
  toasts.value = []
}

/**
 * Notification composable
 * @returns {Object} Notification functions
 */
export function useNotification() {
  /**
   * Show success notification
   * @param {string} message - The success message
   */
  function success(message) {
    return showToast(message, TOAST_TYPES.SUCCESS, 5000)
  }

  /**
   * Show error notification
   * @param {string} message - The error message
   */
  function error(message) {
    return showToast(message, TOAST_TYPES.ERROR, 6000)
  }

  /**
   * Show warning notification
   * @param {string} message - The warning message
   */
  function warning(message) {
    return showToast(message, TOAST_TYPES.WARNING, 5000)
  }

  /**
   * Show info notification
   * @param {string} message - The info message
   */
  function info(message) {
    return showToast(message, TOAST_TYPES.INFO, 4000)
  }

  return {
    toasts,
    success,
    error,
    warning,
    info,
    removeToast,
    pauseToast,
    resumeToast,
    clearAllToasts,
    TYPE_ICONS,
    TOAST_TYPES
  }
}

// Export global state for ToastContainer
export { toasts, removeToast, pauseToast, resumeToast }
