<template>
  <div class="toast-container">
    <transition-group name="toast" tag="div" class="toast-list">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast-item', `toast-${toast.type}`]"
        @click="dismissToast(toast.id)"
        @mouseenter="pauseToast(toast.id)"
        @mouseleave="resumeToast(toast.id)"
      >
        <!-- Icon -->
        <span class="toast-icon">{{ TYPE_ICONS[toast.type] }}</span>

        <!-- Message -->
        <span class="toast-message">{{ toast.message }}</span>

        <!-- Dismiss button -->
        <button class="toast-close" @click.stop="dismissToast(toast.id)">
          &times;
        </button>

        <!-- Progress bar -->
        <div class="toast-progress">
          <div
            class="toast-progress-bar"
            :style="{ width: `${(toast.remaining / toast.duration) * 100}%` }"
          ></div>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { toasts } from '../composables/useNotification'
import { removeToast, pauseToast, resumeToast } from '../composables/useNotification'

// Icon mapping for each toast type
const TYPE_ICONS = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️'
}

/**
 * Dismiss a toast
 * @param {number} id - The toast ID to dismiss
 */
function dismissToast(id) {
  // Add a small delay for the close animation
  setTimeout(() => {
    removeToast(id)
  }, 200)
}
</script>

<style scoped>
/* Toast Container - Fixed position at top right */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
  max-width: 400px;
  width: 100%;
}

.toast-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: auto;
}

/* Toast Item */
.toast-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
  min-width: 300px;
  max-width: 100%;
  cursor: pointer;
  user-select: none;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
}

.toast-item:hover {
  transform: translateX(-4px) scale(1.02);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Toast Type Styles */
.toast-success {
  border-color: rgba(39, 174, 96, 0.3);
  background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
}

.toast-error {
  border-color: rgba(231, 76, 60, 0.3);
  background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
}

.toast-warning {
  border-color: rgba(243, 156, 18, 0.3);
  background: linear-gradient(135deg, #fffaf0 0%, #ffffff 100%);
}

.toast-info {
  border-color: rgba(52, 152, 219, 0.3);
  background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
}

/* Toast Icon */
.toast-icon {
  font-size: 1.4rem;
  line-height: 1.4;
  flex-shrink: 0;
  margin-top: 1px;
}

/* Toast Message */
.toast-message {
  flex: 1;
  font-size: 0.95rem;
  line-height: 1.5;
  color: #2c3e50;
  font-weight: 500;
  word-break: break-word;
}

/* Toast Type-specific message colors */
.toast-success .toast-message {
  color: #27ae60;
}

.toast-error .toast-message {
  color: #c0392b;
}

.toast-warning .toast-message {
  color: #e67e22;
}

.toast-info .toast-message {
  color: #2980b9;
}

/* Toast Close Button */
.toast-close {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #6c757d;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  border-radius: 4px;
  transition: all 0.2s ease;
  opacity: 0.6;
}

.toast-close:hover {
  background-color: rgba(0, 0, 0, 0.08);
  color: #343a40;
  opacity: 1;
  transform: scale(1.1);
}

.toast-close:active {
  transform: scale(0.95);
}

/* Toast Progress Bar */
.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: rgba(0, 0, 0, 0.06);
  border-radius: 0 0 10px 10px;
  overflow: hidden;
}

.toast-progress-bar {
  height: 100%;
  transition: width 0.1s linear;
  border-radius: 0 0 10px 10px;
}

/* Type-specific progress bar colors */
.toast-success .toast-progress-bar {
  background: linear-gradient(90deg, #27ae60 0%, #2ecc71 100%);
}

.toast-error .toast-progress-bar {
  background: linear-gradient(90deg, #c0392b 0%, #e74c3c 100%);
}

.toast-warning .toast-progress-bar {
  background: linear-gradient(90deg, #e67e22 0%, #f39c12 100%);
}

.toast-info .toast-progress-bar {
  background: linear-gradient(90deg, #2980b9 0%, #3498db 100%);
}

/* Toast Animations */
.toast-enter-active {
  animation: toastSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-leave-active {
  animation: toastSlideOut 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes toastSlideIn {
  0% {
    opacity: 0;
    transform: translateX(120%) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes toastSlideOut {
  0% {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateX(120%) scale(0.8);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .toast-container {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }

  .toast-item {
    min-width: unset;
    padding: 14px 16px;
  }

  .toast-message {
    font-size: 0.9rem;
  }

  .toast-icon {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .toast-container {
    top: 5px;
    right: 5px;
    left: 5px;
    gap: 8px;
  }

  .toast-item {
    padding: 12px 14px;
    border-radius: 8px;
  }

  .toast-message {
    font-size: 0.85rem;
  }

  .toast-close {
    width: 20px;
    height: 20px;
    font-size: 1.3rem;
  }

  .toast-progress {
    height: 2px;
  }
}
</style>
