<template>
  <div class="login-view">
    <div class="container-sm">
      <div class="login-card card">
        <h1 class="page-title">Welcome Back</h1>
        
        <!-- Tabs -->
        <div class="tabs">
          <button 
            :class="['tab', { active: activeTab === 'login' }]"
            @click="activeTab = 'login'"
          >
            🚀 Login
          </button>
          <button 
            :class="['tab', { active: activeTab === 'register' }]"
            @click="activeTab = 'register'"
          >
            ✨ Register
          </button>
        </div>

        <!-- Login Form -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label class="form-label">Username or Email</label>
            <input
              v-model="loginForm.username"
              type="text"
              class="form-input"
              required
              placeholder="Enter your username or email"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Password</label>
            <input
              v-model="loginForm.password"
              type="password"
              class="form-input"
              required
              placeholder="Enter your password"
            />
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="loginForm.rememberMe"
                type="checkbox"
                class="checkbox-input"
              />
              <span>Remember me</span>
            </label>
          </div>

          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <button type="submit" :disabled="loading" class="btn btn-primary btn-block">
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>

        <!-- Register Form -->
        <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label class="form-label">Username</label>
            <input
              v-model="registerForm.username"
              type="text"
              class="form-input"
              required
              placeholder="Choose a username"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              v-model="registerForm.email"
              type="email"
              class="form-input"
              required
              placeholder="Enter your email"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input
              v-model="registerForm.name"
              type="text"
              class="form-input"
              required
              placeholder="Enter your full name"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Password</label>
            <input
              v-model="registerForm.password"
              type="password"
              class="form-input"
              required
              placeholder="Choose a password"
              minlength="6"
            />
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="registerForm.marketing_consent"
                type="checkbox"
                class="checkbox-input"
              />
              <span>I agree to receive marketing emails</span>
            </label>
          </div>

          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <div v-if="success" class="alert alert-success">
            {{ success }}
          </div>

          <button type="submit" :disabled="loading" class="btn btn-primary btn-block">
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>
        </form>

        <!-- OAuth Options (placeholder for future implementation) -->
        <div class="oauth-section">
          <div class="divider">
            <span>Or continue with</span>
          </div>
          <button class="btn-oauth" disabled>
            <span>🔒 Google OAuth (Coming Soon)</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()

    const activeTab = ref('login')
    const loading = ref(false)
    const error = ref(null)
    const success = ref(null)

    const loginForm = ref({
      username: '',
      password: '',
      rememberMe: false
    })

    const registerForm = ref({
      username: '',
      email: '',
      name: '',
      password: '',
      marketing_consent: false
    })

    const handleLogin = async () => {
      loading.value = true
      error.value = null

      const result = await authStore.login(
        loginForm.value.username,
        loginForm.value.password,
        loginForm.value.rememberMe
      )

      loading.value = false

      if (result.success) {
        // Redirect to the original page or home
        const redirect = route.query.redirect || '/'
        router.push(redirect)
      } else {
        error.value = result.error
      }
    }

    const handleRegister = async () => {
      loading.value = true
      error.value = null
      success.value = null

      const result = await authStore.register(registerForm.value)

      loading.value = false

      if (result.success) {
        success.value = 'Account created successfully! You can now login.'
        // Clear form
        registerForm.value = {
          username: '',
          email: '',
          name: '',
          password: '',
          marketing_consent: false
        }
        // Switch to login tab after 2 seconds
        setTimeout(() => {
          activeTab.value = 'login'
        }, 2000)
      } else {
        error.value = result.error
      }
    }

    return {
      activeTab,
      loading,
      error,
      success,
      loginForm,
      registerForm,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.login-view {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  padding: 2rem 0;
}

.login-card {
  max-width: 500px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  text-align: center;
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  background: rgba(6, 182, 212, 0.1);
  border-radius: 0.75rem;
  padding: 0.25rem;
  margin-bottom: 2rem;
}

.tab {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: #a0aec0;
  font-weight: 500;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.tab.active {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  color: white;
  box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
}

.auth-form {
  margin-bottom: 2rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #cbd5e0;
  cursor: pointer;
}

.checkbox-input {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.btn-block {
  width: 100%;
}

.oauth-section {
  margin-top: 2rem;
}

.divider {
  position: relative;
  text-align: center;
  margin: 2rem 0;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.divider span {
  position: relative;
  background: rgba(15, 23, 42, 0.95);
  padding: 0 1rem;
  color: #cbd5e0;
  font-size: 0.875rem;
}

.btn-oauth {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: #cbd5e0;
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
