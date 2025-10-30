import { createRouter, createWebHistory } from 'vue-router'

import HomeView  from '../views/Home.vue'
import LogInView from '../views/Login.vue'
import RegisterView from  '../views/Register.vue'
import ContactView from '../views/Contact.vue'
import AdminView from '../views/Admin.vue'
import MainView from '../views/Main.vue'
import NotFoundView from '../views/404.vue'
import ForbiddenView from '../views/403.vue'
import UnauthorizedView from '../views/401.vue'
import BadRequestView from '../views/400.vue'
import SurverErrorView from '../views/500.vue'


// 路由配置
const routes = [
  { path: '/', component: HomeView  },
  { path: '/login', component: LogInView },
  { path: '/register', component: RegisterView},
  { path: '/contact', component: ContactView },
  { path: '/admin', component: AdminView },
  { path: '/main', component: MainView },
  { path: '/admin-login', component: AdminView },
  { path: '/400', name: 'BadRequest', component: BadRequestView },
  { path: '/401', name: 'Unauthorized', component: UnauthorizedView },
  { path: '/403', name: 'Forbidden', component: ForbiddenView },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundView }, // 404
  { path: '/500', name: 'SurverError', component: SurverErrorView },

]


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
