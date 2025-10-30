import { createRouter, createWebHistory } from 'vue-router'

import HomeView  from '../views/Home.vue'
import LogInView from '../views/Login.vue'
import RegisterView from  '../views/Register.vue'
import ContactView from '../views/Contact.vue'
import AdminView from '../views/Admin.vue'
import MainView from '../views/Main.vue'


// 路由配置
const routes = [
  { path: '/', component: HomeView  },
  { path: '/login', component: LogInView },
  { path: '/register', component: RegisterView},
  { path: '/contact', component: ContactView },
  { path: '/admin', component: AdminView },
  { path: '/main', component: MainView }

]


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
