import { createRouter, createWebHistory } from 'vue-router'

import HomeView  from '../views/Home.vue'
import LogInView from '../views/Login.vue'
import RegisterView from  '../views/Register.vue'
import ContactView from '../views/Contact.vue'
import AdminView from '../views/Admin.vue'
import MainView from '../views/Main.vue'
import NewsView from '../views/News.vue'
import AboutView from '../views/About.vue'
import { errorRoutes } from './errorRoutes'

// 路由配置
const routes = [
  { path: '/', component: HomeView  },
  { path: '/news', name: 'News', component: NewsView },
  { path: '/about', name: 'About', component: AboutView },
  { path: '/login', component: LogInView },
  { path: '/register', component: RegisterView},
  { path: '/contact', component: ContactView },
  { path: '/admin', component: AdminView },
  { path: '/main', component: MainView },
  { path: '/admin-login', component: AdminView },
  
  // 错误页面路由
  ...errorRoutes,
  
  // 404页面必须放在最后
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('../views/errors/404.vue') },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router