<template>
  <button
    :disabled="loading || !configured"
    class="google-login-btn"
    @click="loginWithGoogle"
  >
    <svg
      v-if="!loading"
      class="google-icon"
      viewBox="0 0 24 24"
    >
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
    <span
      v-if="loading"
      class="spinner-small"
    />
    <span class="button-text">{{ buttonText }}</span>
  </button>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

export default {
    name: 'GoogleLoginButton',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        const loading = ref(false)
        const configured = ref(false)
        const error = ref(null)

        const buttonText = computed(() => {
            if (loading.value) return 'Connecting...'
            if (!configured.value) return 'Google Login Unavailable'
            return 'Continue with Google'
        })

        // Check if Google OAuth is configured
        onMounted(async () => {
            try {
                const response = await api.get('/auth/google/status')
                configured.value = response.data.configured
            } catch (err) {
                console.error('Failed to check Google OAuth status:', err)
                // Assume configured to allow login attempts even if status check fails
                configured.value = true
            }
        })

        const loginWithGoogle = async () => {
            if (!configured.value || loading.value) return

            loading.value = true
            error.value = null

            try {
                // Generate state for CSRF protection
                const state = generateRandomState()
                localStorage.setItem('oauth_state', state)

                // Determine redirect URI based on current host
                const redirectUri = `${window.location.origin}/auth/google/callback`

                // Get Google OAuth URL from backend
                const response = await api.post('/auth/google/url', {
                    redirect_uri: redirectUri,
                    state: state
                })

                if (response.data.success && response.data.auth_url) {
                    // Redirect to Google
                    window.location.href = response.data.auth_url
                } else {
                    throw new Error('Failed to get Google authorization URL')
                }
            } catch (err) {
                console.error('Google OAuth error:', err)
                error.value = err.response?.data?.detail || 'Failed to initiate Google login'
                loading.value = false
            }
        }

        const generateRandomState = () => {
            const array = new Uint8Array(32)
            crypto.getRandomValues(array)
            return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
        }

        return {
            loading,
            configured,
            buttonText,
            loginWithGoogle
        }
    }
}
</script>

<style scoped>
.google-login-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    width: 100%;
    padding: 0.75rem 1.5rem;
    background: white;
    border: 2px solid #dadce0;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 500;
    color: #3c4043;
    cursor: pointer;
    transition: all 0.2s;
}

.google-login-btn:hover:not(:disabled) {
    background: #f8f9fa;
    border-color: #c6c9cc;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.google-login-btn:active:not(:disabled) {
    background: #f1f3f4;
}

.google-login-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.google-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
}

.button-text {
    color: #3c4043;
}

.spinner-small {
    width: 20px;
    height: 20px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid #4285F4;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

/* Dark mode support */
:root[data-theme="dark"] .google-login-btn {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
}

:root[data-theme="dark"] .google-login-btn:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
}

:root[data-theme="dark"] .button-text {
    color: #e2e8f0;
}
</style>
