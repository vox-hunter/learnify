<template>
  <div class="account-view">
    <div class="container-sm">
      <div class="account-card card">
        <h1 class="page-title">
          Account Settings
        </h1>

        <!-- Tabs -->
        <div class="tabs">
          <button
            :class="['tab', { active: activeTab === 'profile' }]"
            @click="updateTabAndQuery('profile')"
          >
            👤 Profile
          </button>
          <button
            :class="['tab', { active: activeTab === 'learning' }]"
            @click="updateTabAndQuery('learning')"
          >
            📚 Learning Profile
          </button>
          <button
            v-if="!isGoogleOnlyUser"
            :class="['tab', { active: activeTab === 'security' }]"
            @click="updateTabAndQuery('security')"
          >
            🔒 Security
          </button>
          <button
            :class="['tab', { active: activeTab === 'danger' }]"
            @click="updateTabAndQuery('danger')"
          >
            ⚠️ Danger Zone
          </button>
        </div>

        <!-- Profile Tab -->
        <div
          v-if="activeTab === 'profile'"
          class="tab-content"
        >
          <h2 class="section-title">
            Profile Information
          </h2>

          <!-- Google Profile Picture -->
          <div
            v-if="authStore.user?.picture"
            class="profile-picture-section"
          >
            <img
              :src="authStore.user.picture"
              alt="Profile"
              class="profile-picture"
            >
            <p
              v-if="isGoogleUser"
              class="google-badge"
            >
              🔗 Linked with Google
            </p>
          </div>

          <form
            class="form"
            @submit.prevent="updateProfile"
          >
            <div class="form-group">
              <label class="form-label">Username</label>
              <div class="username-input-group">
                <input
                  v-model="profileForm.username"
                  type="text"
                  class="form-input"
                  :disabled="!editingUsername"
                >
                <button
                  v-if="!editingUsername"
                  type="button"
                  class="btn btn-secondary"
                  @click="enableUsernameEdit"
                >
                  Edit
                </button>
                <button
                  v-else
                  type="button"
                  class="btn btn-secondary"
                  @click="cancelUsernameEdit"
                >
                  Cancel
                </button>
              </div>
              <p
                v-if="!editingUsername"
                class="form-hint"
              >
                Click "Edit" to change your username
              </p>
              <p
                v-else
                class="form-hint"
              >
                Choose a username with at least 3 characters
              </p>
            </div>

            <div
              v-if="usernameCheckError"
              class="alert alert-error"
            >
              {{ usernameCheckError }}
            </div>

            <div
              v-if="editingUsername && usernameAvailable === true"
              class="alert alert-success"
            >
              ✓ This username is available
            </div>

            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input
                v-model="profileForm.name"
                type="text"
                class="form-input"
                required
              >
            </div>

            <div class="form-group">
              <label class="form-label">Email</label>
              <input
                v-model="profileForm.email"
                type="email"
                class="form-input"
                disabled
                required
              >
              <p
                class="form-hint"
              >
                Email cannot be changed. Contact support if you need assistance.
              </p>
            </div>

            <div
              v-if="profileError"
              class="alert alert-error"
            >
              {{ profileError }}
            </div>

            <div
              v-if="profileSuccess"
              class="alert alert-success"
            >
              {{ profileSuccess }}
            </div>

            <button
              v-if="!editingUsername"
              type="submit"
              :disabled="profileLoading"
              class="btn btn-primary"
            >
              {{ profileLoading ? 'Saving...' : 'Save Changes' }}
            </button>
            <button
              v-else
              type="button"
              :disabled="profileLoading || !usernameAvailable"
              class="btn btn-primary"
              @click="submitUsernameChange"
            >
              {{ profileLoading ? 'Changing...' : 'Save Username' }}
            </button>
          </form>
        </div>

        <!-- Learning Profile Tab -->
        <div
          v-if="activeTab === 'learning'"
          class="tab-content"
        >
          <h2 class="section-title">
            Learning Profile
          </h2>

          <!-- Loading State -->
          <div
            v-if="learningLoading && !learningProfileLoaded"
            class="loading-state"
          >
            <div class="spinner" />
            <p>Loading your learning profile...</p>
          </div>

          <!-- Error State -->
          <div
            v-else-if="learningError && !learningProfileLoaded"
            class="alert alert-error"
            style="margin-bottom: 1rem;"
          >
            <p style="margin-bottom: 0.75rem;">
              {{ learningError }}
            </p>
            <button
              type="button"
              class="btn btn-secondary"
              style="font-size: 0.875rem; padding: 0.5rem 1rem;"
              @click="fetchLearningProfile"
            >
              Retry
            </button>
          </div>

          <!-- No Profile Message -->
          <div
            v-else-if="!learningLoading && !hasLearningProfile && !learningError"
            class="info-message"
          >
            <p>You haven't completed your onboarding yet. Complete it to personalize your learning experience.</p>
            <button
              class="btn btn-primary"
              @click="$router.push('/onboarding')"
            >
              Complete Onboarding
            </button>
          </div>

          <!-- Learning Profile Form -->
          <form
            v-else
            class="form"
            @submit.prevent="updateLearningProfile"
          >
            <!-- Basic Information Section -->
            <div class="learning-section">
              <h3 class="section-subtitle">
                Basic Information
              </h3>

              <div class="form-group">
                <label class="form-label">Date of Birth</label>
                <input
                  v-model="learningForm.date_of_birth"
                  type="date"
                  class="form-input"
                >
                <p class="form-hint">
                  Must be a valid date, not in the future
                </p>
              </div>

              <div class="form-group">
                <label class="form-label">User Type</label>
                <input
                  :value="learningForm.user_type === 'student' ? 'Student' : 'Educator'"
                  type="text"
                  class="form-input"
                  disabled
                >
                <p class="form-hint">
                  Contact support to change your role
                </p>
              </div>

              <div class="form-group">
                <label class="form-label">Timezone</label>
                <select
                  v-model="learningForm.timezone"
                  class="form-select"
                >
                  <!-- Comment 12: Extended timezone options for better global coverage -->
                  <option value="UTC">
                    UTC
                  </option>
                  <option value="America/New_York">
                    America/New_York (EST/EDT)
                  </option>
                  <option value="America/Chicago">
                    America/Chicago (CST/CDT)
                  </option>
                  <option value="America/Denver">
                    America/Denver (MST/MDT)
                  </option>
                  <option value="America/Los_Angeles">
                    America/Los_Angeles (PST/PDT)
                  </option>
                  <option value="America/Toronto">
                    America/Toronto (EST/EDT)
                  </option>
                  <option value="America/Vancouver">
                    America/Vancouver (PST/PDT)
                  </option>
                  <option value="America/Mexico_City">
                    America/Mexico_City (CST/CDT)
                  </option>
                  <option value="America/Sao_Paulo">
                    America/Sao_Paulo (BRT)
                  </option>
                  <option value="America/Buenos_Aires">
                    America/Buenos_Aires (ART)
                  </option>
                  <option value="Europe/London">
                    Europe/London (GMT/BST)
                  </option>
                  <option value="Europe/Paris">
                    Europe/Paris (CET/CEST)
                  </option>
                  <option value="Europe/Berlin">
                    Europe/Berlin (CET/CEST)
                  </option>
                  <option value="Europe/Madrid">
                    Europe/Madrid (CET/CEST)
                  </option>
                  <option value="Europe/Rome">
                    Europe/Rome (CET/CEST)
                  </option>
                  <option value="Europe/Amsterdam">
                    Europe/Amsterdam (CET/CEST)
                  </option>
                  <option value="Europe/Brussels">
                    Europe/Brussels (CET/CEST)
                  </option>
                  <option value="Europe/Vienna">
                    Europe/Vienna (CET/CEST)
                  </option>
                  <option value="Europe/Warsaw">
                    Europe/Warsaw (CET/CEST)
                  </option>
                  <option value="Europe/Istanbul">
                    Europe/Istanbul (TRT)
                  </option>
                  <option value="Europe/Moscow">
                    Europe/Moscow (MSK)
                  </option>
                  <option value="Africa/Cairo">
                    Africa/Cairo (EET)
                  </option>
                  <option value="Africa/Johannesburg">
                    Africa/Johannesburg (SAST)
                  </option>
                  <option value="Africa/Nairobi">
                    Africa/Nairobi (EAT)
                  </option>
                  <option value="Africa/Lagos">
                    Africa/Lagos (WAT)
                  </option>
                  <option value="Asia/Dubai">
                    Asia/Dubai (GST)
                  </option>
                  <option value="Asia/Karachi">
                    Asia/Karachi (PKT)
                  </option>
                  <option value="Asia/Kolkata">
                    Asia/Kolkata (IST)
                  </option>
                  <option value="Asia/Bangkok">
                    Asia/Bangkok (ICT)
                  </option>
                  <option value="Asia/Singapore">
                    Asia/Singapore (SGT)
                  </option>
                  <option value="Asia/Hong_Kong">
                    Asia/Hong_Kong (HKT)
                  </option>
                  <option value="Asia/Shanghai">
                    Asia/Shanghai (CST)
                  </option>
                  <option value="Asia/Tokyo">
                    Asia/Tokyo (JST)
                  </option>
                  <option value="Asia/Seoul">
                    Asia/Seoul (KST)
                  </option>
                  <option value="Australia/Sydney">
                    Australia/Sydney (AEDT/AEST)
                  </option>
                  <option value="Australia/Melbourne">
                    Australia/Melbourne (AEDT/AEST)
                  </option>
                  <option value="Australia/Brisbane">
                    Australia/Brisbane (AEST)
                  </option>
                  <option value="Australia/Perth">
                    Australia/Perth (AWST)
                  </option>
                  <option value="Pacific/Auckland">
                    Pacific/Auckland (NZDT/NZST)
                  </option>
                  <option value="Pacific/Fiji">
                    Pacific/Fiji (FJT)
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Language Preference</label>
                <select
                  v-model="learningForm.language_preference"
                  class="form-select"
                >
                  <!-- Comment 12: Added ar (Arabic) and ru (Russian) -->
                  <option value="en">
                    English
                  </option>
                  <option value="es">
                    Spanish
                  </option>
                  <option value="fr">
                    French
                  </option>
                  <option value="de">
                    German
                  </option>
                  <option value="it">
                    Italian
                  </option>
                  <option value="pt">
                    Portuguese
                  </option>
                  <option value="ar">
                    Arabic
                  </option>
                  <option value="ru">
                    Russian
                  </option>
                  <option value="zh">
                    Chinese
                  </option>
                  <option value="ja">
                    Japanese
                  </option>
                  <option value="ko">
                    Korean
                  </option>
                </select>
              </div>
            </div>

            <!-- Student Profile Section -->
            <div
              v-if="learningForm.user_type === 'student'"
              class="learning-section"
            >
              <h3 class="section-subtitle">
                Student Information
              </h3>

              <div class="form-group">
                <label class="form-label">Year Level</label>
                <select
                  v-model="learningForm.student_profile.year_level"
                  class="form-select"
                >
                  <option value="">
                    Select a year level
                  </option>
                  <optgroup label="Secondary">
                    <option value="Year 7">
                      Year 7
                    </option>
                    <option value="Year 8">
                      Year 8
                    </option>
                    <option value="Year 9">
                      Year 9
                    </option>
                    <option value="Year 10">
                      Year 10
                    </option>
                    <option value="Year 11">
                      Year 11
                    </option>
                    <option value="Year 12">
                      Year 12
                    </option>
                    <option value="Year 13">
                      Year 13
                    </option>
                  </optgroup>
                  <optgroup label="College">
                    <option value="College Year 1">
                      College Year 1
                    </option>
                    <option value="College Year 2">
                      College Year 2
                    </option>
                    <option value="College Year 3">
                      College Year 3
                    </option>
                    <option value="College Year 4">
                      College Year 4
                    </option>
                  </optgroup>
                  <optgroup label="University">
                    <option value="University Year 1">
                      University Year 1
                    </option>
                    <option value="University Year 2">
                      University Year 2
                    </option>
                    <option value="University Year 3">
                      University Year 3
                    </option>
                    <option value="University Year 4">
                      University Year 4
                    </option>
                  </optgroup>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Study Stage</label>
                <select
                  v-model="learningForm.student_profile.study_stage"
                  class="form-select"
                >
                  <option value="">
                    Select study stage
                  </option>
                  <option value="KS3">
                    KS3
                  </option>
                  <option value="IGCSE">
                    IGCSE
                  </option>
                  <option value="A-Level">
                    A-Level
                  </option>
                  <option value="IB">
                    IB
                  </option>
                  <option value="AP">
                    AP
                  </option>
                  <option value="College">
                    College
                  </option>
                  <option value="University">
                    University
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Exam Board</label>
                <input
                  v-model="learningForm.student_profile.exam_board"
                  type="text"
                  class="form-input"
                  placeholder="e.g., Edexcel, AQA, OCR"
                >
              </div>

              <div class="form-group">
                <label class="form-label">Subjects</label>
                <div class="chip-container">
                  <div
                    v-for="(subject, index) in learningForm.student_profile.subjects"
                    :key="index"
                    class="chip"
                  >
                    {{ subject }}
                    <button
                      type="button"
                      class="chip-remove"
                      @click="removeFromArray('student_profile.subjects', index)"
                    >
                      ×
                    </button>
                  </div>
                </div>
                <div class="add-item-group">
                  <input
                    v-model="newSubject"
                    type="text"
                    class="form-input"
                    placeholder="Add a subject"
                    @keyup.enter="addToArray('student_profile.subjects', 'newSubject')"
                  >
                  <button
                    type="button"
                    class="btn btn-secondary"
                    @click="addToArray('student_profile.subjects', 'newSubject')"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Learning Goals</label>
                <div class="multi-select-group">
                  <label
                    v-for="goal in learningGoalOptions"
                    :key="goal"
                    class="checkbox-label"
                  >
                    <input
                      v-model="learningForm.student_profile.learning_goals"
                      type="checkbox"
                      :value="goal"
                    >
                    {{ goal }}
                  </label>
                </div>
              </div>

              <!-- Conditional fields for College/University -->
              <div
                v-if="learningForm.student_profile.study_stage === 'College' || learningForm.student_profile.study_stage === 'University'"
              >
                <div class="form-group">
                  <label class="form-label">Course Name</label>
                  <input
                    v-model="learningForm.student_profile.course_name"
                    type="text"
                    class="form-input"
                    placeholder="e.g., Computer Science"
                  >
                  <p class="form-hint">
                    Required for College/University students
                  </p>
                </div>

                <div class="form-group">
                  <label class="form-label">Institution Name</label>
                  <input
                    v-model="learningForm.student_profile.institution_name"
                    type="text"
                    class="form-input"
                    placeholder="e.g., University of Oxford"
                  >
                  <p class="form-hint">
                    Required for College/University students
                  </p>
                </div>
              </div>
            </div>

            <!-- Educator Profile Section -->
            <div
              v-if="learningForm.user_type === 'educator'"
              class="learning-section"
            >
              <h3 class="section-subtitle">
                Educator Information
              </h3>

              <div class="form-group">
                <label class="form-label">Subjects Taught</label>
                <div class="chip-container">
                  <div
                    v-for="(subject, index) in learningForm.educator_profile.subjects_taught"
                    :key="index"
                    class="chip"
                  >
                    {{ subject }}
                    <button
                      type="button"
                      class="chip-remove"
                      @click="removeFromArray('educator_profile.subjects_taught', index)"
                    >
                      ×
                    </button>
                  </div>
                </div>
                <!-- Comment 16: AI suggestions for subjects taught -->
                <div
                  class="add-item-group"
                  style="position: relative;"
                >
                  <input
                    v-model="newSubjectTaught"
                    type="text"
                    class="form-input"
                    placeholder="Add a subject (type to see suggestions)"
                    @input="handleSubjectTaughtInput"
                    @keyup.enter="addToArray('educator_profile.subjects_taught', 'newSubjectTaught')"
                  >
                  <button
                    type="button"
                    class="btn btn-secondary"
                    @click="addToArray('educator_profile.subjects_taught', 'newSubjectTaught')"
                  >
                    Add
                  </button>
                  <div
                    v-if="showSubjectDropdown"
                    class="suggestions-dropdown"
                  >
                    <div
                      v-for="(suggestion, idx) in subjectSuggestions"
                      :key="idx"
                      class="suggestion-item"
                      @click="selectSubjectSuggestion(suggestion)"
                    >
                      {{ suggestion }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Stages Covered</label>
                <div class="multi-select-group">
                  <label
                    v-for="stage in stageOptions"
                    :key="stage"
                    class="checkbox-label"
                  >
                    <input
                      v-model="learningForm.educator_profile.stages_covered"
                      type="checkbox"
                      :value="stage"
                    >
                    {{ stage }}
                  </label>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Exam Boards Covered</label>
                <div class="chip-container">
                  <div
                    v-for="(board, index) in learningForm.educator_profile.exam_boards_covered"
                    :key="index"
                    class="chip"
                  >
                    {{ board }}
                    <button
                      type="button"
                      class="chip-remove"
                      @click="removeFromArray('educator_profile.exam_boards_covered', index)"
                    >
                      ×
                    </button>
                  </div>
                </div>
                <!-- Comment 16: AI suggestions for exam boards -->
                <div
                  class="add-item-group"
                  style="position: relative;"
                >
                  <input
                    v-model="newExamBoard"
                    type="text"
                    class="form-input"
                    placeholder="Add an exam board (type to see suggestions)"
                    @input="handleExamBoardInput"
                    @keyup.enter="addToArray('educator_profile.exam_boards_covered', 'newExamBoard')"
                  >
                  <button
                    type="button"
                    class="btn btn-secondary"
                    @click="addToArray('educator_profile.exam_boards_covered', 'newExamBoard')"
                  >
                    Add
                  </button>
                  <div
                    v-if="showExamBoardDropdown"
                    class="suggestions-dropdown"
                  >
                    <div
                      v-for="(suggestion, idx) in examBoardSuggestions"
                      :key="idx"
                      class="suggestion-item"
                      @click="selectExamBoardSuggestion(suggestion)"
                    >
                      {{ typeof suggestion === 'string' ? suggestion : suggestion.name }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Use Cases</label>
                <div class="multi-select-group">
                  <label
                    v-for="useCase in useCaseOptions"
                    :key="useCase"
                    class="checkbox-label"
                  >
                    <input
                      v-model="learningForm.educator_profile.use_cases"
                      type="checkbox"
                      :value="useCase"
                    >
                    {{ useCase }}
                  </label>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Institution Name (Optional)</label>
                <input
                  v-model="learningForm.educator_profile.institution_name"
                  type="text"
                  class="form-input"
                  placeholder="e.g., Springfield High School"
                >
              </div>

              <div class="form-group">
                <label class="form-label">Class Size (Optional)</label>
                <input
                  v-model.number="learningForm.educator_profile.class_size"
                  type="number"
                  class="form-input"
                  placeholder="Average class size"
                  min="1"
                >
              </div>
            </div>

            <!-- Optional Fields Section -->
            <div class="learning-section">
              <h3 class="section-subtitle">
                Additional Information (Optional)
              </h3>

              <div class="form-group">
                <label class="form-label">User Intent</label>
                <input
                  v-model="learningForm.user_intent"
                  type="text"
                  class="form-input"
                  placeholder="What brings you to Learnify?"
                >
              </div>

              <div class="form-group">
                <label class="form-label">Tech Comfort Level</label>
                <select
                  v-model="learningForm.tech_comfort_level"
                  class="form-select"
                >
                  <option value="">
                    Select level
                  </option>
                  <option value="Novice">
                    Novice
                  </option>
                  <option value="Intermediate">
                    Intermediate
                  </option>
                  <option value="Advanced">
                    Advanced
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">AI Familiarity</label>
                <select
                  v-model="learningForm.ai_familiarity"
                  class="form-select"
                >
                  <option value="">
                    Select level
                  </option>
                  <option value="Beginner">
                    Beginner
                  </option>
                  <option value="Intermediate">
                    Intermediate
                  </option>
                  <option value="Expert">
                    Expert
                  </option>
                </select>
              </div>
            </div>

            <!-- Error and Success Messages -->
            <div
              v-if="learningError"
              class="alert alert-error"
            >
              {{ learningError }}
            </div>

            <div
              v-if="learningSuccess"
              class="alert alert-success"
            >
              {{ learningSuccess }}
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="learningLoading"
              class="btn btn-primary"
            >
              {{ learningLoading ? 'Saving...' : 'Save Learning Profile' }}
            </button>
          </form>
        </div>

        <!-- Security Tab -->
        <div
          v-if="activeTab === 'security'"
          class="tab-content"
        >
          <h2 class="section-title">
            Change Password
          </h2>
          <form
            class="form"
            @submit.prevent="changePassword"
          >
            <div class="form-group">
              <label class="form-label">Current Password</label>
              <input
                v-model="securityForm.currentPassword"
                type="password"
                class="form-input"
                required
              >
            </div>

            <div class="form-group">
              <label class="form-label">New Password</label>
              <input
                v-model="securityForm.newPassword"
                type="password"
                class="form-input"
                required
                minlength="6"
              >
            </div>

            <div class="form-group">
              <label class="form-label">Confirm New Password</label>
              <input
                v-model="securityForm.confirmPassword"
                type="password"
                class="form-input"
                required
                minlength="6"
              >
            </div>

            <div
              v-if="securityError"
              class="alert alert-error"
            >
              {{ securityError }}
            </div>

            <div
              v-if="securitySuccess"
              class="alert alert-success"
            >
              {{ securitySuccess }}
            </div>

            <button
              type="submit"
              :disabled="securityLoading"
              class="btn btn-primary"
            >
              {{ securityLoading ? 'Changing...' : 'Change Password' }}
            </button>
          </form>
        </div>

        <!-- Danger Zone Tab -->
        <div
          v-if="activeTab === 'danger'"
          class="tab-content"
        >
          <h2 class="section-title">
            Danger Zone
          </h2>
          <div class="danger-zone">
            <!-- Google Account Link/Unlink Button -->
            <div class="danger-section">
              <div class="danger-warning">
                <h3 v-if="isGoogleUser">
                  🔗 Unlink Google Account
                </h3>
                <h3 v-else>
                  🔗 Link Google Account
                </h3>
                <p v-if="isGoogleUser">
                  Remove the connection to your Google account. You'll still be able to log in
                  with your username and password.
                </p>
                <p v-else>
                  Connect your Google account for quick sign-in. You'll be able to log in
                  with either your username/password or Google.
                </p>
              </div>
              <button
                v-if="isGoogleUser"
                :disabled="unlinkLoading"
                class="btn btn-warning"
                @click="unlinkGoogle"
              >
                {{ unlinkLoading ? 'Unlinking...' : 'Unlink Google Account' }}
              </button>
              <button
                v-else
                :disabled="linkLoading"
                class="btn btn-primary"
                @click="linkGoogle"
              >
                {{ linkLoading ? 'Linking...' : 'Link Google Account' }}
              </button>
              <div
                v-if="unlinkError && isGoogleUser"
                class="alert alert-error"
              >
                {{ unlinkError }}
              </div>
              <div
                v-if="unlinkSuccess && isGoogleUser"
                class="alert alert-success"
              >
                {{ unlinkSuccess }}
              </div>
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
                <button
                  class="btn btn-danger"
                  @click="showDeleteConfirm = true"
                >
                  Delete My Account
                </button>
              </div>

              <div
                v-else
                class="delete-confirm"
              >
                <p class="confirm-text">
                  Are you absolutely sure? Type your username
                  <strong>{{ authStore.user?.username }}</strong> to confirm:
                </p>
                <input
                  v-model="deleteConfirmText"
                  type="text"
                  class="form-input"
                  placeholder="Type your username to confirm"
                >

                <div
                  v-if="deleteError"
                  class="alert alert-error"
                >
                  {{ deleteError }}
                </div>

                <div class="button-group">
                  <button
                    :disabled="deleteConfirmText !== authStore.user?.username || deleteLoading"
                    class="btn btn-danger"
                    @click="deleteAccount"
                  >
                    {{ deleteLoading ? 'Deleting...' : 'Yes, Delete My Account' }}
                  </button>
                  <button
                    class="btn btn-secondary"
                    :disabled="deleteLoading"
                    @click="showDeleteConfirm = false; deleteConfirmText = ''"
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
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
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
    const editingUsername = ref(false)
    const originalUsername = ref('')
    const usernameAvailable = ref(null)
    const usernameCheckError = ref(null)

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

    // Learning profile form
    const learningForm = ref({
      date_of_birth: '',
      user_type: '',
      timezone: 'UTC',
      language_preference: 'en',
      student_profile: {
        year_level: '',
        study_stage: '',
        course_name: '',
        institution_name: '',
        exam_board: '',
        subjects: [],
        learning_goals: [],
        learning_style: ''
      },
      educator_profile: {
        subjects_taught: [],
        stages_covered: [],
        exam_boards_covered: [],
        use_cases: [],
        institution_name: '',
        class_size: null
      },
      user_intent: '',
      tech_comfort_level: '',
      ai_familiarity: ''
    })
    const learningLoading = ref(false)
    const learningError = ref(null)
    const learningSuccess = ref(null)
    const learningProfileLoaded = ref(false)
    const hasLearningProfile = ref(false)

    // Temp variables for adding items to arrays
    const newSubject = ref('')
    const newSubjectTaught = ref('')
    const newExamBoard = ref('')

    // Comment 16: AI suggestions state
    const aiSuggestionsCache = ref({})
    const subjectSuggestions = ref([])
    const examBoardSuggestions = ref([])
    const showSubjectDropdown = ref(false)
    const showExamBoardDropdown = ref(false)

    // Options for checkboxes
    const learningGoalOptions = ['Revision', 'Improving grades', 'Understanding concepts', 'Exam preparation', 'Homework help']
    const stageOptions = ['KS3', 'IGCSE', 'A-Level', 'IB', 'AP', 'College', 'University']
    const useCaseOptions = ['Lesson creation', 'Student analytics', 'Resource generation', 'Assessment creation', 'Homework assignments']

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

    // Watch for active tab changes to lazy-load learning profile
    watch(activeTab, (newTab) => {
      if (newTab === 'learning' && !learningProfileLoaded.value) {
        fetchLearningProfile()
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

    const enableUsernameEdit = () => {
      editingUsername.value = true
      originalUsername.value = profileForm.value.username
      usernameCheckError.value = null
    }

    const cancelUsernameEdit = () => {
      editingUsername.value = false
      profileForm.value.username = originalUsername.value
      usernameCheckError.value = null
      usernameAvailable.value = null
    }

    const checkUsernameAvailability = async () => {
      if (profileForm.value.username === authStore.user.username) {
        usernameCheckError.value = 'New username must be different from current username'
        usernameAvailable.value = false
        return
      }

      if (profileForm.value.username.length < 3) {
        usernameCheckError.value = 'Username must be at least 3 characters'
        usernameAvailable.value = false
        return
      }

      try {
        const response = await api.get(`/auth/check-username?username=${profileForm.value.username}`)
        if (response.data.available) {
          usernameAvailable.value = true
          usernameCheckError.value = null
        } else {
          usernameAvailable.value = false
          usernameCheckError.value = 'This username is already taken'
        }
      } catch (e) {
        usernameCheckError.value = 'Error checking username availability'
        usernameAvailable.value = false
      }
    }

    const submitUsernameChange = async () => {
      if (profileForm.value.username === authStore.user.username) {
        profileError.value = 'New username must be different'
        return
      }

      if (!usernameAvailable.value) {
        await checkUsernameAvailability()
        if (!usernameAvailable.value) return
      }

      profileLoading.value = true
      profileError.value = null
      profileSuccess.value = null

      try {
        const response = await api.put('/account/username', {
          old_username: authStore.user.username,
          new_username: profileForm.value.username
        })

        if (response.data.success) {
          profileSuccess.value = 'Username changed successfully!'

          // Update auth store with new username
          authStore.user.username = response.data.new_username

          // Update localStorage
          const userData = JSON.stringify(authStore.user)
          localStorage.setItem('userData', userData)
          if (sessionStorage.getItem('userData')) {
            sessionStorage.setItem('userData', userData)
          }

          // Update original username tracking
          originalUsername.value = response.data.new_username
          editingUsername.value = false
          usernameAvailable.value = null
          usernameCheckError.value = null

          setTimeout(() => {
            profileSuccess.value = null
          }, 3000)
        }
      } catch (error) {
        profileError.value = error.response?.data?.detail || 'Failed to change username'
      } finally {
        profileLoading.value = false
      }
    }

    // Watch for username changes to check availability
    watch(() => profileForm.value.username, () => {
      if (editingUsername.value) {
        checkUsernameAvailability()
      }
    })

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

    const updateTabAndQuery = (tabName) => {
      activeTab.value = tabName
      router.replace({ query: { ...route.query, tab: tabName } })
    }

    // Comment 16: Fetch AI suggestions for educators
    const fetchAISuggestions = async (type, context) => {
      const sortedContext = Object.fromEntries(Object.entries(context).sort())
      const cacheKey = type + JSON.stringify(sortedContext)
      if (aiSuggestionsCache.value[cacheKey]) {
        return aiSuggestionsCache.value[cacheKey]
      }

      try {
        const response = await api.post('/onboarding/ai-suggestions', {
          suggestion_type: type,
          context,
          max_suggestions: 10
        })

        const suggestions = response.data.suggestions || []
        aiSuggestionsCache.value[cacheKey] = suggestions
        return suggestions
      } catch (err) {
        console.error('Error fetching AI suggestions:', err)
        return []
      }
    }

    const handleSubjectTaughtInput = async () => {
      if (newSubjectTaught.value.length < 2) {
        showSubjectDropdown.value = false
        return
      }

      const suggestions = await fetchAISuggestions('subjects', { user_type: 'educator' })
      subjectSuggestions.value = suggestions.filter(s => 
        s.toLowerCase().includes(newSubjectTaught.value.toLowerCase())
      ).slice(0, 5)
      showSubjectDropdown.value = subjectSuggestions.value.length > 0
    }

    const handleExamBoardInput = async () => {
      if (newExamBoard.value.length < 2) {
        showExamBoardDropdown.value = false
        return
      }

      const suggestions = await fetchAISuggestions('exam_boards', { default: true })
      examBoardSuggestions.value = suggestions.filter(s => {
        const name = typeof s === 'string' ? s : s.name || ''
        return name.toLowerCase().includes(newExamBoard.value.toLowerCase())
      }).slice(0, 5)
      showExamBoardDropdown.value = examBoardSuggestions.value.length > 0
    }

    const selectSubjectSuggestion = (suggestion) => {
      newSubjectTaught.value = suggestion
      showSubjectDropdown.value = false
      addToArray('educator_profile.subjects_taught', 'newSubjectTaught')
    }

    const selectExamBoardSuggestion = (suggestion) => {
      const board = typeof suggestion === 'string' ? suggestion : suggestion.name || ''
      newExamBoard.value = board
      showExamBoardDropdown.value = false
      addToArray('educator_profile.exam_boards_covered', 'newExamBoard')
    }

    const cleanPayload = (obj) => {
      if (obj === null || obj === undefined) return undefined
      
      if (Array.isArray(obj)) {
        const cleaned = obj.filter(item => item !== null && item !== undefined && item !== '')
        return cleaned.length > 0 ? cleaned : undefined
      }
      
      if (typeof obj !== 'object') {
        if (obj === null || obj === undefined || obj === '') return undefined
        return obj
      }
      
      const cleaned = {}
      for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
          const cleanedValue = cleanPayload(obj[key])
          if (cleanedValue !== undefined) {
            cleaned[key] = cleanedValue
          }
        }
      }
      return Object.keys(cleaned).length > 0 ? cleaned : undefined
    }

    const validateLearningProfile = () => {
      // Validate date of birth
      if (learningForm.value.date_of_birth) {
        const dob = new Date(learningForm.value.date_of_birth)
        const today = new Date()
        if (dob > today) {
          learningError.value = 'Date of birth cannot be in the future'
          return false
        }
      }
      
      // Validate student-specific requirements
      if (learningForm.value.user_type === 'student') {
        const stage = learningForm.value.student_profile.study_stage
        if (stage === 'College' || stage === 'University') {
          if (!learningForm.value.student_profile.course_name || !learningForm.value.student_profile.course_name.trim()) {
            learningError.value = 'Course name is required for College/University students'
            return false
          }
          if (!learningForm.value.student_profile.institution_name || !learningForm.value.student_profile.institution_name.trim()) {
            learningError.value = 'Institution name is required for College/University students'
            return false
          }
        }
      }
      
      // Validate educator-specific requirements (arrays must be arrays)
      if (learningForm.value.user_type === 'educator') {
        if (!Array.isArray(learningForm.value.educator_profile.subjects_taught)) {
          learningError.value = 'Subjects taught must be an array'
          return false
        }
        if (!Array.isArray(learningForm.value.educator_profile.stages_covered)) {
          learningError.value = 'Stages covered must be an array'
          return false
        }
      }
      
      return true
    }

    const fetchLearningProfile = async () => {
      learningLoading.value = true
      learningError.value = null
      learningSuccess.value = null

      try {
        const response = await api.get('/onboarding/profile')

        if (response.data.profile) {
          // Populate form with profile data
          const profile = response.data.profile
          
          learningForm.value = {
            date_of_birth: profile.date_of_birth || '',
            user_type: profile.user_type || '',
            timezone: profile.timezone || 'UTC',
            language_preference: profile.language_preference || 'en',
            student_profile: {
              year_level: profile.student_profile?.year_level || '',
              study_stage: profile.student_profile?.study_stage || '',
              course_name: profile.student_profile?.course_name || '',
              institution_name: profile.student_profile?.institution_name || '',
              exam_board: profile.student_profile?.exam_board || '',
              subjects: profile.student_profile?.subjects || [],
              learning_goals: profile.student_profile?.learning_goals || []
            },
            educator_profile: {
              subjects_taught: profile.educator_profile?.subjects_taught || [],
              stages_covered: profile.educator_profile?.stages_covered || [],
              exam_boards_covered: profile.educator_profile?.exam_boards_covered || [],
              use_cases: profile.educator_profile?.use_cases || [],
              institution_name: profile.educator_profile?.institution_name || '',
              class_size: profile.educator_profile?.class_size || null
            },
            user_intent: profile.user_intent || '',
            tech_comfort_level: profile.tech_comfort_level || '',
            ai_familiarity: profile.ai_familiarity || ''
          }

          hasLearningProfile.value = true
        } else {
          hasLearningProfile.value = false
        }

        learningProfileLoaded.value = true
      } catch (error) {
        learningError.value = error.response?.data?.detail || 'Failed to load learning profile'
        hasLearningProfile.value = false
      } finally {
        learningLoading.value = false
      }
    }

    const updateLearningProfile = async () => {
      learningLoading.value = true
      learningError.value = null
      learningSuccess.value = null

      // Validate form data before submission
      if (!validateLearningProfile()) {
        learningLoading.value = false
        return
      }

      try {
        // Prepare payload - deep clone
        const payload = JSON.parse(JSON.stringify(learningForm.value))

        // Remove nested objects based on user type
        if (payload.user_type === 'student') {
          delete payload.educator_profile
        } else if (payload.user_type === 'educator') {
          delete payload.student_profile
        }

        // Recursively clean empty values
        const cleanedPayload = cleanPayload(payload)

        const response = await api.put('/onboarding/profile', cleanedPayload || {})

        if (response.data.success) {
          learningSuccess.value = 'Learning profile updated successfully!'
          hasLearningProfile.value = true

          // Update auth store if needed
          if (authStore.user) {
            authStore.user.onboarding_completed = true

            // Update localStorage
            const userData = JSON.stringify(authStore.user)
            localStorage.setItem('userData', userData)
            if (sessionStorage.getItem('userData')) {
              sessionStorage.setItem('userData', userData)
            }
          }

          setTimeout(() => {
            learningSuccess.value = null
          }, 3000)
        }
      } catch (error) {
        console.error('Learning profile update error:', error.response?.data)
        learningError.value = error.response?.data?.detail || 'Failed to update learning profile'
      } finally {
        learningLoading.value = false
      }
    }

    const addToArray = (path, tempVarName) => {
      const tempVar = { newSubject, newSubjectTaught, newExamBoard }[tempVarName]
      if (!tempVar.value.trim()) return

      const parts = path.split('.')
      let target = learningForm.value
      for (let i = 0; i < parts.length - 1; i++) {
        target = target[parts[i]]
      }
      const arrayKey = parts[parts.length - 1]
      
      if (!target[arrayKey].includes(tempVar.value.trim())) {
        target[arrayKey].push(tempVar.value.trim())
      }
      
      tempVar.value = ''
    }

    const removeFromArray = (path, index) => {
      const parts = path.split('.')
      let target = learningForm.value
      for (let i = 0; i < parts.length - 1; i++) {
        target = target[parts[i]]
      }
      const arrayKey = parts[parts.length - 1]
      target[arrayKey].splice(index, 1)
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
      router,
      route,
      activeTab,
      authStore,
      profileForm,
      profileLoading,
      profileError,
      profileSuccess,
      updateProfile,
      editingUsername,
      originalUsername,
      usernameAvailable,
      usernameCheckError,
      enableUsernameEdit,
      cancelUsernameEdit,
      checkUsernameAvailability,
      submitUsernameChange,
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
      linkGoogle,
      learningForm,
      learningLoading,
      learningError,
      learningSuccess,
      learningProfileLoaded,
      hasLearningProfile,
      fetchLearningProfile,
      updateLearningProfile,
      newSubject,
      newSubjectTaught,
      newExamBoard,
      learningGoalOptions,
      stageOptions,
      useCaseOptions,
      addToArray,
      removeFromArray,
      updateTabAndQuery,
      validateLearningProfile,
      cleanPayload,
      // Comment 16: AI suggestions exports
      subjectSuggestions,
      examBoardSuggestions,
      showSubjectDropdown,
      showExamBoardDropdown,
      handleSubjectTaughtInput,
      handleExamBoardInput,
      selectSubjectSuggestion,
      selectExamBoardSuggestion
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

.username-input-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.username-input-group .form-input {
  flex: 1;
}

.username-input-group .btn {
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  white-space: nowrap;
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

/* Learning Profile Styles */
.learning-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
}

.learning-section:last-of-type {
  border-bottom: none;
}

.section-subtitle {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.25rem;
}

.chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  min-height: 2rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--accent-primary);
  color: white;
  border-radius: 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.chip-remove {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  margin-left: 0.25rem;
  transition: transform 0.2s;
}

.chip-remove:hover {
  transform: scale(1.2);
}

.add-item-group {
  display: flex;
  gap: 0.5rem;
  position: relative;
}

.add-item-group .form-input {
  flex: 1;
}

/* Comment 16: Suggestions dropdown styling */
.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 4rem;
  margin-top: 0.25rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.suggestion-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.suggestion-item:hover {
  background: var(--bg-secondary);
}

.multi-select-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.checkbox-label:hover {
  border-color: var(--accent-primary);
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.info-message {
  text-align: center;
  padding: 2rem;
  background: rgba(119, 51, 255, 0.05);
  border: 2px dashed var(--accent-primary);
  border-radius: 0.75rem;
}

.info-message p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.loading-state {
  text-align: center;
  padding: 3rem 2rem;
}

.loading-state p {
  color: var(--text-secondary);
  margin-top: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--bg-tertiary);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .multi-select-group {
    grid-template-columns: 1fr;
  }

  .add-item-group {
    flex-direction: column;
  }

  .add-item-group .btn {
    width: 100%;
  }

  .tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .tab {
    min-width: fit-content;
  }
}
</style>
