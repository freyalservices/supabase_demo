import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('../views/SignupView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('../views/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
      },
      {
        path: 'upload',
        name: 'Upload',
        component: () => import('../views/UploadView.vue'),
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('../views/HistoryView.vue'),
      },
      {
        path: 'detection/:id',
        name: 'DetectionDetail',
        component: () => import('../views/DetectionDetailView.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'Login' }
  }
  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'Dashboard' }
  }
})

export default router
