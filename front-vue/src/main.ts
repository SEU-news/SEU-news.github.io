import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ToastContainer from './components/ToastContainer.vue'

const app = createApp(App)
const pinia = createPinia()

// 挂载路由
app.use(pinia)
app.use(router)

// Register ToastContainer globally
app.component('ToastContainer', ToastContainer)

app.mount('#app')
