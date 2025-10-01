import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/courses',
      name: 'courses',
      component: () => import('../views/CoursesView.vue')
    },
    {
      path: '/course/:id',
      name: 'course',
      component: () => import('../views/CourseView.vue')
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('../views/PrivacyView.vue')
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('../views/TermsView.vue')
    }
  ]
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const publicPages = ['/', '/login', '/privacy', '/terms']
  // Allow guests to view courses (they have localStorage courses)
  const isCoursePage = to.path.startsWith('/course/')
  const authRequired = !publicPages.includes(to.path) && !isCoursePage

  console.log('[Router] Navigation to:', to.path)
  console.log('[Router] Is authenticated:', authStore.isAuthenticated)
  console.log('[Router] Auth required:', authRequired)

  if (authRequired && !authStore.isAuthenticated) {
    console.log('[Router] ❌ Redirecting to login - auth required but not authenticated')
    // Redirect to login with return path
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else {
    console.log('[Router] ✅ Allowing navigation')
    next()
  }
})

export default router
