<template>
  <div class="login-view">
    <div class="container-sm">
      <Card class="login-card">
        <CardHeader>
          <CardTitle class="page-title">
            Welcome Back
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          <!-- Tabs -->
          <Tabs v-model="activeTab" default-value="login" class="mb-4">
            <TabsList class="grid w-full grid-cols-2">
              <TabsTrigger value="login">
                🚀 Login
              </TabsTrigger>
              <TabsTrigger value="register">
                ✨ Register
              </TabsTrigger>
            </TabsList>

            <!-- Login Form -->
            <TabsContent value="login">
              <form
                class="auth-form space-y-4"
                @submit.prevent="handleLogin"
              >
                <div class="space-y-2">
                  <Label for="login-username">Username or Email</Label>
                  <Input
                    id="login-username"
                    v-model="loginForm.username"
                    type="text"
                    required
                    placeholder="Enter your username or email"
                  />
                </div>

                <div class="space-y-2">
                  <Label for="login-password">Password</Label>
                  <Input
                    id="login-password"
                    v-model="loginForm.password"
                    type="password"
                    required
                    placeholder="Enter your password"
                  />
                </div>

                <div class="form-row">
                  <label class="flex items-center gap-2">
                    <Checkbox
                      v-model:checked="loginForm.rememberMe"
                      id="remember-me"
                    />
                    <span class="text-sm">Remember me</span>
                  </label>
                  <Button 
                    variant="link"
                    type="button" 
                    class="forgot-link p-0 h-auto"
                    @click="showForgotPassword = true; activeTab = 'forgot'"
                  >
                    Forgot password?
                  </Button>
                </div>

                <Alert v-if="error" variant="destructive">
                  <AlertDescription>
                    {{ error }}
                  </AlertDescription>
                </Alert>

                <Button
                  type="submit"
                  :disabled="loading"
                  class="w-full"
                >
                  {{ loading ? 'Logging in...' : 'Login' }}
                </Button>

                <!-- OAuth Divider -->
                <div class="oauth-divider">
                  <span>Or</span>
                </div>

                <!-- Google Login Button -->
                <GoogleLoginButton />
              </form>
            </TabsContent>

            <!-- Forgot Password Forms -->
            <div v-if="activeTab === 'forgot'" class="space-y-4">
              <!-- Forgot Password - Step 1: Enter Email -->
              <form
                v-if="!showResetVerification"
                class="auth-form space-y-4"
                @submit.prevent="handleForgotPassword"
              >
                <div class="forgot-header mb-6">
                  <h2 class="verification-title text-2xl font-semibold">
                    🔐 Reset Password
                  </h2>
                  <p class="verification-text text-muted-foreground">
                    Enter your email address and we'll send you a verification code
                  </p>
                </div>

                <div class="space-y-2">
                  <Label for="forgot-email">Email Address</Label>
                  <Input
                    id="forgot-email"
                    v-model="forgotPasswordForm.email"
                    type="email"
                    required
                    placeholder="Enter your email"
                  />
                </div>

                <Alert v-if="error" variant="destructive">
                  <AlertDescription>
                    {{ error }}
                  </AlertDescription>
                </Alert>

                <Button
                  type="submit"
                  :disabled="loading"
                  class="w-full"
                >
                  {{ loading ? 'Sending code...' : 'Send Verification Code' }}
                </Button>

                <Button
                  variant="link"
                  type="button"
                  class="w-full"
                  @click="activeTab = 'login'; showForgotPassword = false; error = null"
                >
                  ← Back to login
                </Button>
              </form>

              <!-- Forgot Password - Step 2: Verify Code & Reset -->
              <div
                v-if="showResetVerification"
                class="auth-form space-y-4"
              >
                <div class="verification-header mb-6">
                  <h2 class="verification-title text-2xl font-semibold">
                    🔐 Reset Password
                  </h2>
                  <p class="verification-text text-muted-foreground">
                    We've sent a 6-digit code to <strong>{{ forgotPasswordForm.email }}</strong>
                  </p>
                </div>

                <div class="space-y-2">
                  <Label for="reset-code">Verification Code</Label>
                  <Input
                    id="reset-code"
                    v-model="forgotPasswordForm.code"
                    type="text"
                    class="verification-input"
                    required
                    placeholder="Enter 6-digit code"
                    maxlength="6"
                    pattern="[0-9]{6}"
                  />
                </div>

                <div class="space-y-2">
                  <Label for="new-password">New Password</Label>
                  <Input
                    id="new-password"
                    v-model="forgotPasswordForm.newPassword"
                    type="password"
                    required
                    placeholder="Enter new password"
                    minlength="6"
                  />
                </div>

                <div class="space-y-2">
                  <Label for="confirm-password">Confirm Password</Label>
                  <Input
                    id="confirm-password"
                    v-model="forgotPasswordForm.confirmPassword"
                    type="password"
                    required
                    placeholder="Confirm new password"
                    minlength="6"
                  />
                </div>

                <Alert v-if="error" variant="destructive">
                  <AlertDescription>
                    {{ error }}
                  </AlertDescription>
                </Alert>

                <Alert v-if="success" variant="success">
                  <AlertDescription>
                    {{ success }}
                  </AlertDescription>
                </Alert>

                <Button 
                  :disabled="loading || forgotPasswordForm.code.length !== 6" 
                  class="w-full"
                  type="button"
                  @click="handleResetPassword"
                >
                  {{ loading ? 'Resetting...' : 'Reset Password' }}
                </Button>

                <div class="resend-section text-center">
                  <Button 
                    :disabled="resetResendCooldown > 0" 
                    variant="link"
                    type="button"
                    @click="handleResendResetCode"
                  >
                    {{ resetResendCooldown > 0 ? `Resend code in ${resetResendCooldown}s` : 'Resend verification code' }}
                  </Button>
                </div>

                <Button
                  variant="link"
                  type="button"
                  class="w-full"
                  @click="showResetVerification = false; error = null; success = null"
                >
                  ← Back to email entry
                </Button>
              </div>
            </div>

            <!-- Register Form - Step 1: User Details -->
            <TabsContent value="register">
              <form
                v-if="!showVerification"
                class="auth-form space-y-4"
                @submit.prevent="handleRegister"
              >
                <div class="space-y-2">
                  <Label for="register-email">Email</Label>
                  <Input
                    id="register-email"
                    v-model="registerForm.email"
                    type="email"
                    required
                    placeholder="Enter your email"
                  />
                  <p class="form-hint text-sm text-muted-foreground">
                    We'll send a verification code to this email
                  </p>
                </div>

                <div class="space-y-2">
                  <Label for="register-username">Username</Label>
                  <Input
                    id="register-username"
                    v-model="registerForm.username"
                    type="text"
                    required
                    placeholder="Choose a username"
                  />
                </div>

                <div class="space-y-2">
                  <Label for="register-name">Full Name</Label>
                  <Input
                    id="register-name"
                    v-model="registerForm.name"
                    type="text"
                    required
                    placeholder="Enter your full name"
                  />
                </div>

                <div class="space-y-2">
                  <Label for="register-password">Password</Label>
                  <Input
                    id="register-password"
                    v-model="registerForm.password"
                    type="password"
                    required
                    placeholder="Choose a password"
                    minlength="6"
                  />
                </div>

                <div>
                  <label class="flex items-center gap-2">
                    <Checkbox
                      v-model:checked="registerForm.marketing_consent"
                      id="marketing-consent"
                    />
                    <span class="text-sm">I agree to receive marketing emails</span>
                  </label>
                </div>

                <Alert v-if="error" variant="destructive">
                  <AlertDescription>
                    {{ error }}
                  </AlertDescription>
                </Alert>

                <Button
                  type="submit"
                  :disabled="loading"
                  class="w-full"
                >
                  {{ loading ? 'Sending verification code...' : 'Continue' }}
                </Button>

                <!-- OAuth Divider -->
                <div class="oauth-divider">
                  <span>Or</span>
                </div>

                <!-- Google Login Button -->
                <GoogleLoginButton />
              </form>

              <!-- Register Form - Step 2: Email Verification -->
              <div
                v-if="showVerification"
                class="auth-form space-y-4"
              >
                <div class="verification-header mb-6">
                  <h2 class="verification-title text-2xl font-semibold">
                    📧 Verify Your Email
                  </h2>
                  <p class="verification-text text-muted-foreground">
                    We've sent a 6-digit code to <strong>{{ registerForm.email }}</strong>
                  </p>
                </div>

                <div class="space-y-2">
                  <Label for="verification-code">Verification Code</Label>
                  <Input
                    id="verification-code"
                    v-model="verificationCode"
                    type="text"
                    class="verification-input"
                    required
                    placeholder="Enter 6-digit code"
                    maxlength="6"
                    pattern="[0-9]{6}"
                  />
                </div>

                <Alert v-if="error" variant="destructive">
                  <AlertDescription>
                    {{ error }}
                  </AlertDescription>
                </Alert>

                <Alert v-if="success" variant="success">
                  <AlertDescription>
                    {{ success }}
                  </AlertDescription>
                </Alert>

                <Button 
                  :disabled="loading || verificationCode.length !== 6" 
                  class="w-full"
                  @click="handleVerifyEmail"
                >
                  {{ loading ? 'Verifying...' : 'Verify & Complete Registration' }}
                </Button>

                <div class="resend-section text-center">
                  <Button 
                    :disabled="resendCooldown > 0" 
                    variant="link"
                    type="button"
                    @click="handleResendCode"
                  >
                    {{ resendCooldown > 0 ? `Resend code in ${resendCooldown}s` : 'Resend verification code' }}
                  </Button>
                </div>

                <Button
                  variant="link"
                  type="button"
                  class="w-full"
                  @click="showVerification = false; error = null"
                >
                  ← Back to registration
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import GoogleLoginButton from '../components/GoogleLoginButton.vue'
import Button from '../components/ui/Button.vue'
import Input from '../components/ui/Input.vue'
import Label from '../components/ui/Label.vue'
import Card from '../components/ui/Card.vue'
import CardHeader from '../components/ui/CardHeader.vue'
import CardTitle from '../components/ui/CardTitle.vue'
import CardContent from '../components/ui/CardContent.vue'
import Tabs from '../components/ui/Tabs.vue'
import TabsList from '../components/ui/TabsList.vue'
import TabsTrigger from '../components/ui/TabsTrigger.vue'
import TabsContent from '../components/ui/TabsContent.vue'
import Alert from '../components/ui/Alert.vue'
import AlertDescription from '../components/ui/AlertDescription.vue'
import Checkbox from '../components/ui/Checkbox.vue'

export default {
  name: 'LoginView',
  components: {
    GoogleLoginButton,
    Button,
    Input,
    Label,
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    Tabs,
    TabsList,
    TabsTrigger,
    TabsContent,
    Alert,
    AlertDescription,
    Checkbox
  },
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
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  background: var(--bg-tertiary);
  border-radius: 0.75rem;
  padding: 0.25rem;
  margin-bottom: 2rem;
}

.tab {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-weight: 500;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.tab.active {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  box-shadow: 0 4px 15px rgba(119, 51, 255, 0.3);
}

:root[data-theme="light"] .tab.active {
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25);
}

.auth-form {
  margin-bottom: 2rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
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
  background: var(--bg-primary);
  padding: 0 1rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.btn-oauth {
  width: 100%;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-light);
  border-radius: 0.5rem;
  color: var(--text-secondary);
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
  color: var(--accent-primary);
  font-size: 0.875rem;
  text-decoration: none;
  transition: all 0.2s;
}

.forgot-link:hover {
  color: var(--accent-secondary);
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
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.forgot-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.verification-text {
  color: var(--text-secondary);
  line-height: 1.6;
}

.forgot-text {
  color: var(--text-secondary);
  line-height: 1.6;
}

.verification-text strong {
  color: var(--accent-primary);
  font-weight: 600;
}

.forgot-text strong {
  color: var(--accent-primary);
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
  color: var(--accent-primary);
  cursor: pointer;
  padding: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-link:hover:not(:disabled) {
  color: var(--accent-secondary);
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

.oauth-divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.oauth-divider::before,
.oauth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.oauth-divider span {
  padding: 0 1rem;
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
