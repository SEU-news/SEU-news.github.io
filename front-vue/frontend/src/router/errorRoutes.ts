// 错误页面路由数组
export const errorRoutes = [
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