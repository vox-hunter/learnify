<template>
  <div class="oauth-callback">
    <div class="container">
      <div class="callback-card">
        <div
          v-if="loading"
          class="loading-state"
        >
          <div class="spinner" />
          <h2>Completing Google Sign In...</h2>
          <p>Please wait while we verify your account</p>
        </div>

        <div
          v-else-if="error"
          class="error-state"
        >
          <div class="error-icon">
            ⚠️
          </div>
          <h2>Authentication Failed</h2>
          <p class="error-message">
            {{ error }}
          </p>
          <button
            class="btn btn-primary"
            @click="$router.push('/login')"
          >
            Back to Login
          </button>
        </div>

        <div
          v-else-if="success"
          class="success-state"
        >
          <div class="success-icon">
            ✓
          </div>
          <h2>{{ isLinking ? 'Account Linked!' : `Welcome${userName ? `, ${userName}` : ''}!` }}</h2>
          <p>{{ isNewUser ? 'Your account has been created successfully.' : isLinking ? 'Google account has been linked to your account.' : 'Successfully signed in.' }}</p>
          <p class="redirect-message">
            Redirecting to {{ redirectTarget }}...
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

export default {
  name: 'GoogleCallbackView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()
    
    const loading = ref(true)
    const error = ref(null)
    const success = ref(false)
    const userName = ref('')
    const isNewUser = ref(false)
    const isLinking = ref(false)
    const redirectTarget = ref('')

    const handleCallback = async () => {
      try {
        // Get code and state from URL
        const code = route.query.code
        const state = route.query.state
        const storedState = localStorage.getItem('oauth_state')

        // Validate state (CSRF protection)
        if (!state || state !== storedState) {
          throw new Error('Invalid state parameter. Possible CSRF attack.')
        }

        // Clear stored state
        localStorage.removeItem('oauth_state')

        if (!code) {
          throw new Error('No authorization code received from Google')
        }

        // Determine redirect URI (must match what was sent to Google)
        const redirectUri = `${window.location.origin}/auth/google/callback`

        // Send code to backend
        const response = await api.post('/auth/google/callback', {
          code: code,
          redirect_uri: redirectUri,
          state: state
        })

        if (response.data.success) {
          // Check if user needs to select username (new user)
          if (response.data.needs_username) {
            // Store OAuth data for username selection
            sessionStorage.setItem('google_oauth_pending', JSON.stringify({
              // Use signup_token flow to avoid reusing one-time code
              signup_token: response.data.signup_token || null,
              user_info: response.data.user_info
            }))
            
            // Redirect to username selection
            loading.value = false
            router.push('/auth/google/username')
            return
          }
          
          // Existing user or linked account - complete login
          authStore.user = {
            username: response.data.username,
            name: response.data.name,
            email: response.data.email,
            picture: response.data.picture,
            isAdmin: response.data.isAdmin,
            isGoogleUser: response.data.isGoogleUser || false,
            hasPassword: response.data.hasPassword || false
          }
          
          // Store username for API requests
          localStorage.setItem('username', response.data.username)
          
          // Store complete user data in both localStorage and sessionStorage
          const userData = JSON.stringify(authStore.user)
          localStorage.setItem('userData', userData)
          sessionStorage.setItem('userData', userData)
          
          // Store isAdmin flag if present
          if (response.data.isAdmin) {
            localStorage.setItem('isAdmin', 'true')
            sessionStorage.setItem('isAdmin', 'true')
          }
          
          console.log('[GoogleCallback] User data updated:', authStore.user)
          
          // Check if user was linking from account page
          const isLinkMode = localStorage.getItem('oauth_link_mode') === 'true'
          const redirectPath = localStorage.getItem('oauth_redirect') || null
          
          if (isLinkMode) {
            localStorage.removeItem('oauth_link_mode')
          }
          if (redirectPath) {
            localStorage.removeItem('oauth_redirect')
          }
          
          userName.value = response.data.name || response.data.username
          isNewUser.value = response.data.is_new_user && !isLinkMode
          isLinking.value = isLinkMode
          success.value = true
          loading.value = false

          // Determine redirect target for display
          if (redirectPath) {
            redirectTarget.value = redirectPath === '/' ? 'chat' : 'home'
          } else if (isLinkMode) {
            redirectTarget.value = 'account settings'
          } else {
            redirectTarget.value = 'home'
          }

          // Redirect based on context
          setTimeout(() => {
            if (redirectPath) {
              router.push(redirectPath)
            } else if (isLinkMode) {
              router.push('/account')
            } else {
              router.push('/')
            }
          }, 2000)
        } else {
          throw new Error('Authentication failed')
        }
      } catch (err) {
        console.error('OAuth callback error:', err)
        error.value = err.response?.data?.detail || err.message || 'Failed to complete Google sign in'
        loading.value = false
      }
    }

    onMounted(() => {
      handleCallback()
    })

    return {
      loading,
      error,
      success,
      userName,
      isNewUser,
      isLinking,
      redirectTarget
    }
  }
}
</script>

<style scoped>
.oauth-callback {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

.container {
  max-width: 500px;
  width: 100%;
}

.callback-card {
  background: var(--card-bg);
  border-radius: 1rem;
  padding: 3rem 2rem;
  box-shadow: 0 10px 40px var(--shadow-color);
  text-align: center;
}

.loading-state,
.error-state,
.success-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon,
.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
}

.error-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.success-icon {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  font-weight: bold;
}

h2 {
  font-size: 1.75rem;
  color: var(--text-primary);
  margin: 0;
}

p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 1rem;
}

.error-message {
  color: #ef4444;
  font-weight: 500;
}

.redirect-message {
  color: var(--text-muted);
  font-size: 0.875rem;
  font-style: italic;
}

.btn {
  margin-top: 1rem;
}
</style>
