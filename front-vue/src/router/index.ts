import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 错误页面名称集合，用于App.vue中判断是否显示导航栏
export const errorRouteNames = [
  'BadRequest',
  'Unauthorized',
  'Forbidden',
  'NotFound',
  'SurverError',
  'MethodNotAllowed',
  'RequestTimeout',
  'PayloadTooLarge',
  'TooManyRequests',
  'BadGateway',
  'ServiceUnavailable',
  'GatewayTimeout'
]

// 错误页面路由
const errorRoutes = [
  { path: '/400', name: 'BadRequest', component: () => import('../views/errors/400.vue') },
  { path: '/401', name: 'Unauthorized', component: () => import('../views/errors/401.vue') },
  { path: '/403', name: 'Forbidden', component: () => import('../views/errors/403.vue') },
  { path: '/404', name: 'NotFound', component: () => import('../views/errors/404.vue') },
  { path: '/405', name: 'MethodNotAllowed', component: () => import('../views/errors/405.vue') },
  { path: '/408', name: 'RequestTimeout', component: () => import('../views/errors/408.vue') },
  { path: '/413', name: 'PayloadTooLarge', component: () => import('../views/errors/413.vue') },
  { path: '/429', name: 'TooManyRequests', component: () => import('../views/errors/429.vue') },
  { path: '/500', name: 'SurverError', component: () => import('../views/errors/500.vue') },
  { path: '/502', name: 'BadGateway', component: () => import('../views/errors/502.vue') },
  { path: '/503', name: 'ServiceUnavailable', component: () => import('../views/errors/503.vue') },
  { path: '/504', name: 'GatewayTimeout', component: () => import('../views/errors/504.vue') },
]

// 路由配置
const routes = [
  // 公开页面
  {
    path: '/',
    name: 'Home',
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
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/Contact.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guestOnly: true }
  },

  // 管理页面（Editor+）- 嵌套路由
  {
    path: '/manage',
    name: 'ManageLayout',
    component: () => import('../views/manage/ManageLayout.vue'),
    meta: { requiresAuth: true, requiresEditor: true },
    redirect: '/manage/list',
    children: [
      {
        path: 'list',
        name: 'ManageList',
        component: () => import('../views/manage/ManageList.vue'),
        meta: { requiresAuth: true, requiresEditor: true }
      },
      {
        path: 'publish',
        name: 'ManagePublish',
        component: () => import('../views/manage/ManagePublish.vue'),
        meta: { requiresAuth: true, requiresEditor: true }
      }
    ]
  },

  // 管理员专属（Admin）- 嵌套路由
  {
    path: '/manage/admin',
    name: 'AdminLayout',
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/manage/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/AdminDashboard.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/AdminUsers.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'entries',
        name: 'AdminEntries',
        component: () => import('../views/admin/AdminEntries.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      }
    ]
  },

  // 错误页面
  ...errorRoutes,
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 在每次导航时恢复登录状态
  authStore.restoreState()

  const { requiresAuth, requiresEditor, requiresAdmin, guestOnly } = to.meta

  // 未登录且需要认证
  if (requiresAuth && !authStore.isLoggedIn) {
    return next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }

  // 仅未登录可访问
  if (guestOnly && authStore.isLoggedIn) {
    return next('/')  // 已登录用户访问登录/注册页，跳转到首页
  }

  // 需要 Editor 权限
  if (requiresEditor && !authStore.hasEditorPerm) {
    return next('/403')
  }

  // 需要 Admin 权限
  if (requiresAdmin && !authStore.hasAdminPerm) {
    return next('/403')
  }

  next()
})

export default router