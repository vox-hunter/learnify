<template>
  <div class="username-selection">
    <div class="container">
      <div class="username-card">
        <div
          v-if="loading"
          class="loading-state"
        >
          <div class="spinner" />
          <h2>Setting up your account...</h2>
        </div>

        <div
          v-else-if="error"
          class="error-state"
        >
          <div class="error-icon">
            ⚠️
          </div>
          <h2>Error</h2>
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
          v-else
          class="form-state"
        >
          <div class="header">
            <img
              v-if="userInfo.picture"
              :src="userInfo.picture"
              alt="Profile"
              class="profile-pic"
            >
            <h2>Choose Your Username</h2>
            <p class="welcome-text">
              Welcome, {{ userInfo.name }}!
            </p>
            <p class="email-text">
              {{ userInfo.email }}
            </p>
          </div>

          <form
            class="username-form"
            @submit.prevent="completeSignup"
          >
            <div class="form-group">
              <label class="form-label">Username</label>
              <input
                v-model="username"
                type="text"
                class="form-input"
                required
                placeholder="Choose a unique username"
                @input="checkUsername"
              >
              <p
                v-if="usernameChecking"
                class="form-hint checking"
              >
                Checking availability...
              </p>
              <p
                v-else-if="usernameAvailable === false"
                class="form-hint error"
              >
                Username is already taken
              </p>
              <p
                v-else-if="usernameAvailable === true"
                class="form-hint success"
              >
                Username is available!
              </p>
            </div>

            <div
              v-if="submitError"
              class="alert alert-error"
            >
              {{ submitError }}
            </div>

            <button
              type="submit"
              :disabled="submitting || !usernameAvailable || usernameChecking"
              class="btn btn-primary btn-block"
            >
              {{ submitting ? 'Creating Account...' : 'Complete Sign Up' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

export default {
  name: 'GoogleUsernameView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const loading = ref(true)
    const error = ref(null)
    const userInfo = ref({})
    const oauthData = ref({})
    const username = ref('')
    const usernameChecking = ref(false)
    const usernameAvailable = ref(null)
    const submitError = ref(null)
    const submitting = ref(false)

    let checkTimeout = null

    onMounted(() => {
      // Get OAuth data from sessionStorage
      const storedData = sessionStorage.getItem('google_oauth_pending')
      if (!storedData) {
        error.value = 'No OAuth data found. Please try logging in again.'
        loading.value = false
        return
      }

      try {
        const data = JSON.parse(storedData)
        oauthData.value = data
        userInfo.value = data.user_info

        // Set default username from email (before @)
        const emailUsername = data.user_info.email.split('@')[0]
        username.value = emailUsername.replace(/[^a-zA-Z0-9_]/g, '_')

        loading.value = false

        // Check initial username availability
        checkUsername()
      } catch (err) {
        error.value = 'Invalid OAuth data'
        loading.value = false
      }
    })

    const checkUsername = () => {
      if (!username.value || username.value.length < 3) {
        usernameAvailable.value = null
        return
      }

      usernameChecking.value = true

      // Debounce
      clearTimeout(checkTimeout)
      checkTimeout = setTimeout(async () => {
        try {
          const response = await api.get(`/auth/check-username?username=${username.value}`)
          usernameAvailable.value = response.data.available
        } catch (err) {
          console.error('Error checking username:', err)
          usernameAvailable.value = null
        } finally {
          usernameChecking.value = false
        }
      }, 500)
    }

    const completeSignup = async () => {
      if (!usernameAvailable.value) return

      submitting.value = true
      submitError.value = null

      try {
        // Complete the OAuth signup with chosen username
        const payload = {
          username: username.value
        }
        if (oauthData.value.signup_token) {
          payload.signup_token = oauthData.value.signup_token
        } else {
          // Legacy fallback if user arrived with old storage
          payload.code = oauthData.value.code
          payload.redirect_uri = oauthData.value.redirect_uri
          payload.state = oauthData.value.state
        }
        const response = await api.post('/auth/google/complete', payload)

        if (response.data.success) {
          // Clear pending data
          sessionStorage.removeItem('google_oauth_pending')

          // Update auth store
          authStore.user = {
            username: response.data.username,
            name: response.data.name,
            email: response.data.email,
            picture: response.data.picture,
            isAdmin: response.data.isAdmin,
            isGoogleUser: true
          }

          localStorage.setItem('username', response.data.username)

          // Redirect to home
          router.push('/')
        } else {
          throw new Error('Signup failed')
        }
      } catch (err) {
        console.error('Signup error:', err)
        // Always show backend error message, clarify for user if needed
        let detail = err.response?.data?.detail || 'Failed to complete signup';
        if (detail.includes('Username is already taken')) {
          detail = 'That username is already taken. Please choose another.';
        } else if (detail.includes('Email already registered')) {
          detail = 'An account with this email already exists. Please log in.';
        }
        submitError.value = detail;
      } finally {
        submitting.value = false;
      }
    }

    watch(username, () => {
      usernameAvailable.value = null
    })

    return {
      loading,
      error,
      userInfo,
      username,
      usernameChecking,
      usernameAvailable,
      submitError,
      submitting,
      checkUsername,
      completeSignup
    }
  }
}
</script>

<style scoped>
.username-selection {
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

.username-card {
  background: var(--card-bg);
  border-radius: 1rem;
  padding: 3rem 2rem;
  box-shadow: 0 10px 40px var(--shadow-color);
}

.loading-state,
.error-state,
.form-state {
  text-align: center;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.error-message {
  color: #ef4444;
  margin-bottom: 1.5rem;
}

.header {
  margin-bottom: 2rem;
}

.profile-pic {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto 1rem;
  display: block;
  border: 3px solid var(--accent-primary);
}

h2 {
  font-size: 1.75rem;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
}

.welcome-text {
  color: var(--text-secondary);
  font-size: 1rem;
  margin: 0.5rem 0;
}

.email-text {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0;
}

.username-form {
  text-align: left;
}

.form-hint.checking {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.form-hint.error {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.form-hint.success {
  color: #22c55e;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}
</style>
