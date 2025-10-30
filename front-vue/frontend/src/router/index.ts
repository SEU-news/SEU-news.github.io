import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import LogIn from '../views/Login.vue'
import Register from  '../views/Register.vue'
import Contact from '../views/Contact.vue'

// 路由配置
const routes = [
  { path: '/', component: Home },
  { path: '/login', component: LogIn },
  { path: '/register', component: Register},
  { path: '/contact', component: Contact }
]


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
