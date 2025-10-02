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
            <div class="form-row">
              <label class="checkbox-label">
                <input
                  v-model="loginForm.rememberMe"
                  type="checkbox"
                  class="checkbox-input"
                />
                <span>Remember me</span>
              </label>
              <button 
                type="button" 
                @click="showForgotPassword = true; activeTab = 'forgot'"
                class="btn-link forgot-link"
              >
                Forgot password?
              </button>
            </div>
          </div>

          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <button type="submit" :disabled="loading" class="btn btn-primary btn-block">
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>

        <!-- Forgot Password - Step 1: Enter Email -->
        <form v-if="activeTab === 'forgot' && !showResetVerification" @submit.prevent="handleForgotPassword" class="auth-form">
          <div class="forgot-header">
            <h2 class="verification-title">🔐 Reset Password</h2>
            <p class="verification-text">
              Enter your email address and we'll send you a verification code
            </p>
          </div>

          <div class="form-group">
            <label class="form-label">Email Address</label>
            <input
              v-model="forgotPasswordForm.email"
              type="email"
              class="form-input"
              required
              placeholder="Enter your email"
            />
          </div>

          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <button type="submit" :disabled="loading" class="btn btn-primary btn-block">
            {{ loading ? 'Sending code...' : 'Send Verification Code' }}
          </button>

          <button @click="activeTab = 'login'; showForgotPassword = false; error = null" class="btn-link" type="button">
            ← Back to login
          </button>
        </form>

        <!-- Forgot Password - Step 2: Verify Code & Reset -->
        <div v-if="activeTab === 'forgot' && showResetVerification" class="auth-form">
          <div class="verification-header">
            <h2 class="verification-title">🔐 Reset Password</h2>
            <p class="verification-text">
              We've sent a 6-digit code to <strong>{{ forgotPasswordForm.email }}</strong>
            </p>
          </div>

          <div class="form-group">
            <label class="form-label">Verification Code</label>
            <input
              v-model="forgotPasswordForm.code"
              type="text"
              class="form-input verification-input"
              required
              placeholder="Enter 6-digit code"
              maxlength="6"
              pattern="[0-9]{6}"
            />
          </div>

          <div class="form-group">
            <label class="form-label">New Password</label>
            <input
              v-model="forgotPasswordForm.newPassword"
              type="password"
              class="form-input"
              required
              placeholder="Enter new password"
              minlength="6"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Confirm Password</label>
            <input
              v-model="forgotPasswordForm.confirmPassword"
              type="password"
              class="form-input"
              required
              placeholder="Confirm new password"
              minlength="6"
            />
          </div>

          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <div v-if="success" class="alert alert-success">
            {{ success }}
          </div>

          <button 
            @click="handleResetPassword" 
            :disabled="loading || forgotPasswordForm.code.length !== 6"
            class="btn btn-primary btn-block"
            type="button"
          >
            {{ loading ? 'Resetting...' : 'Reset Password' }}
          </button>

          <div class="resend-section">
            <button 
              @click="handleResendResetCode" 
              :disabled="resetResendCooldown > 0"
              class="btn-link"
              type="button"
            >
              {{ resetResendCooldown > 0 ? `Resend code in ${resetResendCooldown}s` : 'Resend verification code' }}
            </button>
          </div>

          <button @click="showResetVerification = false; error = null; success = null" class="btn-link" type="button">
            ← Back to email entry
          </button>
        </div>

        <!-- Register Form - Step 1: User Details -->
        <form v-if="activeTab === 'register' && !showVerification" @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              v-model="registerForm.email"
              type="email"
              class="form-input"
              required
              placeholder="Enter your email"
            />
            <p class="form-hint">We'll send a verification code to this email</p>
          </div>

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

          <button type="submit" :disabled="loading" class="btn btn-primary btn-block">
            {{ loading ? 'Sending verification code...' : 'Continue' }}
          </button>
        </form>

        <!-- Register Form - Step 2: Email Verification -->
        <div v-if="activeTab === 'register' && showVerification" class="auth-form">
          <div class="verification-header">
            <h2 class="verification-title">📧 Verify Your Email</h2>
            <p class="verification-text">
              We've sent a 6-digit code to <strong>{{ registerForm.email }}</strong>
            </p>
          </div>

          <div class="form-group">
            <label class="form-label">Verification Code</label>
            <input
              v-model="verificationCode"
              type="text"
              class="form-input verification-input"
              required
              placeholder="Enter 6-digit code"
              maxlength="6"
              pattern="[0-9]{6}"
            />
          </div>

          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <div v-if="success" class="alert alert-success">
            {{ success }}
          </div>

          <button 
            @click="handleVerifyEmail" 
            :disabled="loading || verificationCode.length !== 6"
            class="btn btn-primary btn-block"
          >
            {{ loading ? 'Verifying...' : 'Verify & Complete Registration' }}
          </button>

          <div class="resend-section">
            <button 
              @click="handleResendCode" 
              :disabled="resendCooldown > 0"
              class="btn-link"
              type="button"
            >
              {{ resendCooldown > 0 ? `Resend code in ${resendCooldown}s` : 'Resend verification code' }}
            </button>
          </div>

          <button @click="showVerification = false; error = null" class="btn-link" type="button">
            ← Back to registration
          </button>
        </div>

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
import api from '../services/api'

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
    const showVerification = ref(false)
    const verificationCode = ref('')
    const resendCooldown = ref(0)
    const showForgotPassword = ref(false)
    const showResetVerification = ref(false)
    const resetResendCooldown = ref(0)

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

    const forgotPasswordForm = ref({
      email: '',
      code: '',
      newPassword: '',
      confirmPassword: ''
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

      try {
        // Step 1: Send verification email
        const response = await api.post('/auth/send-verification', {
          email: registerForm.value.email
        })

        if (response.data.success) {
          showVerification.value = true
          success.value = 'Verification code sent! Check your email.'
          startResendCooldown()
        }
      } catch (err) {
        if (err.response) {
          error.value = err.response.data?.detail || `Server error: ${err.response.status}`
        } else if (err.request) {
          error.value = 'Cannot connect to server. Please check if the backend is running.'
        } else {
          error.value = err.message || 'Failed to send verification code'
        }
      } finally {
        loading.value = false
      }
    }

    const handleVerifyEmail = async () => {
      loading.value = true
      error.value = null
      success.value = null

      try {
        // Step 2: Verify email code
        const verifyResponse = await api.post('/auth/verify-email', {
          email: registerForm.value.email,
          code: verificationCode.value
        })

        if (verifyResponse.data.success) {
          // Step 3: Complete registration
          const result = await authStore.register(registerForm.value)

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
            verificationCode.value = ''
            showVerification.value = false
            
            // Switch to login tab after 2 seconds
            setTimeout(() => {
              activeTab.value = 'login'
              success.value = null
            }, 2000)
          } else {
            error.value = result.error
          }
        }
      } catch (err) {
        if (err.response) {
          error.value = err.response.data?.detail || `Server error: ${err.response.status}`
        } else if (err.request) {
          error.value = 'Cannot connect to server. Please check if the backend is running.'
        } else {
          error.value = err.message || 'Verification failed'
        }
      } finally {
        loading.value = false
      }
    }

    const handleResendCode = async () => {
      loading.value = true
      error.value = null
      success.value = null

      try {
        const response = await api.post('/auth/send-verification', {
          email: registerForm.value.email
        })

        if (response.data.success) {
          success.value = 'Verification code resent!'
          startResendCooldown()
        }
      } catch (err) {
        if (err.response) {
          error.value = err.response.data?.detail || `Server error: ${err.response.status}`
        } else if (err.request) {
          error.value = 'Cannot connect to server. Please check if the backend is running.'
        } else {
          error.value = err.message || 'Failed to resend code'
        }
      } finally {
        loading.value = false
      }
    }

    const startResendCooldown = () => {
      resendCooldown.value = 60
      const interval = setInterval(() => {
        resendCooldown.value--
        if (resendCooldown.value <= 0) {
          clearInterval(interval)
        }
      }, 1000)
    }

    const startResetResendCooldown = () => {
      resetResendCooldown.value = 60
      const interval = setInterval(() => {
        resetResendCooldown.value--
        if (resetResendCooldown.value <= 0) {
          clearInterval(interval)
        }
      }, 1000)
    }

    const handleForgotPassword = async () => {
      loading.value = true
      error.value = null
      success.value = null

      try {
        // Send password reset verification code
        const response = await api.post('/auth/forgot-password', {
          email: forgotPasswordForm.value.email
        })

        if (response.data.success) {
          showResetVerification.value = true
          success.value = 'Verification code sent! Check your email.'
          startResetResendCooldown()
        }
      } catch (err) {
        if (err.response) {
          error.value = err.response.data?.detail || `Server error: ${err.response.status}`
        } else if (err.request) {
          error.value = 'Cannot connect to server. Please check if the backend is running.'
        } else {
          error.value = err.message || 'Failed to send verification code'
        }
      } finally {
        loading.value = false
      }
    }

    const handleResetPassword = async () => {
      loading.value = true
      error.value = null
      success.value = null

      // Validate passwords match
      if (forgotPasswordForm.value.newPassword !== forgotPasswordForm.value.confirmPassword) {
        error.value = 'Passwords do not match'
        loading.value = false
        return
      }

      try {
        // Verify code and reset password
        const response = await api.post('/auth/reset-password', {
          email: forgotPasswordForm.value.email,
          code: forgotPasswordForm.value.code,
          new_password: forgotPasswordForm.value.newPassword
        })

        if (response.data.success) {
          success.value = 'Password reset successfully! Redirecting to login...'
          
          // Clear form
          forgotPasswordForm.value = {
            email: '',
            code: '',
            newPassword: '',
            confirmPassword: ''
          }
          
          // Switch to login tab after 2 seconds
          setTimeout(() => {
            activeTab.value = 'login'
            showForgotPassword.value = false
            showResetVerification.value = false
            success.value = null
          }, 2000)
        }
      } catch (err) {
        if (err.response) {
          error.value = err.response.data?.detail || `Server error: ${err.response.status}`
        } else if (err.request) {
          error.value = 'Cannot connect to server. Please check if the backend is running.'
        } else {
          error.value = err.message || 'Failed to reset password'
        }
      } finally {
        loading.value = false
      }
    }

    const handleResendResetCode = async () => {
      loading.value = true
      error.value = null
      success.value = null

      try {
        const response = await api.post('/auth/forgot-password', {
          email: forgotPasswordForm.value.email
        })

        if (response.data.success) {
          success.value = 'Verification code resent!'
          startResetResendCooldown()
        }
      } catch (err) {
        if (err.response) {
          error.value = err.response.data?.detail || `Server error: ${err.response.status}`
        } else if (err.request) {
          error.value = 'Cannot connect to server. Please check if the backend is running.'
        } else {
          error.value = err.message || 'Failed to resend code'
        }
      } finally {
        loading.value = false
      }
    }

    return {
      activeTab,
      loading,
      error,
      success,
      showVerification,
      verificationCode,
      resendCooldown,
      showForgotPassword,
      showResetVerification,
      resetResendCooldown,
      loginForm,
      registerForm,
      forgotPasswordForm,
      handleLogin,
      handleRegister,
      handleVerifyEmail,
      handleResendCode,
      handleForgotPassword,
      handleResetPassword,
      handleResendResetCode
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

.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.forgot-link {
  color: #06b6d4;
  font-size: 0.875rem;
  text-decoration: none;
  transition: all 0.2s;
}

.forgot-link:hover {
  color: #0891b2;
  text-decoration: underline;
}

.verification-header {
  margin-bottom: 2rem;
  text-align: center;
}

.forgot-header {
  margin-bottom: 2rem;
  text-align: center;
}

.verification-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 0.75rem;
}

.forgot-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 0.75rem;
}

.verification-text {
  color: #cbd5e0;
  line-height: 1.6;
}

.forgot-text {
  color: #cbd5e0;
  line-height: 1.6;
}

.verification-text strong {
  color: #06b6d4;
  font-weight: 600;
}

.forgot-text strong {
  color: #06b6d4;
  font-weight: 600;
}

.verification-input {
  text-align: center;
  font-size: 1.5rem;
  letter-spacing: 0.5rem;
  font-family: 'Courier New', Courier, monospace;
  font-weight: 600;
}

.resend-section {
  margin: 1rem 0;
  text-align: center;
}

.btn-link {
  background: none;
  border: none;
  color: #06b6d4;
  cursor: pointer;
  padding: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-link:hover:not(:disabled) {
  color: #0891b2;
  text-decoration: underline;
}

.btn-link:disabled {
  color: #a0aec0;
  cursor: not-allowed;
}

.form-hint {
  font-size: 0.875rem;
  color: #a0aec0;
  margin-top: 0.25rem;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .verification-input {
    font-size: 1.25rem;
    letter-spacing: 0.25rem;
  }
}
</style>
