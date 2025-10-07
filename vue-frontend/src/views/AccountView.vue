<template>
  <div class="account-view">
    <div class="container-sm">
      <div class="account-card card">
        <h1 class="page-title">
          Account Settings
        </h1>

        <!-- Tabs -->
        <div class="tabs">
          <button :class="['tab', { active: activeTab === 'profile' }]" @click="activeTab = 'profile'">
            👤 Profile
          </button>
          <button v-if="!isGoogleOnlyUser" :class="['tab', { active: activeTab === 'security' }]"
            @click="activeTab = 'security'">
            🔒 Security
          </button>
          <button :class="['tab', { active: activeTab === 'danger' }]" @click="activeTab = 'danger'">
            ⚠️ Danger Zone
          </button>
        </div>

        <!-- Profile Tab -->
        <div v-if="activeTab === 'profile'" class="tab-content">
          <h2 class="section-title">
            Profile Information
          </h2>

          <!-- Google Profile Picture -->
          <div v-if="authStore.user?.picture" class="profile-picture-section">
            <img :src="authStore.user.picture" alt="Profile" class="profile-picture">
            <p v-if="isGoogleUser" class="google-badge">
              🔗 Linked with Google
            </p>
          </div>

          <form class="form" @submit.prevent="updateProfile">
            <div class="form-group">
              <label class="form-label">Username</label>
              <input v-model="profileForm.username" type="text" class="form-input" disabled>
              <p class="form-hint">
                Username cannot be changed
              </p>
            </div>

            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input v-model="profileForm.name" type="text" class="form-input" required>
            </div>

            <div class="form-group">
              <label class="form-label">Email</label>
              <input v-model="profileForm.email" type="email" class="form-input" :disabled="isGoogleUser" required>
              <p v-if="isGoogleUser" class="form-hint">
                Email cannot be changed for Google accounts
              </p>
            </div>

            <div v-if="profileError" class="alert alert-error">
              {{ profileError }}
            </div>

            <div v-if="profileSuccess" class="alert alert-success">
              {{ profileSuccess }}
            </div>

            <button type="submit" :disabled="profileLoading" class="btn btn-primary">
              {{ profileLoading ? 'Saving...' : 'Save Changes' }}
            </button>
          </form>
        </div>

        <!-- Security Tab -->
        <div v-if="activeTab === 'security'" class="tab-content">
          <h2 class="section-title">
            Change Password
          </h2>
          <form class="form" @submit.prevent="changePassword">
            <div class="form-group">
              <label class="form-label">Current Password</label>
              <input v-model="securityForm.currentPassword" type="password" class="form-input" required>
            </div>

            <div class="form-group">
              <label class="form-label">New Password</label>
              <input v-model="securityForm.newPassword" type="password" class="form-input" required minlength="6">
            </div>

            <div class="form-group">
              <label class="form-label">Confirm New Password</label>
              <input v-model="securityForm.confirmPassword" type="password" class="form-input" required minlength="6">
            </div>

            <div v-if="securityError" class="alert alert-error">
              {{ securityError }}
            </div>

            <div v-if="securitySuccess" class="alert alert-success">
              {{ securitySuccess }}
            </div>

            <button type="submit" :disabled="securityLoading" class="btn btn-primary">
              {{ securityLoading ? 'Changing...' : 'Change Password' }}
            </button>
          </form>
        </div>

        <!-- Danger Zone Tab -->
        <div v-if="activeTab === 'danger'" class="tab-content">
          <h2 class="section-title">
            Danger Zone
          </h2>
          <div class="danger-zone">
            <!-- Unlink Google Account (for Google users with password) -->
            <div v-if="isGoogleUser && hasPassword" class="danger-section">
              <div class="danger-warning">
                <h3>🔗 Unlink Google Account</h3>
                <p>
                  Remove the connection to your Google account. You'll still be able to log in
                  with your username and password.
                </p>
              </div>
              <button :disabled="unlinkLoading" class="btn btn-warning" @click="unlinkGoogle">
                {{ unlinkLoading ? 'Unlinking...' : 'Unlink Google Account' }}
              </button>
              <div v-if="unlinkError" class="alert alert-error">
                {{ unlinkError }}
              </div>
              <div v-if="unlinkSuccess" class="alert alert-success">
                {{ unlinkSuccess }}
              </div>
            </div>

            <!-- Link Google Account (for traditional users) -->
            <div v-if="!isGoogleUser" class="danger-section">
              <div class="danger-warning">
                <h3>🔗 Link Google Account</h3>
                <p>
                  Connect your Google account for quick sign-in. You'll be able to log in
                  with either your username/password or Google.
                </p>
              </div>
              <button :disabled="linkLoading" class="btn btn-primary" @click="linkGoogle">
                {{ linkLoading ? 'Linking...' : 'Link Google Account' }}
              </button>
            </div>

            <!-- Delete Account -->
            <div class="danger-section">
              <div class="danger-warning">
                <h3>⚠️ Delete Account</h3>
                <p>
                  Once you delete your account, there is no going back. This will permanently
                  delete your account, all your courses, and progress. This action cannot be undone.
                </p>
              </div>

              <div v-if="!showDeleteConfirm">
                <button class="btn btn-danger" @click="showDeleteConfirm = true">
                  Delete My Account
                </button>
              </div>

              <div v-else class="delete-confirm">
                <p class="confirm-text">
                  Are you absolutely sure? Type your username
                  <strong>{{ authStore.user?.username }}</strong> to confirm:
                </p>
                <input v-model="deleteConfirmText" type="text" class="form-input"
                  placeholder="Type your username to confirm">

                <div v-if="deleteError" class="alert alert-error">
                  {{ deleteError }}
                </div>

                <div class="button-group">
                  <button :disabled="deleteConfirmText !== authStore.user?.username || deleteLoading"
                    class="btn btn-danger" @click="deleteAccount">
                    {{ deleteLoading ? 'Deleting...' : 'Yes, Delete My Account' }}
                  </button>
                  <button class="btn btn-secondary" :disabled="deleteLoading"
                    @click="showDeleteConfirm = false; deleteConfirmText = ''">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

export default {
  name: 'AccountView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()

    const activeTab = ref('profile')

    // Profile form
    const profileForm = ref({
      username: '',
      name: '',
      email: ''
    })
    const profileLoading = ref(false)
    const profileError = ref(null)
    const profileSuccess = ref(null)

    // Security form
    const securityForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    const securityLoading = ref(false)
    const securityError = ref(null)
    const securitySuccess = ref(null)

    // Delete account
    const showDeleteConfirm = ref(false)
    const deleteConfirmText = ref('')
    const deleteLoading = ref(false)
    const deleteError = ref(null)

    // Google account management
    const unlinkLoading = ref(false)
    const unlinkError = ref(null)
    const unlinkSuccess = ref(null)
    const linkLoading = ref(false)

    // Computed properties
    const isGoogleUser = computed(() => authStore.user?.isGoogleUser || false)
    const hasPassword = computed(() => authStore.user?.hasPassword !== false)
    const isGoogleOnlyUser = computed(() => isGoogleUser.value && !hasPassword.value)

    // Load user data
    onMounted(() => {
      if (!authStore.user) {
        router.push('/login')
        return
      }

      // support deep-linking to a specific tab via ?tab=danger
      const qtab = route.query.tab
      if (qtab && typeof qtab === 'string') {
        activeTab.value = qtab
      }

      profileForm.value = {
        username: authStore.user.username,
        name: authStore.user.name || '',
        email: authStore.user.email || ''
      }
    })

    const updateProfile = async () => {
      profileLoading.value = true
      profileError.value = null
      profileSuccess.value = null

      try {
        const response = await api.put('/account/profile', {
          username: authStore.user.username,
          name: profileForm.value.name,
          email: profileForm.value.email
        })

        if (response.data.success) {
          profileSuccess.value = 'Profile updated successfully!'

          // Update auth store with new data
          authStore.user.name = profileForm.value.name
          authStore.user.email = profileForm.value.email

          // Update localStorage
          const userData = JSON.stringify(authStore.user)
          localStorage.setItem('userData', userData)

          setTimeout(() => {
            profileSuccess.value = null
          }, 3000)
        }
      } catch (error) {
        profileError.value = error.response?.data?.detail || 'Failed to update profile'
      } finally {
        profileLoading.value = false
      }
    }

    const changePassword = async () => {
      securityError.value = null
      securitySuccess.value = null

      // Validate passwords match
      if (securityForm.value.newPassword !== securityForm.value.confirmPassword) {
        securityError.value = 'New passwords do not match'
        return
      }

      securityLoading.value = true

      try {
        const response = await api.put('/account/password', {
          username: authStore.user.username,
          current_password: securityForm.value.currentPassword,
          new_password: securityForm.value.newPassword
        })

        if (response.data.success) {
          securitySuccess.value = 'Password changed successfully!'

          // Clear form
          securityForm.value = {
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
          }

          setTimeout(() => {
            securitySuccess.value = null
          }, 3000)
        }
      } catch (error) {
        securityError.value = error.response?.data?.detail || 'Failed to change password'
      } finally {
        securityLoading.value = false
      }
    }

    const deleteAccount = async () => {
      deleteError.value = null
      deleteLoading.value = true

      try {
        const response = await api.delete('/account', {
          data: { username: authStore.user.username }
        })

        if (response.data.success) {
          // Logout and redirect to home
          authStore.logout()
          router.push('/')
        }
      } catch (error) {
        deleteError.value = error.response?.data?.detail || 'Failed to delete account'
      } finally {
        deleteLoading.value = false
      }
    }

    const unlinkGoogle = async () => {
      unlinkLoading.value = true
      unlinkError.value = null
      unlinkSuccess.value = null

      try {
        const response = await api.post('/account/unlink-google', {
          username: authStore.user.username
        })

        if (response.data.success) {
          unlinkSuccess.value = 'Google account unlinked successfully!'

          // Update auth store
          authStore.user.isGoogleUser = false
          authStore.user.picture = null

          // Update localStorage
          const userData = JSON.stringify(authStore.user)
          localStorage.setItem('userData', userData)
          if (sessionStorage.getItem('userData')) {
            sessionStorage.setItem('userData', userData)
          }

          setTimeout(() => {
            unlinkSuccess.value = null
          }, 3000)
        }
      } catch (error) {
        unlinkError.value = error.response?.data?.detail || 'Failed to unlink Google account'
      } finally {
        unlinkLoading.value = false
      }
    }

    const linkGoogle = async () => {
      linkLoading.value = true

      try {
        // Generate state for CSRF protection
        const state = generateRandomState()
        localStorage.setItem('oauth_state', state)
        localStorage.setItem('oauth_link_mode', 'true')

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
      } catch (error) {
        console.error('Google link error:', error)
        linkLoading.value = false
      }
    }

    const generateRandomState = () => {
      const array = new Uint8Array(32)
      crypto.getRandomValues(array)
      return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
    }

    return {
      activeTab,
      authStore,
      profileForm,
      profileLoading,
      profileError,
      profileSuccess,
      updateProfile,
      securityForm,
      securityLoading,
      securityError,
      securitySuccess,
      changePassword,
      showDeleteConfirm,
      deleteConfirmText,
      deleteLoading,
      deleteError,
      deleteAccount,
      isGoogleUser,
      hasPassword,
      isGoogleOnlyUser,
      unlinkLoading,
      unlinkError,
      unlinkSuccess,
      unlinkGoogle,
      linkLoading,
      linkGoogle
    }
  }
}
</script>

<style scoped>
.account-view {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  padding: 2rem 0;
}

.account-card {
  max-width: 700px;
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

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.form {
  max-width: 500px;
}

.form-hint {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.danger-zone {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.danger-section {
  background: rgba(239, 68, 68, 0.05);
  border: 2px solid rgba(239, 68, 68, 0.2);
  border-radius: 0.75rem;
  padding: 2rem;
}

.danger-warning {
  margin-bottom: 1.5rem;
}

.danger-warning h3 {
  color: #f87171;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.danger-warning p {
  color: #cbd5e0;
  line-height: 1.6;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.delete-confirm {
  margin-top: 1.5rem;
}

.confirm-text {
  color: #cbd5e0;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.confirm-text strong {
  color: #f87171;
  font-weight: 600;
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .tabs {
    flex-direction: column;
  }

  .button-group {
    flex-direction: column;
  }

  .button-group .btn {
    width: 100%;
  }
}

.profile-picture-section {
  text-align: center;
  margin-bottom: 2rem;
}

.profile-picture {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 3px solid var(--accent-primary);
  margin-bottom: 0.5rem;
}

.google-badge {
  color: var(--accent-primary);
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
}
</style>
