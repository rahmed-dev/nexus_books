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
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/views/TransactionList.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsPage.vue'),
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/views/CategoryList.vue'),
  },
  {
    path: '/accounts',
    name: 'Accounts',
    component: () => import('@/views/AccountList.vue'),
  },
  {
    path: '/settings/dashboard',
    name: 'DashboardConfig',
    component: () => import('@/views/DashboardConfig.vue'),
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
