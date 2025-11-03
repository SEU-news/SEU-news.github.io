// 错误页面路由配置
import BadRequestView from '../views/errors/400.vue'
import UnauthorizedView from '../views/errors/401.vue'
import ForbiddenView from '../views/errors/403.vue'
import NotFoundView from '../views/errors/404.vue'
import MethodNotAllowedView from '../views/errors/405.vue'
import RequestTimeoutView from '../views/errors/408.vue'
import PayloadTooLargeView from '../views/errors/413.vue'
import TooManyRequestsView from '../views/errors/429.vue'
import SurverErrorView from '../views/errors/500.vue'
import BadGatewayView from '../views/errors/502.vue'
import ServiceUnavailableView from '../views/errors/503.vue'
import GatewayTimeoutView from '../views/errors/504.vue'

// 错误页面路由数组
export const errorRoutes = [
  { path: '/400', name: 'BadRequest', component: BadRequestView },
  { path: '/401', name: 'Unauthorized', component: UnauthorizedView },
  { path: '/403', name: 'Forbidden', component: ForbiddenView },
  { path: '/404', name: 'NotFound', component: NotFoundView },
  { path: '/405', name: 'MethodNotAllowed', component: MethodNotAllowedView },
  { path: '/408', name: 'RequestTimeout', component: RequestTimeoutView },
  { path: '/413', name: 'PayloadTooLarge', component: PayloadTooLargeView },
  { path: '/429', name: 'TooManyRequests', component: TooManyRequestsView },
  { path: '/500', name: 'SurverError', component: SurverErrorView },
  { path: '/502', name: 'BadGateway', component: BadGatewayView },
  { path: '/503', name: 'ServiceUnavailable', component: ServiceUnavailableView },
  { path: '/504', name: 'GatewayTimeout', component: GatewayTimeoutView },
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