<template>
  <div 
    class="chat-view"
    :class="{ 'has-messages': messages.length > 0 }"
  >
    <!-- Centered Chat Container -->
    <div 
      class="chat-container"
      :class="{ 'chat-active': messages.length > 0 }"
    >
      <!-- Header/Branding -->
      <div 
        v-if="messages.length === 0" 
        class="chat-header"
      >
        <div class="brand-logo">
          <img
            src="/STITCH.png"
            alt="AI"
            style="width: 44px; height: 44px; object-fit: contain; vertical-align: middle;"
          >
        </div>
        <h1 class="brand-title">
          <template v-if="greetingFirstName">
            What's new, {{ greetingFirstName }}?
          </template>
          <template v-else>
            Learning starts when you start talking
          </template>
        </h1>
        <p class="brand-subtitle">
          Ask Stitch to generated a course for you, or help you learn anything.
        </p>
      </div>

      <!-- Messages Area -->
      <div
        v-if="messages.length > 0"
        ref="chatFeed"
        class="messages-area"
      >
        <!-- Message List -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div
            class="message-avatar"
            style="display: flex; align-items: center; justify-content: center; margin-right: 16px;"
          >
            <span v-if="msg.role === 'user'">👤</span>
            <span v-else>
              <img
                src="/STITCH.png"
                alt="AI"
                style="width: 36px; height: 36px; object-fit: contain; vertical-align: middle;"
              >
            </span>
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">{{ msg.role === 'user' ? 'You' : 'Stitch' }}</span>
              <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
            </div>
            <div
              v-if="isStreamingMessage(index)"
              class="message-text"
            >
              <span
                v-for="(word, wordIndex) in getStreamingWords(msg.text)"
                :key="wordIndex"
                class="streaming-word"
                :style="{ animationDelay: `${wordIndex * 0.03}s` }"
              >{{ word }}</span>
            </div>
            <div
              v-else
              class="message-text"
              v-html="formatMessage(msg.text, msg.role)"
            />
            <!-- Grounding metadata: Show search queries and citations if available -->
            <div
              v-if="msg.grounding_metadata && (msg.grounding_metadata.search_queries || msg.grounding_metadata.grounding_chunks)"
              class="message-grounding"
            >
              <details v-if="msg.grounding_metadata.search_queries && msg.grounding_metadata.search_queries.length > 0">
                <summary class="grounding-summary">
                  🔍 Sources ({{ msg.grounding_metadata.grounding_chunks.length }})
                </summary>
                <div class="grounding-details">
                  <div class="search-queries">
                    <span class="queries-label">Search queries used:</span>
                    <ul>
                      <li
                        v-for="(query, idx) in msg.grounding_metadata.search_queries"
                        :key="idx"
                      >
                        {{ query }}
                      </li>
                    </ul>
                  </div>
                  <div
                    v-if="msg.grounding_metadata.grounding_chunks && msg.grounding_metadata.grounding_chunks.length > 0"
                    class="citations"
                  >
                    <span class="citations-label">Sources:</span>
                    <ul>
                      <li
                        v-for="(chunk, idx) in msg.grounding_metadata.grounding_chunks"
                        :key="idx"
                        class="citation-item"
                      >
                        <a
                          :href="chunk.uri"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="citation-link"
                        >[{{ idx + 1 }}] {{ chunk.title || new URL(chunk.uri).hostname }}</a>
                      </li>
                    </ul>
                  </div>
                </div>
              </details>
            </div>
            <!-- URL Context metadata -->
            <div
              v-if="msg.grounding_metadata && msg.grounding_metadata.url_context && msg.grounding_metadata.url_context.length > 0"
              class="message-url-context"
            >
              <details>
                <summary class="grounding-summary">
                  🔗 URLs Retrieved
                </summary>
                <div class="url-list">
                  <div
                    v-for="(urlInfo, idx) in msg.grounding_metadata.url_context"
                    :key="idx"
                    class="url-item"
                  >
                    <a
                      :href="urlInfo.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="url-link"
                    >{{ urlInfo.url }}</a>
                    <span
                      :class="['url-status', urlInfo.status.toLowerCase()]"
                    >{{ urlInfo.status === 'URL_RETRIEVAL_STATUS_SUCCESS' ? '✓' : '✗' }}</span>
                  </div>
                </div>
              </details>
            </div>
            <div
              v-if="msg.attachment"
              class="message-attachment"
            >
              <span class="attachment-icon">📎</span>
              <span class="attachment-name">{{ msg.attachment.name }}</span>
            </div>
          </div>
        </div>
        <!-- Loading Indicator - Removed duplicate avatar, uses avatar from assistant message placeholder -->
        <Transition name="activity-fade">
          <div
            v-if="aiActivity.isActive"
            :key="aiActivity.type"
            :class="['activity-indicator-enhanced', `activity-${aiActivity.type}`]"
          >
            <div class="activity-icon-container">
              <div :class="['activity-icon', aiActivity.type]">
                {{ getActivityIcon(aiActivity.type) }}
              </div>
            </div>
            <TransitionGroup
              name="status-slide"
              tag="div"
            >
              <div
                :key="`${aiActivity.type}-${aiActivity.message}`"
                class="activity-message-text"
              >
                {{ aiActivity.message }}
              </div>
            </TransitionGroup>
            <div class="activity-progress-bar" />
          </div>
        </Transition>
      </div>

      <!-- Input Area -->
      <div class="chat-input-wrapper">
        <div
          v-if="selectedFile || urlInput"
          class="attachment-preview"
        >
          <div
            v-if="selectedFile"
            class="preview-item"
          >
            <span class="preview-icon">📄</span>
            <span class="preview-name">{{ selectedFile.name }}</span>
            <button
              class="preview-remove"
              @click="removeFile"
            >
              ×
            </button>
          </div>
          <div
            v-if="urlInput"
            class="preview-item"
          >
            <span class="preview-icon">🔗</span>
            <span class="preview-name">{{ urlInput }}</span>
            <button
              class="preview-remove"
              @click="removeUrl"
            >
              ×
            </button>
          </div>
        </div>

        <div
          v-if="error"
          class="chat-error"
        >
          {{ error }}
        </div>

        <div class="input-container">
          <label
            class="attach-btn"
            title="Upload file"
          >
            <input
              ref="fileInput"
              type="file"
              accept=".pdf,.docx,.doc,.txt,.pptx,.ppt,.xlsx,.xls,.md,.rtf"
              hidden
              @change="handleFileSelect"
            >
            📎
          </label>

          <input
            v-if="showUrlInput"
            v-model="urlInput"
            type="url"
            class="chat-input"
            placeholder="Paste URL here..."
            @keydown.enter="handleUrlSubmit"
            @keydown.esc="showUrlInput = false"
          >

          <button
            v-else-if="reachedNgLimit"
            class="link-google-btn"
            @click="linkGoogleAccount"
          >
            🔗 Link Google Account to Continue
          </button>

          <input
            v-else
            v-model="messageInput"
            type="text"
            class="chat-input"
            placeholder="I want to learn about..."
            :disabled="isLoading"
            @keydown.enter="sendMessage"
          >

          <button
            v-if="!reachedNgLimit"
            class="send-btn"
            :disabled="!canSend || isLoading"
            @click="sendMessage"
          >
            <span
              v-if="isLoading"
              class="spinner-icon"
            >⏳</span>
            <span
              v-else
              class="send-icon"
            >➤</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCourseStore } from '../stores/course'
import { useFlashcardStore } from '../stores/flashcard'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import { streamChatMessage } from '../services/chatStream'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

export default {
    name: 'ChatView',
    setup() {
        const router = useRouter()
        const route = useRoute()
        const courseStore = useCourseStore()
        const flashcardStore = useFlashcardStore()
        const authStore = useAuthStore()

        // State
        const messages = ref([])
        const messageInput = ref('')
        const urlInput = ref('')
        const selectedFile = ref(null)
        const fileInput = ref(null)
        const chatFeed = ref(null)
        const isLoading = ref(false)
        const error = ref(null)
        const showUrlInput = ref(false)
        const sessionId = ref(null)
        const aiActivity = ref({
            isActive: false,
            type: '',
            message: ''
        })
        const streamController = ref(null)
        const currentStreamingMessageIndex = ref(null)
        const isCurrentlyStreaming = ref(false)
        const isRetrying = ref(false)
        const retryAttempt = ref(0)
        const fallbackTriggered = ref(false)
        const savedCourseTitles = ref(new Set())
        const savedFlashcardTitles = ref(new Set())
        const processedIdempotencyIds = ref(new Set())
        const suppressStreamingText = ref(false)

        const examplePrompts = [
            'Create a course about Python basics',
            'Help me understand quantum physics',
            'Summarize this document'
        ]

        const canSend = computed(() => {
            return (messageInput.value.trim() || selectedFile.value || urlInput.value) && !isLoading.value
        })

        const isAuthenticated = computed(() => !!authStore.user)

        const greetingFirstName = computed(() => {
            const u = authStore.user
            // If no signed-in user, return null so template shows fallback text
            if (!u) return null
            // Prefer common fields that might contain first name
            if (u.first_name) return u.first_name
            if (u.given_name) return u.given_name
            if (u.name) {
                // If name is full name, return first token
                return String(u.name).split(' ')[0]
            }
            if (u.username) return u.username
            return null
        })

        // Non-Google per-user counter (frontend UX enforcement)
        const ngStorageKey = (username) => `ng_chat_count:${username}`
        const getNgCount = (username) => {
            if (!username) return 0
            const v = parseInt(localStorage.getItem(ngStorageKey(username)) || '0', 10)
            return Number.isNaN(v) ? 0 : v
        }
        const setNgCount = (username, n) => {
            if (!username) return
            localStorage.setItem(ngStorageKey(username), String(n))
        }
        const incrementNgCount = (username) => {
            if (!username) return 0
            const c = getNgCount(username) + 1
            setNgCount(username, c)
            return c
        }
        const nonGoogleCount = ref(0)
        const reachedNgLimit = computed(() => {
            // Unlock chat if user is Google user
            if (authStore.user?.isGoogleUser) return false
            // Check limit for non-Google authenticated users
            const isLimited = !!authStore.user && !authStore.user?.isGoogleUser && nonGoogleCount.value >= 6
            console.log('[ChatView] Limit check:', { 
                isGoogleUser: authStore.user?.isGoogleUser, 
                nonGoogleCount: nonGoogleCount.value, 
                isLimited 
            })
            return isLimited
        })
        watch(() => authStore.user, (newUser) => {
            console.log('[ChatView] User changed:', { 
                username: newUser?.username, 
                isGoogleUser: newUser?.isGoogleUser 
            })
            if (newUser?.isGoogleUser && newUser.username) {
                localStorage.removeItem(ngStorageKey(newUser.username))
                nonGoogleCount.value = 0
                // Reset error state when user becomes Google user
                error.value = null
                console.log('[ChatView] Reset count for Google user')
            } else if (newUser?.username && !newUser?.isGoogleUser) {
                // Only get count for non-Google users
                const count = getNgCount(newUser.username)
                nonGoogleCount.value = count
                console.log('[ChatView] Loaded count for non-Google user:', count)
            } else if (!newUser) {
                // User logged out
                nonGoogleCount.value = 0
                console.log('[ChatView] User logged out, reset count')
            }
        }, { deep: true, immediate: true })

        // Watch for route changes (e.g., returning from OAuth)
        watch(() => route.path, (newPath) => {
            console.log('[ChatView] Route changed to:', newPath)
            // Force re-check user status when navigating to chat
            if (newPath === '/' && authStore.user?.username) {
                // Re-initialize user data from localStorage in case it was updated
                const userData = localStorage.getItem('userData')
                if (userData) {
                    try {
                        const parsedUser = JSON.parse(userData)
                        console.log('[ChatView] Reloading user from localStorage:', parsedUser)
                        authStore.user = parsedUser
                    } catch (e) {
                        console.error('[ChatView] Failed to parse userData:', e)
                    }
                }
            }
        })

        // Watch messages and typeset math when they change
        watch(messages, () => {
            typesetMath()
        }, { deep: true })

        const showGoogleLinkButton = computed(() => {
            if (!messages.value.length) return false
            const last = messages.value[messages.value.length - 1]
            return (
                last.role === 'assistant' &&
                typeof last.text === 'string' &&
                last.text.includes('You need to be logged in to use AI features')
            )
        })

        const linkGoogleAccount = async () => {
            try {
                // Store current route for redirect after OAuth (use root path for chat)
                localStorage.setItem('oauth_redirect', '/')
                
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
                    window.location.href = response.data.auth_url
                } else {
                    error.value = 'Failed to get Google login URL.'
                }
            } catch (e) {
                error.value = 'Failed to get Google login URL.'
            }
        }

        function generateRandomState() {
            const array = new Uint8Array(32)
            window.crypto.getRandomValues(array)
            return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
        }

        const scrollToBottom = () => {
            nextTick(() => {
                if (chatFeed.value) chatFeed.value.scrollTop = chatFeed.value.scrollHeight
            })
        }

        const formatTime = (ts) => {
            const d = new Date(ts)
            return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
        }

    const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

        const formatMessage = (text, role = 'assistant') => {
            if (!text) return ''
            // Replace reference-style citation links to safe links
            let withCitations = String(text).replace(/\[(\d+)\]\((https?:\/\/[^)]+)\)/g, '[$1]($2)')

            if (role === 'assistant') {
                // Render markdown
                const rendered = md.render(withCitations)
                return DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } })
            }

            // simple user message formatting
            return withCitations.replace(/\n/g, '<br>')
        }

        // Typeset math after messages update
        const typesetMath = () => {
            nextTick(() => {
                if (window.MathJax && window.MathJax.typesetPromise) {
                    window.MathJax.typesetPromise().catch((err) => {
                        console.error('MathJax typesetting failed:', err)
                    })
                }
            })
        }

        const handleFileSelect = (e) => {
            const f = e.target.files?.[0]
            if (!f) return
            selectedFile.value = f
        }

        const removeFile = () => {
            selectedFile.value = null
            if (fileInput.value) fileInput.value.value = null
        }

        const toggleUrlInput = () => {
            showUrlInput.value = !showUrlInput.value
        }

        const handleUrlSubmit = () => {
            // trigger send
            sendMessage()
        }

        const removeUrl = () => {
            urlInput.value = ''
        }

        const sendExamplePrompt = (text) => {
            messageInput.value = text
            sendMessage()
        }

        const sendMessage = async () => {

            // ...existing code...
            if (typeof window.saEvent === 'function') {
                window.saEvent('chat_send_clicked');
            }

            // Close any active streaming connection before starting a new message
            if (streamController.value) {
                streamController.value.close()
                streamController.value = null
            }

            if (!canSend.value) return

            const userMessage = messageInput.value.trim()
            const url = urlInput.value.trim()
            const file = selectedFile.value

            const userMsg = {
                role: 'user',
                text: userMessage || (url ? `Analyzing URL: ${url}` : 'Uploaded file'),
                timestamp: Date.now(),
                attachment: file ? { name: file.name, type: file.type } : null
            }

            messages.value.push(userMsg)

            // if logged-in and not Google-linked, increment frontend counter and check limit
            if (authStore.user && !authStore.user?.isGoogleUser && authStore.user.username) {
                const c = incrementNgCount(authStore.user.username)
                nonGoogleCount.value = c
                // If we've hit the limit, show assistant notice and stop further processing
                if (c >= 6) {
                    messages.value.push({ role: 'assistant', text: 'You have reached the free chat request limit. Please link your Google account to continue.', timestamp: Date.now() })
                    isLoading.value = false
                    scrollToBottom()
                    return
                }
            }

            // clear inputs
            messageInput.value = ''
            urlInput.value = ''
            removeFile()
            showUrlInput.value = false
            error.value = null
            isLoading.value = true

            // Set initial activity indicator to thinking (will be updated by backend status events)
            aiActivity.value = {
                isActive: true,
                type: 'thinking',
                message: 'Processing your request...'
            }

            scrollToBottom()

            try {
                if (!isAuthenticated.value) {
                    const fake = 'You need to be logged in to use AI features, if you want to try AI Generated course, checkout "library" for community generated courses.'
                    messages.value.push({ role: 'assistant', text: fake, timestamp: Date.now() })
                    isLoading.value = false
                    scrollToBottom()
                    return
                }

                // Handle file uploads using POST endpoint
                if (file) {
                    const formData = new FormData()
                    formData.append('message', userMessage || 'Please analyze this content')
                    if (sessionId.value) formData.append('session_id', sessionId.value)
                    formData.append('file', file)
                    if (url) formData.append('url', url)
                    if (authStore.user?.username) formData.append('username', authStore.user.username)

                    const response = await api.post('/chat/message', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
                    console.log('Chat API response:', response)

                    // Development-only debug log for response structure
                    if (import.meta.env.DEV) {
                        console.log('[DEV] Response data keys:', Object.keys(response.data))
                        console.log('[DEV] is_course:', response.data.is_course, 'has course_data:', !!response.data.course_data)
                        console.log('[DEV] is_flashcard:', response.data.is_flashcard, 'has flashcard_data:', !!response.data.flashcard_data)
                    }

                    // Update activity indicator with backend info if available
                    if (response.data.activity_info) {
                        aiActivity.value = {
                            isActive: true,
                            type: response.data.activity_info.type,
                            message: response.data.activity_info.message
                        }
                    }

                    if (!response.data.success) throw new Error(response.data.error || 'Failed to get response')

                    sessionId.value = response.data.session_id
                    localStorage.setItem('chat_session_id', sessionId.value)

                    if (response.data.is_course && response.data.course_data) {
                        const saveResult = await courseStore.saveCourse(response.data.course_data.sections, response.data.course_data.course_title)
                        if (saveResult.success) {
                            messages.value.push({ role: 'system', text: `🎓 Course "${response.data.course_data.course_title}" created successfully! Redirecting...`, timestamp: Date.now() })
                            scrollToBottom()
                            setTimeout(() => router.push(`/course/${saveResult.courseId}`), 1200)
                        } else {
                            throw new Error(saveResult.error || 'Failed to save course')
                        }
                    } else if (response.data.is_flashcard && response.data.flashcard_data) {
                        // Handle flashcard generation
                        const flashcardData = response.data.flashcard_data
                        const saveResult = await flashcardStore.saveFlashcard(
                            flashcardData.cards,
                            flashcardData.flashcard_title,
                            flashcardData.source_course_id || null
                        )
                        if (saveResult.success) {
                            messages.value.push({ role: 'system', text: `🃏 Flashcard set "${flashcardData.flashcard_title}" created successfully! Redirecting...`, timestamp: Date.now() })
                            scrollToBottom()
                            setTimeout(() => router.push(`/flashcard/${saveResult.flashcardId}`), 1200)
                        } else {
                            throw new Error(saveResult.error || 'Failed to save flashcards')
                        }
                    } else {
                        if (response.data.reply && response.data.reply.trim()) {
                            const aiMsg = { role: 'assistant', text: response.data.reply, timestamp: Date.now() }
                            // Attach grounding metadata if available
                            if (response.data.grounding_metadata) {
                                aiMsg.grounding_metadata = response.data.grounding_metadata
                            }
                            messages.value.push(aiMsg)
                        } else {
                            messages.value.push({ role: 'system', text: '⚠️ No reply received from AI. Please check backend logs or try again later.', timestamp: Date.now() })
                        }
                    }

                    scrollToBottom()
                    isLoading.value = false
                    aiActivity.value = { isActive: false, type: '', message: '' }
                    return
                }

                // Handle text-only messages using streaming
                const aiMessageIndex = messages.value.length
                messages.value.push({
                    role: 'assistant',
                    text: '',
                    timestamp: Date.now()
                })
                currentStreamingMessageIndex.value = aiMessageIndex

                // Adaptive typewriter effect - adjusts speed based on streaming rate
                let characterQueue = ''
                let characterTicker = null
                let isStreamComplete = false
                let lastChunkTime = Date.now()
                let chunkCount = 0
                let adaptiveDelay = 40 // Start with 40ms per character
                
                const calculateAdaptiveDelay = () => {
                    const now = Date.now()
                    const timeSinceLastChunk = now - lastChunkTime
                    lastChunkTime = now
                    chunkCount++
                    
                    // If chunks arrive very quickly (< 100ms apart), use sentence-based display
                    if (timeSinceLastChunk < 100 && chunkCount > 1) {
                        // Display at ~1 sentence per second (roughly 60-80 words per second)
                        return 15 // 15ms per character = ~67 characters per second
                    }
                    // If chunks arrive slowly, use character-by-character
                    return 40 // 40ms per character
                }
                
                const processCharacter = () => {
                    if (characterQueue.length > 0) {
                        const char = characterQueue.charAt(0)
                        characterQueue = characterQueue.slice(1)
                        
                        if (messages.value[aiMessageIndex]) {
                            messages.value[aiMessageIndex].text += char
                            isCurrentlyStreaming.value = true
                            scrollToBottom()
                            debouncedSaveChatMessages()
                        }
                        
                        // Recalculate delay for next character
                        adaptiveDelay = calculateAdaptiveDelay()
                        characterTicker = setTimeout(processCharacter, adaptiveDelay)
                    } else if (isStreamComplete) {
                        // Stream is complete and queue is empty, stop processing
                        characterTicker = null
                    }
                }

                const startCharacterTicker = () => {
                    if (!characterTicker) {
                        adaptiveDelay = calculateAdaptiveDelay()
                        characterTicker = setTimeout(processCharacter, adaptiveDelay)
                    }
                }

                const stopCharacterTicker = () => {
                    if (characterTicker) {
                        clearTimeout(characterTicker)
                        characterTicker = null
                    }
                }

                // Start streaming
                streamController.value = streamChatMessage({
                    message: userMessage || 'Hello',
                    sessionId: sessionId.value,
                    url: url || null,
                    username: authStore.user?.username || null,
                    
                    onStatus: (statusData) => {
                        // Only show specific tags for function call actions, otherwise default to thinking
                        let activityType = 'thinking'
                        let activityMessage = statusData.message || 'Processing...'
                        
                        if (statusData.action === 'course_generation' || statusData.action === 'flashcard_generation') {
                            activityType = statusData.type || activityType
                        }
                        
                        aiActivity.value = {
                            isActive: true,
                            type: activityType,
                            message: activityMessage
                        }
                    },
                    
                    onChunk: (text) => {
                        // Suppress text chunks if tool is generating content
                        if (suppressStreamingText.value) {
                            return
                        }
                        
                        // Queue characters for throttled display
                        characterQueue += text
                        startCharacterTicker()
                    },
                    
                    onCourse: async (courseData) => {
                        try {
                            // Comment 6: Suppress streaming text and show generation status
                            suppressStreamingText.value = true
                            
                            // Clear placeholder text and update activity
                            if (messages.value[aiMessageIndex]) {
                                messages.value[aiMessageIndex].text = ''
                            }
                            
                            aiActivity.value = {
                                isActive: true,
                                type: 'generating_course',
                                message: 'Generating course content…'
                            }
                            
                            // Extract idempotency ID if present
                            let courseContent = courseData
                            let idempotencyId = null
                            
                            if (courseData.idempotency_id) {
                                idempotencyId = courseData.idempotency_id
                                courseContent = courseData.data || courseData
                            }
                            
                            // Check if already processed using idempotency ID
                            if (idempotencyId && processedIdempotencyIds.value.has(idempotencyId)) {
                                console.log('[ChatView] Idempotent course already processed, skipping duplicate')
                                return
                            }
                            
                            // Check if course was already saved using Set
                            if (savedCourseTitles.value.has(courseContent.course_title)) {
                                console.log('[ChatView] Course already saved, skipping duplicate')
                                return
                            }

                            const saveResult = await courseStore.saveCourse(
                                courseContent.sections,
                                courseContent.course_title
                            )
                            if (saveResult.success) {
                                // Track saved course and idempotency ID
                                savedCourseTitles.value.add(courseContent.course_title)
                                if (idempotencyId) {
                                    processedIdempotencyIds.value.add(idempotencyId)
                                }
                                
                                // Update activity to show redirect status
                                aiActivity.value = {
                                    isActive: true,
                                    type: 'thinking',
                                    message: 'Redirecting you…'
                                }
                                
                                messages.value.push({
                                    role: 'system',
                                    text: `🎓 Course "${courseContent.course_title}" created successfully! Redirecting...`,
                                    timestamp: Date.now()
                                })
                                scrollToBottom()
                                setTimeout(() => {
                                    aiActivity.value = { isActive: false, type: '', message: '' }
                                    router.push(`/course/${saveResult.courseId}`)
                                }, 1200)
                            } else {
                                throw new Error(saveResult.error || 'Failed to save course')
                            }
                        } catch (err) {
                            console.error('Error saving course:', err)
                            error.value = err.message || 'Failed to save course'
                            messages.value.push({
                                role: 'system',
                                text: `⚠️ Error saving course: ${error.value}`,
                                timestamp: Date.now()
                            })
                            scrollToBottom()
                        }
                    },
                    
                    onFlashcard: async (flashcardData) => {
                        try {
                            // Comment 6: Suppress streaming text and show generation status
                            suppressStreamingText.value = true
                            
                            // Clear placeholder text and update activity
                            if (messages.value[aiMessageIndex]) {
                                messages.value[aiMessageIndex].text = ''
                            }
                            
                            aiActivity.value = {
                                isActive: true,
                                type: 'generating_flashcard',
                                message: 'Generating flashcards…'
                            }
                            
                            // Extract idempotency ID if present
                            let flashcardContent = flashcardData
                            let idempotencyId = null
                            
                            if (flashcardData.idempotency_id) {
                                idempotencyId = flashcardData.idempotency_id
                                flashcardContent = flashcardData.data || flashcardData
                            }
                            
                            // Check if already processed using idempotency ID
                            if (idempotencyId && processedIdempotencyIds.value.has(idempotencyId)) {
                                console.log('[ChatView] Idempotent flashcard already processed, skipping duplicate')
                                return
                            }
                            
                            // Check if flashcard was already saved using Set
                            if (savedFlashcardTitles.value.has(flashcardContent.flashcard_title)) {
                                console.log('[ChatView] Flashcard already saved, skipping duplicate')
                                return
                            }

                            const saveResult = await flashcardStore.saveFlashcard(
                                flashcardContent.cards,
                                flashcardContent.flashcard_title,
                                flashcardContent.source_course_id || null
                            )
                            if (saveResult.success) {
                                // Track saved flashcard and idempotency ID
                                savedFlashcardTitles.value.add(flashcardContent.flashcard_title)
                                if (idempotencyId) {
                                    processedIdempotencyIds.value.add(idempotencyId)
                                }
                                
                                // Update activity to show redirect status
                                aiActivity.value = {
                                    isActive: true,
                                    type: 'thinking',
                                    message: 'Redirecting you…'
                                }
                                
                                messages.value.push({
                                    role: 'system',
                                    text: `🃏 Flashcard set "${flashcardContent.flashcard_title}" created successfully! Redirecting...`,
                                    timestamp: Date.now()
                                })
                                scrollToBottom()
                                setTimeout(() => {
                                    aiActivity.value = { isActive: false, type: '', message: '' }
                                    router.push(`/flashcard/${saveResult.flashcardId}`)
                                }, 1200)
                            } else {
                                throw new Error(saveResult.error || 'Failed to save flashcards')
                            }
                        } catch (err) {
                            console.error('Error saving flashcards:', err)
                            error.value = err.message || 'Failed to save flashcards'
                            messages.value.push({
                                role: 'system',
                                text: `⚠️ Error saving flashcards: ${error.value}`,
                                timestamp: Date.now()
                            })
                            scrollToBottom()
                        }
                    },
                    
                    onComplete: (newSessionId, groundingMetadata) => {
                        // Attach grounding metadata to the latest AI message
                        if (groundingMetadata && messages.value[aiMessageIndex]) {
                            messages.value[aiMessageIndex].grounding_metadata = groundingMetadata
                        }
                        
                        // Mark stream as complete so ticker stops when queue is empty
                        isStreamComplete = true
                        
                        // Wait for character queue to drain
                        if (characterQueue.length === 0) {
                            stopCharacterTicker()
                            // Clear activity indicator immediately
                            isRetrying.value = false
                            retryAttempt.value = 0
                            sessionId.value = newSessionId
                            localStorage.setItem('chat_session_id', sessionId.value)
                            isLoading.value = false
                            isCurrentlyStreaming.value = false
                            aiActivity.value = { isActive: false, type: '', message: '' }
                            streamController.value = null
                            currentStreamingMessageIndex.value = null
                            suppressStreamingText.value = false
                            scrollToBottom()
                        } else {
                            // Schedule cleanup after queue drains
                            const checkQueueEmpty = setInterval(() => {
                                if (characterQueue.length === 0 && !characterTicker) {
                                    clearInterval(checkQueueEmpty)
                                    isRetrying.value = false
                                    retryAttempt.value = 0
                                    sessionId.value = newSessionId
                                    localStorage.setItem('chat_session_id', sessionId.value)
                                    isLoading.value = false
                                    isCurrentlyStreaming.value = false
                                    aiActivity.value = { isActive: false, type: '', message: '' }
                                    streamController.value = null
                                    currentStreamingMessageIndex.value = null
                                    suppressStreamingText.value = false
                                    scrollToBottom()
                                }
                            }, 50)
                        }
                    },
                    
                    onRetry: (retryState) => {
                        isRetrying.value = true
                        retryAttempt.value = retryState.retryCount
                        aiActivity.value = {
                            isActive: true,
                            type: 'thinking',
                            message: `Connection lost, reconnecting (${retryState.retryCount}/${retryState.maxRetries})...`
                        }
                    },
                    
                    onFallback: () => {
                        console.log('[ChatView] Fallback callback triggered')
                        handleStreamFallback(userMessage, url, aiMessageIndex)
                    },
                    
                    onError: (errorMsg) => {
                        console.error('Streaming error:', errorMsg)
                        
                        // Don't push error if fallback was already triggered
                        if (fallbackTriggered.value) {
                            console.log('[ChatView] Fallback in progress, suppressing error message')
                            return
                        }

                        error.value = errorMsg

                        // Remove placeholder AI message if it's empty
                        if (messages.value[aiMessageIndex] && !messages.value[aiMessageIndex].text) {
                            messages.value.splice(aiMessageIndex, 1)
                        }

                        messages.value.push({
                            role: 'system',
                            text: `⚠️ Error: ${errorMsg}`,
                            timestamp: Date.now()
                        })

                        isLoading.value = false
                        isRetrying.value = false
                        aiActivity.value = { isActive: false, type: '', message: '' }
                        streamController.value = null
                        currentStreamingMessageIndex.value = null
                        scrollToBottom()
                    }
                })

            } catch (err) {
                console.error('Error sending message:', err)
                error.value = err.response?.data?.detail || err.message || 'Failed to send message'
                messages.value.push({ role: 'system', text: `⚠️ Error: ${error.value}`, timestamp: Date.now() })
                scrollToBottom()
                isLoading.value = false
                aiActivity.value = { isActive: false, type: '', message: '' }
            }
        }

        /**
         * Fallback handler when streaming fails after max retries
         */
        async function handleStreamFallback(userMessage, url, aiMessageIndex) {
            // Prevent duplicate fallback calls
            if (fallbackTriggered.value) {
                console.log('[ChatView] Fallback already triggered, skipping duplicate call')
                return
            }

            fallbackTriggered.value = true
            console.log('[ChatView] Streaming failed, falling back to POST endpoint')

            try {
                // Update activity indicator
                aiActivity.value = {
                    isActive: true,
                    type: 'thinking',
                    message: 'Retrying with standard mode...'
                }

                // Build FormData for POST endpoint
                const formData = new FormData()
                formData.append('message', userMessage || 'Hello')
                if (sessionId.value) formData.append('session_id', sessionId.value)
                if (url) formData.append('url', url)
                if (authStore.user?.username) formData.append('username', authStore.user.username)

                // Call POST endpoint with FormData
                const response = await api.post('/chat/message', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                })

                console.log('[ChatView] Fallback POST response:', response)

                if (!response.data.success) {
                    throw new Error(response.data.error || 'Failed to get response')
                }

                // Update session ID
                sessionId.value = response.data.session_id
                localStorage.setItem('chat_session_id', sessionId.value)

                // Handle course response
                if (response.data.is_course && response.data.course_data) {
                    const saveResult = await courseStore.saveCourse(
                        response.data.course_data.sections,
                        response.data.course_data.course_title
                    )
                    if (saveResult.success) {
                        messages.value.push({
                            role: 'system',
                            text: `🎓 Course "${response.data.course_data.course_title}" created successfully! Redirecting...`,
                            timestamp: Date.now()
                        })
                        scrollToBottom()
                        setTimeout(() => router.push(`/course/${saveResult.courseId}`), 1200)
                    } else {
                        throw new Error(saveResult.error || 'Failed to save course')
                    }
                }
                // Handle flashcard response
                else if (response.data.is_flashcard && response.data.flashcard_data) {
                    const flashcardData = response.data.flashcard_data
                    const saveResult = await flashcardStore.saveFlashcard(
                        flashcardData.cards,
                        flashcardData.flashcard_title,
                        flashcardData.source_course_id || null
                    )
                    if (saveResult.success) {
                        messages.value.push({
                            role: 'system',
                            text: `🃏 Flashcard set "${flashcardData.flashcard_title}" created successfully! Redirecting...`,
                            timestamp: Date.now()
                        })
                        scrollToBottom()
                        setTimeout(() => router.push(`/flashcard/${saveResult.flashcardId}`), 1200)
                    } else {
                        throw new Error(saveResult.error || 'Failed to save flashcards')
                    }
                }
                // Handle regular text response
                else {
                    if (response.data.reply && response.data.reply.trim()) {
                        // Append to existing AI message if it exists, otherwise create new one
                        if (aiMessageIndex !== null && messages.value[aiMessageIndex]) {
                            messages.value[aiMessageIndex].text += response.data.reply
                        } else {
                            messages.value.push({
                                role: 'assistant',
                                text: response.data.reply,
                                timestamp: Date.now()
                            })
                        }
                    } else {
                        messages.value.push({
                            role: 'system',
                            text: '⚠️ No reply received from AI. Please check backend logs or try again later.',
                            timestamp: Date.now()
                        })
                    }
                }

                scrollToBottom()
            } catch (err) {
                console.error('[ChatView] Fallback error:', err)
                error.value = err.response?.data?.detail || err.message || 'Failed to send message'
                messages.value.push({
                    role: 'system',
                    text: `⚠️ Error: ${error.value}`,
                    timestamp: Date.now()
                })
                scrollToBottom()
            } finally {
                isLoading.value = false
                isRetrying.value = false
                aiActivity.value = { isActive: false, type: '', message: '' }
                fallbackTriggered.value = false
            }
        }

        // Activity indicator helper functions
        const determineActivityType = (message, file, url) => {
            if (file) {
                if (message && (message.toLowerCase().includes('course') || message.toLowerCase().includes('generate'))) {
                    return 'generating_course'
                }
                return 'processing_file'
            }
            if (url) return 'searching_web'
            if (message) {
                const lowerMsg = message.toLowerCase()
                if (lowerMsg.includes('flashcard') || lowerMsg.includes('flash card') || lowerMsg.includes('study cards')) {
                    return 'generating_flashcard'
                }
                if (lowerMsg.includes('course') || lowerMsg.includes('generate') || lowerMsg.includes('create')) {
                    return 'generating_course'
                }
                if (lowerMsg.includes('search') || lowerMsg.includes('find')) {
                    return 'searching_web'
                }
            }
            return 'thinking'
        }

        const getActivityIcon = (type) => {
            const icons = {
                'thinking': '🧠',
                'searching_web': '🌐',
                'generating_course': '🎓',
                'generating_flashcard': '🃏',
                'processing_file': '📄'
            }
            return icons[type] || '🧠'
        }

        const getActivityMessage = (message, file, url) => {
            if (file) {
                if (message && (message.toLowerCase().includes('course') || message.toLowerCase().includes('generate'))) {
                    return `🎓 Generating course from ${file.name}...`
                }
                return `📄 Processing ${file.name}...`
            }
            if (url) return `🌐 Searching the web...`
            if (message) {
                const lowerMsg = message.toLowerCase()
                if (lowerMsg.includes('flashcard') || lowerMsg.includes('flash card') || lowerMsg.includes('study cards')) {
                    return '🃏 Generating flashcards...'
                }
                if (lowerMsg.includes('course') || lowerMsg.includes('generate') || lowerMsg.includes('create')) {
                    return '🎓 Generating course content...'
                }
                if (lowerMsg.includes('search') || lowerMsg.includes('find')) {
                    return '🔍 Searching for information...'
                }
            }
            return '🧠 Thinking...'
        }

        const isStreamingMessage = (index) => {
            return currentStreamingMessageIndex.value === index && isCurrentlyStreaming.value
        }

        const getStreamingWords = (text) => {
            return text.split(/(\s+)/).filter(word => word.length > 0)
        }

        // Save and load chat messages from localStorage
        const saveChatMessages = () => {
            try {
                const chatData = {
                    messages: messages.value,
                    sessionId: sessionId.value,
                    timestamp: Date.now()
                }
                localStorage.setItem('chat_messages', JSON.stringify(chatData))
            } catch (e) {
                console.error('Failed to save chat messages:', e)
            }
        }

        const loadChatMessages = () => {
            try {
                const savedData = localStorage.getItem('chat_messages')
                if (savedData) {
                    const chatData = JSON.parse(savedData)
                    // Load messages if they're less than 24 hours old
                    const age = Date.now() - (chatData.timestamp || 0)
                    if (age < 24 * 60 * 60 * 1000) {
                        if (Array.isArray(chatData.messages)) {
                            messages.value = chatData.messages
                        } else {
                            messages.value = []
                        }
                        sessionId.value = chatData.sessionId || sessionId.value
                        // Scroll to bottom after loading
                        nextTick(() => scrollToBottom())
                    }
                }
            } catch (e) {
                console.error('Failed to load chat messages:', e)
                messages.value = []
            }
        }

        // Debounced save function to reduce localStorage thrash during streaming
        let saveTimeout = null
        const debouncedSaveChatMessages = () => {
            if (saveTimeout) {
                clearTimeout(saveTimeout)
            }
            saveTimeout = setTimeout(() => {
                saveChatMessages()
            }, 400) // 400ms debounce
        }

        // Watch messages and save to localStorage whenever they change (debounced)
        watch(messages, () => {
            debouncedSaveChatMessages()
        }, { deep: true })

        onMounted(() => {
            const saved = localStorage.getItem('chat_session_id')
            if (saved) sessionId.value = saved
            // Load saved chat messages
            loadChatMessages()
            // Initialize nonGoogleCount for current user
            if (authStore.user?.username && !authStore.user?.isGoogleUser) {
                const count = getNgCount(authStore.user.username)
                nonGoogleCount.value = count
                console.log('[ChatView] Initialized count on mount:', count, 'for user:', authStore.user.username)
            } else if (authStore.user?.isGoogleUser) {
                console.log('[ChatView] Google user on mount, count stays 0')
            }
        })

        onUnmounted(() => {
            // Cleanup: close any active streaming connection when component is unmounted
            if (streamController.value) {
                streamController.value.close()
            }
        })

        return {
            messages,
            messageInput,
            urlInput,
            selectedFile,
            fileInput,
            chatFeed,
            isLoading,
            error,
            showUrlInput,
            examplePrompts,
            canSend,
            formatTime,
            formatMessage,
            greetingFirstName,
            handleFileSelect,
            removeFile,
            toggleUrlInput,
            handleUrlSubmit,
            removeUrl,
            sendExamplePrompt,
            sendMessage,
            showGoogleLinkButton,
            linkGoogleAccount,
            reachedNgLimit,
            aiActivity,
            streamController,
            currentStreamingMessageIndex,
            isCurrentlyStreaming,
            isStreamingMessage,
            getStreamingWords,
            getActivityIcon,
            determineActivityType,
            getActivityMessage,
            isRetrying,
            retryAttempt,
            fallbackTriggered,
            handleStreamFallback,
            savedCourseTitles,
            savedFlashcardTitles,
            processedIdempotencyIds
        }
    }
}
</script>

<style scoped>
/* Main Chat View Container */
.chat-view {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-primary);
    padding: 1rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}


.chat-view.has-messages {
    align-items: stretch;
    padding: 0 !important;
    margin: 0;
    width: 100%;
    box-sizing: border-box;
    position: static;
}

/* Chat Container - Centered initially, then expands */
.chat-container {
    width: 100%;
    max-width: 680px;
    background: var(--card-bg);
    border-radius: 1.5rem;
    box-shadow: 0 20px 60px var(--shadow-color);
    overflow: hidden;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
}


.chat-container.chat-active {
    max-width: 100%;
    width: 100%;
    height: 100vh;
    border-radius: 0;
    animation: expandToBottom 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    box-sizing: border-box;
    margin: 0;
    position: relative;
}

@keyframes expandToBottom {
    0% {
        transform: translateY(0);
        max-width: 680px;
        border-radius: 1.5rem;
    }
    100% {
        transform: translateY(0);
        max-width: 100%;
        border-radius: 0;
    }
}

/* Chat Header - Only visible before first message */
.chat-header {
    padding: 3rem 2rem 2rem;
    text-align: center;
    border-bottom: 1px solid var(--border-color);
}

.brand-logo {
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: center;
}

.logo-image {
    width: 80px;
    height: 80px;
    object-fit: contain;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-10px);
    }
}

.brand-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.brand-subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
}

/* Messages Area - Scrollable conversation */
.messages-area {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    scroll-behavior: smooth;
    min-height: 0;
}

/* Scrollbar styling */
.messages-area::-webkit-scrollbar {
    width: 6px;
}

.messages-area::-webkit-scrollbar-track {
    background: transparent;
}

.messages-area::-webkit-scrollbar-thumb {
    background: rgba(119, 51, 255, 0.2);
    border-radius: 3px;
}

.messages-area::-webkit-scrollbar-thumb:hover {
    background: rgba(119, 51, 255, 0.3);
}

/* Individual Message */
.message {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    animation: messageSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    opacity: 0;
    animation-fill-mode: forwards;
}

@keyframes messageSlideIn {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.user-message {
    flex-direction: row-reverse;
    justify-content: flex-start;
    margin-left: auto;
}

/* Message Avatar */

.message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
    background: transparent;
    border: none;
}

.user-message .message-avatar {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    border: none;
}


.stitch-logo {
    width: 36px;
    height: 36px;
    object-fit: contain;
    border: none;
    border-radius: 0;
}

/* Message Content */
.message-content {
    flex: 1;
    min-width: 0;
}

.user-message .message-content {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.message-header {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-bottom: 0.5rem;
}

.user-message .message-header {
    flex-direction: row-reverse;
    justify-content: flex-start;
}

.message-sender {
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--text-primary);
}

.message-time {
    font-size: 0.75rem;
    color: var(--text-muted);
}

/* Message Text */
.message-text {
    line-height: 1.6;
    font-size: 0.95rem;
    color: var(--text-primary);
    word-wrap: break-word;
    overflow-wrap: anywhere;
}

.user-message .message-text {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    color: white;
    padding: 0.875rem 1.125rem;
    border-radius: 1.25rem;
    border-top-right-radius: 0.25rem;
    box-shadow: 0 4px 12px rgba(119, 51, 255, 0.25);
    display: inline-block;
}

.ai-message .message-text {
    padding: 0.5rem 0;
    contain: layout style paint;
}

/* Message Attachment */
.message-attachment {
    margin-top: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
}

.attachment-icon {
    font-size: 1rem;
}

.attachment-name {
    color: var(--text-secondary);
}

/* Typing Indicator */
.typing-indicator {
    display: flex;
    gap: 0.4rem;
    padding: 1rem;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: var(--accent-primary);
    border-radius: 50%;
    animation: typing 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.4;
    }
    30% {
        transform: translateY(-8px);
        opacity: 1;
    }
}

/* Activity Indicator */
.activity-indicator {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.activity-message {
    font-size: 0.875rem;
    color: var(--text-muted);
    opacity: 0.8;
    font-style: italic;
    padding: 0 1rem;
    animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 0.8;
        transform: translateY(0);
    }
}

/* Chat Input Wrapper - Sticky at bottom */
.chat-input-wrapper {
    padding: 1.25rem 1.5rem;
    background: var(--card-bg);
    border-top: 1px solid var(--border-color);
    backdrop-filter: blur(10px);
    flex-shrink: 0;
    z-index: 10;
}

/* Attachment Preview */
.attachment-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.preview-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 1rem;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    font-size: 0.875rem;
    animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.preview-icon {
    font-size: 1rem;
}

.preview-name {
    color: var(--text-secondary);
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.preview-remove {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
}

.preview-remove:hover {
    background: var(--border-color);
    color: var(--text-primary);
}

/* Chat Error */
.chat-error {
    padding: 0.875rem 1rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.75rem;
    color: #ef4444;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    animation: fadeIn 0.3s ease;
}

/* Input Container */
.input-container {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    background: var(--bg-tertiary);
    border: 2px solid var(--border-color);
    border-radius: 1.5rem;
    padding: 0.5rem 0.75rem;
    transition: all 0.3s ease;
}

.input-container:focus-within {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 4px rgba(119, 51, 255, 0.1);
}

/* Attach Button */
.attach-btn {
    width: 40px;
    height: 40px;
    border-radius: 0.75rem;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    font-size: 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.attach-btn:hover {
    background: var(--border-color);
    color: var(--accent-primary);
}

/* Chat Input Field */
.chat-input {
    flex: 1;
    padding: 0.75rem 0.5rem;
    border: none;
    background: transparent;
    color: var(--text-primary);
    font-size: 0.95rem;
    outline: none;
    min-width: 0;
}

.chat-input::placeholder {
    color: var(--text-muted);
}

.chat-input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* Send Button */
.send-btn {
    width: 40px;
    height: 40px;
    border-radius: 0.75rem;
    border: none;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    color: white;
    font-size: 1.125rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(119, 51, 255, 0.3);
}

.send-btn:hover:not(:disabled) {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(119, 51, 255, 0.4);
}

.send-btn:active:not(:disabled) {
    transform: scale(0.95);
}

.send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.send-icon {
    display: flex;
    align-items: center;
    justify-content: center;
}

.spinner-icon {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

/* Link Google Button */
.link-google-btn {
    flex: 1;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 1rem;
    background: linear-gradient(135deg, #4285f4, #34a853);
    color: white;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
}

.link-google-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(66, 133, 244, 0.4);
}

.link-google-btn:active {
    transform: translateY(0);
}

:deep(.citation-link) {
    color: var(--accent-primary);
    text-decoration: none;
    font-weight: 600;
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    background: rgba(119, 51, 255, 0.1);
}

:deep(.citation-link:hover) {
    background: rgba(119, 51, 255, 0.2);
    text-decoration: underline;
}

/* Markdown styling for AI messages */
:deep(.message-text) h1,
:deep(.message-text) h2,
:deep(.message-text) h3 {
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}

:deep(.message-text) p {
    margin-bottom: 0.75rem;
}

:deep(.message-text) code {
    background: rgba(0, 0, 0, 0.1);
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
}

:deep(.message-text) pre {
    background: rgba(0, 0, 0, 0.1);
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    max-width: 100%;
    margin: 0.75rem 0;
}

/* Ensure rich content doesn't overflow the viewport */
:deep(.message-text) img {
    max-width: 100%;
    height: auto;
    display: inline-block;
}

:deep(.message-text) table {
    display: block;
    max-width: 100%;
    overflow-x: auto;
}

:deep(.message-text) ul,
:deep(.message-text) ol {
    margin-left: 1.5rem;
    margin-bottom: 0.75rem;
}

:deep(.message-text) li {
    margin-bottom: 0.25rem;
}

:deep(.message-text) a {
    color: var(--accent-primary);
    text-decoration: underline;
}

/* MathLive display math styling */
:deep(.math-display) {
    text-align: center !important;
    margin: 1rem 0 !important;
    display: block !important;
    overflow-x: auto;
}

:deep(.math-error) {
    color: #dc3545;
    background: rgba(220, 53, 69, 0.1);
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin: 0.5rem 0;
    display: block;
}

.user-message :deep(.message-text) code,
.user-message :deep(.message-text) pre {
    background: rgba(255, 255, 255, 0.2);
}

/* Responsive Design */
@media (max-width: 768px) {
    .chat-view {
        padding: 0;
    }

    .chat-container {
        border-radius: 0;
        max-width: 100%;
    }

    .chat-header {
        padding: 2rem 1.5rem 1.5rem;
    }

    .brand-title {
        font-size: 1.5rem;
    }

    .brand-subtitle {
        font-size: 0.875rem;
    }

    .logo-image {
        width: 60px;
        height: 60px;
    }

    .messages-area {
        padding: 1rem;
        gap: 1.25rem;
    }

    .message-avatar {
        width: 36px;
        height: 36px;
    }

    .stitch-logo {
        width: 20px;
        height: 20px;
    }

    .message-text {
        font-size: 0.9rem;
    }

    .chat-input-wrapper {
        padding: 1rem;
    }

    .input-container {
        padding: 0.375rem 0.5rem;
    }

    .attach-btn,
    .send-btn {
        width: 36px;
        height: 36px;
    }

    .chat-input {
        font-size: 0.9rem;
        padding: 0.625rem 0.375rem;
    }
}

@media (max-width: 480px) {
    .chat-header {
        padding: 1.5rem 1rem 1rem;
    }

    .brand-title {
        font-size: 1.25rem;
    }

    .messages-area {
        padding: 0.75rem;
    }

    .message {
        gap: 0.75rem;
    }

    .message-avatar {
        width: 32px;
        height: 32px;
        font-size: 1rem;
    }
}

/* Enhanced Activity Indicator Styles */
.activity-indicator-enhanced {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(119, 51, 255, 0.05);
    border-radius: 0.75rem;
    margin: 0.5rem 0;
}

.activity-icon-container {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.activity-icon {
    font-size: 1.5rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 0.5rem;
    background: rgba(119, 51, 255, 0.1);
}

.activity-icon.thinking {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.activity-icon.searching_web {
    animation: rotate 2s linear infinite;
}

.activity-icon.generating_course {
    animation: bounce 1.5s ease-in-out infinite;
}

.activity-icon.generating_flashcard {
    animation: flip 1.5s ease-in-out infinite;
}

.activity-icon.processing_file {
    animation: slide 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.1);
        opacity: 0.8;
    }
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

@keyframes bounce {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-8px);
    }
}

@keyframes flip {
    0%, 100% {
        transform: rotateY(0deg);
    }
    50% {
        transform: rotateY(180deg);
    }
}

@keyframes slide {
    0%, 100% {
        transform: translateX(0);
    }
    50% {
        transform: translateX(8px);
    }
}

@keyframes progress {
    0% {
        width: 0%;
    }
    100% {
        width: 100%;
    }
}

.activity-progress-bar {
    height: 2px;
    background: rgba(119, 51, 255, 0.1);
    border-radius: 1px;
    overflow: hidden;
    position: relative;
}

.activity-progress-bar::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    background: linear-gradient(
        90deg,
        transparent 0%,
        var(--accent-primary) 50%,
        transparent 100%
    );
    animation: shimmer 2s ease-in-out infinite;
}

@keyframes shimmer {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(200%);
    }
}

.activity-message-text {
    font-size: 0.875rem;
    color: var(--text-muted);
    opacity: 0.8;
    font-style: italic;
}

/* ChatGPT-style typewriter effect */
.ai-message .message-text {
    display: inline-block;
    animation: typewriterText steps(1, end) 0.05s;
    animation-fill-mode: forwards;
    overflow: hidden;
    white-space: pre-wrap;
    word-wrap: break-word;
}

@keyframes typewriterText {
    0% {
        max-width: 0;
        opacity: 1;
    }
    99% {
        max-width: 100vw;
        opacity: 1;
    }
    100% {
        max-width: 100%;
        opacity: 1;
    }
}

/* Vue Transition Styles */
.activity-fade-enter-active,
.activity-fade-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.activity-fade-enter-from,
.activity-fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

.status-slide-enter-active,
.status-slide-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.status-slide-enter-from {
    opacity: 0;
    transform: translateX(-20px);
}

.status-slide-leave-to {
    opacity: 0;
    transform: translateX(20px);
}

.status-slide-move {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Grounding Metadata Styles */
.message-grounding,
.message-url-context {
    margin-top: 1rem;
    padding: 0.75rem;
    background: rgba(119, 51, 255, 0.08);
    border-left: 3px solid rgba(119, 51, 255, 0.4);
    border-radius: 0.375rem;
    font-size: 0.875rem;
}

.grounding-summary {
    cursor: pointer;
    color: var(--accent-primary);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    user-select: none;
}

.grounding-summary:hover {
    text-decoration: underline;
}

.grounding-summary::marker {
    color: var(--accent-primary);
}

.grounding-details {
    margin-top: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.search-queries,
.citations,
.url-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.queries-label,
.citations-label {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.search-queries ul,
.citations ul {
    margin: 0;
    padding-left: 1.5rem;
    list-style-type: disc;
}

.search-queries li {
    margin: 0.25rem 0;
    color: var(--text-secondary);
}

.citation-item {
    margin: 0.25rem 0;
    word-break: break-word;
}

.citation-link {
    color: var(--accent-primary);
    text-decoration: none;
    font-weight: 600;
    border-bottom: 1px dotted var(--accent-primary);
}

.citation-link:hover {
    text-decoration: underline;
    background: rgba(119, 51, 255, 0.1);
    border-radius: 0.2rem;
    padding: 0.1rem 0.2rem;
}

.url-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: rgba(0, 0, 0, 0.03);
    border-radius: 0.25rem;
    word-break: break-all;
}

.url-link {
    flex: 1;
    color: var(--accent-primary);
    text-decoration: none;
    font-weight: 600;
    border-bottom: 1px dotted var(--accent-primary);
}

.url-link:hover {
    text-decoration: underline;
}

.url-status {
    flex-shrink: 0;
    font-weight: 700;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
}

.url-status.url_retrieval_status_success {
    background: rgba(34, 197, 94, 0.2);
    color: rgb(22, 163, 74);
}

.url-status.url_retrieval_status_failed,
.url-status.unknown {
    background: rgba(239, 68, 68, 0.2);
    color: rgb(220, 38, 38);
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .streaming-word {
        animation-duration: 0.3s;
        margin-right: 0.2em;
        filter: blur(2px);
    }

    .activity-icon {
        width: 36px;
        height: 36px;
        font-size: 1.25rem;
    }

    .activity-indicator-enhanced {
        padding: 0.75rem;
        gap: 0.5rem;
    }
}
</style>
