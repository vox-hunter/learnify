import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/ChatView.vue'),
      meta: { public: true }
    },
    {
      path: '/old-home',
      name: 'old-home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/courses',
      name: 'myspace',
      alias: ['/my-space'],
      component: () => import('../views/CoursesView.vue')
    },
    {
      path: '/library',
      name: 'library',
      component: () => import('../views/LibraryView.vue'),
      meta: { public: true }
    },
    {
      path: '/course/:id',
      name: 'course',
      component: () => import('../views/CourseView.vue')
    },
    {
      path: '/flashcard/:id',
      name: 'flashcard',
      component: () => import('../views/FlashcardView.vue')
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('../views/PrivacyView.vue'),
      meta: { public: true }
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('../views/TermsView.vue'),
      meta: { public: true }
    },
    {
      path: '/account',
      name: 'account',
      component: () => import('../views/AccountView.vue')
    },
    {
      path: '/auth/google/callback',
      name: 'google-callback',
      component: () => import('../views/GoogleCallbackView.vue'),
      meta: { public: true }
    },
    {
      path: '/auth/google/username',
      name: 'google-username',
      component: () => import('../views/GoogleUsernameView.vue'),
      meta: { public: true }
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: () => import('../views/OnboardingView.vue'),
      meta: { requiresAuth: true }  // Comment 20: Explicitly mark as requiring auth
    }
  ]
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  // Use meta.public for public route detection
  const isPublicRoute = to.meta?.public === true
  const authRequired = !isPublicRoute

  // Comment 7: Wrap debug logs with import.meta.env.DEV to disable in production
  if (import.meta.env.DEV) {
    console.log('[Router] Navigation to:', to.path, 'name:', to.name)
    console.log('[Router] Is authenticated:', authStore.isAuthenticated)
    console.log('[Router] Auth required:', authRequired)
    console.log('[Router] Needs onboarding:', authStore.needsOnboarding)
  }

  // Check if not authenticated and route requires authentication
  if (authRequired && !authStore.isAuthenticated) {
    if (import.meta.env.DEV) {
      console.log('[Router] ❌ Redirecting to login - auth required but not authenticated')
    }
    // Redirect to login with return path
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } 
  // Check if authenticated but needs onboarding
  else if (authStore.needsOnboarding && to.path !== '/onboarding') {
    if (import.meta.env.DEV) {
      console.log('[Router] ⚠️ Redirecting to onboarding - user profile incomplete')
    }
    // Redirect to onboarding with intended destination
    next({
      path: '/onboarding',
      query: { redirect: to.fullPath }
    })
  }
  // Check if trying to access onboarding but already completed
  else if (to.path === '/onboarding' && authStore.isAuthenticated && !authStore.needsOnboarding) {
    if (import.meta.env.DEV) {
      console.log('[Router] ✅ Onboarding already completed, redirecting to home')
    }
    // Redirect to home if onboarding is already completed
    next('/')
  }
  else {
    if (import.meta.env.DEV) {
      console.log('[Router] ✅ Allowing navigation')
    }
    next()
  }
})

export default router
