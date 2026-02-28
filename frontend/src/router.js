import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/views/CategoryList.vue'),
  },
  {
    path: '/:invalidPath(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory('/nexus'),
  routes,
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = window.is_logged_in || (window.user_id && window.user_id !== 'Guest')
  if (!isLoggedIn) {
    window.location.href = '/login?redirect-to=/nexus'
    return
  }
  next()
})

export default router
