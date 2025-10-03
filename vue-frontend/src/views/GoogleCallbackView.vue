<template>
  <div class="oauth-callback">
    <div class="container">
      <div class="callback-card">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <h2>Completing Google Sign In...</h2>
          <p>Please wait while we verify your account</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <h2>Authentication Failed</h2>
          <p class="error-message">{{ error }}</p>
          <button @click="$router.push('/login')" class="btn btn-primary">
            Back to Login
          </button>
        </div>

        <div v-else-if="success" class="success-state">
          <div class="success-icon">✓</div>
          <h2>Welcome{{ userName ? `, ${userName}` : '' }}!</h2>
          <p>{{ isNewUser ? 'Your account has been created successfully.' : 'Successfully signed in.' }}</p>
          <p class="redirect-message">Redirecting to home...</p>
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
          // Update auth store
          authStore.user = {
            username: response.data.username,
            name: response.data.name,
            email: response.data.email,
            picture: response.data.picture,
            isAdmin: response.data.isAdmin
          }
          
          // Store username for API requests
          localStorage.setItem('username', response.data.username)
          
          userName.value = response.data.name || response.data.username
          isNewUser.value = response.data.is_new_user
          success.value = true
          loading.value = false

          // Redirect to home after 2 seconds
          setTimeout(() => {
            router.push('/')
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
      isNewUser
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
