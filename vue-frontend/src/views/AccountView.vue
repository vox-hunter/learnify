<template>
  <div class="account-view">
    <div class="container-sm">
      <div class="account-card card">
        <h1 class="page-title">Account Settings</h1>
        
        <!-- Tabs -->
        <div class="tabs">
          <button 
            :class="['tab', { active: activeTab === 'profile' }]"
            @click="activeTab = 'profile'"
          >
            👤 Profile
          </button>
          <button 
            :class="['tab', { active: activeTab === 'security' }]"
            @click="activeTab = 'security'"
          >
            🔒 Security
          </button>
          <button 
            :class="['tab', { active: activeTab === 'danger' }]"
            @click="activeTab = 'danger'"
          >
            ⚠️ Danger Zone
          </button>
        </div>

        <!-- Profile Tab -->
        <div v-if="activeTab === 'profile'" class="tab-content">
          <h2 class="section-title">Profile Information</h2>
          <form @submit.prevent="updateProfile" class="form">
            <div class="form-group">
              <label class="form-label">Username</label>
              <input
                v-model="profileForm.username"
                type="text"
                class="form-input"
                disabled
              />
              <p class="form-hint">Username cannot be changed</p>
            </div>

            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input
                v-model="profileForm.name"
                type="text"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">Email</label>
              <input
                v-model="profileForm.email"
                type="email"
                class="form-input"
                required
              />
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
          <h2 class="section-title">Change Password</h2>
          <form @submit.prevent="changePassword" class="form">
            <div class="form-group">
              <label class="form-label">Current Password</label>
              <input
                v-model="securityForm.currentPassword"
                type="password"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">New Password</label>
              <input
                v-model="securityForm.newPassword"
                type="password"
                class="form-input"
                required
                minlength="6"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Confirm New Password</label>
              <input
                v-model="securityForm.confirmPassword"
                type="password"
                class="form-input"
                required
                minlength="6"
              />
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
          <h2 class="section-title">Danger Zone</h2>
          <div class="danger-zone">
            <div class="danger-warning">
              <h3>⚠️ Delete Account</h3>
              <p>
                Once you delete your account, there is no going back. This will permanently 
                delete your account, all your courses, and progress. This action cannot be undone.
              </p>
            </div>

            <div v-if="!showDeleteConfirm">
              <button @click="showDeleteConfirm = true" class="btn btn-danger">
                Delete My Account
              </button>
            </div>

            <div v-else class="delete-confirm">
              <p class="confirm-text">
                Are you absolutely sure? Type your username 
                <strong>{{ authStore.user?.username }}</strong> to confirm:
              </p>
              <input
                v-model="deleteConfirmText"
                type="text"
                class="form-input"
                placeholder="Type your username to confirm"
              />

              <div v-if="deleteError" class="alert alert-error">
                {{ deleteError }}
              </div>

              <div class="button-group">
                <button 
                  @click="deleteAccount" 
                  :disabled="deleteConfirmText !== authStore.user?.username || deleteLoading"
                  class="btn btn-danger"
                >
                  {{ deleteLoading ? 'Deleting...' : 'Yes, Delete My Account' }}
                </button>
                <button 
                  @click="showDeleteConfirm = false; deleteConfirmText = ''" 
                  class="btn btn-secondary"
                  :disabled="deleteLoading"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

export default {
  name: 'AccountView',
  setup() {
    const router = useRouter()
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

    // Load user data
    onMounted(() => {
      if (!authStore.user) {
        router.push('/login')
        return
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
      deleteAccount
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
  color: #e2e8f0;
  margin-bottom: 1.5rem;
}

.form {
  max-width: 500px;
}

.form-hint {
  font-size: 0.875rem;
  color: #a0aec0;
  margin-top: 0.25rem;
}

.danger-zone {
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
</style>
