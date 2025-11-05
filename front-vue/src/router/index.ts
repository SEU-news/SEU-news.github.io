import { createRouter, createWebHistory } from 'vue-router'
import { errorRoutes } from './errorRoutes'

// 路由配置
const routes = [
  { 
    path: '/', 
    component: () => import('../views/Home.vue')
  },
  { 
    path: '/news', 
    name: 'News', 
    component: () => import('../views/News.vue') 
  },
  { 
    path: '/about', 
    name: 'About', 
    component: () => import('../views/About.vue') 
  },
  { 
    path: '/login', 
    component: () => import('../views/Login.vue') 
  },
  { 
    path: '/register', 
    component: () => import('../views/Register.vue')
  },
  { 
    path: '/contact', 
    component: () => import('../views/Contact.vue') 
  },
  { 
    path: '/admin', 
    component: () => import('../views/Admin.vue') 
  },
  { 
    path: '/main', 
    component: () => import('../views/Main.vue') 
  },
  { 
    path: '/admin-login', 
    component: () => import('../views/Admin.vue') 
  },
  
  // 错误页面路由
  ...errorRoutes,
  
  // 通配符路由，用于捕获所有未匹配的路由并重定向到404页面
  { 
    path: '/:pathMatch(.*)*', 
    redirect: '/404' 
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router