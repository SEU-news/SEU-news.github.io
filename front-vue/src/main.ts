import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ToastContainer from './components/ToastContainer.vue'
import LoadingSpinner from './components/admin/LoadingSpinner.vue'
import EmptyState from './components/EmptyState.vue'
import StatusBadge from './components/StatusBadge.vue'

const app = createApp(App)
const pinia = createPinia()

// 挂载路由
app.use(pinia)
app.use(router)

// Register global components
app.component('ToastContainer', ToastContainer)
app.component('LoadingSpinner', LoadingSpinner)
app.component('EmptyState', EmptyState)
app.component('StatusBadge', StatusBadge)

app.mount('#app')
