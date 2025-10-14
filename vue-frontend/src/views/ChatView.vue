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
            alt="Stitch"
            class="logo-image"
          >
        </div>
        <h1 class="brand-title">
          What's new, Vox?
        </h1>
        <p class="brand-subtitle">
          Start a conversation with Stitch
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
          <div class="message-avatar">
            <span v-if="msg.role === 'user'">👤</span>
            <span v-else>
              <img
                src="/STITCH.png"
                alt="Stitch Logo"
                class="stitch-logo"
              >
            </span>
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">{{ msg.role === 'user' ? 'You' : 'Stitch' }}</span>
              <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
            </div>
            <div
              class="message-text"
              v-html="formatMessage(msg.text, msg.role)"
            />
            <div
              v-if="msg.attachment"
              class="message-attachment"
            >
              <span class="attachment-icon">📎</span>
              <span class="attachment-name">{{ msg.attachment.name }}</span>
            </div>
          </div>
        </div>

        <!-- Loading Indicator -->
        <div
          v-if="isLoading"
          class="message ai-message loading"
        >
          <div class="message-avatar">
            <span>
              <img
                src="/STITCH.png"
                alt="Stitch Logo"
                class="stitch-logo"
              >
            </span>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
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
            placeholder="How can I help you today?"
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
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCourseStore } from '../stores/course'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

export default {
    name: 'ChatView',
    setup() {
        const router = useRouter()
        const route = useRoute()
        const courseStore = useCourseStore()
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

        const examplePrompts = [
            'Create a course about Python basics',
            'Help me understand quantum physics',
            'Summarize this document'
        ]

        const canSend = computed(() => {
            return (messageInput.value.trim() || selectedFile.value || urlInput.value) && !isLoading.value
        })

        const isAuthenticated = computed(() => !!authStore.user)

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

            // Simple Analytics event for send button click
            if (typeof window.saEvent === 'function') {
                window.saEvent('chat_send_clicked');
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

            scrollToBottom()

            try {
                if (!isAuthenticated.value) {
                    const fake = 'You need to be logged in to use AI features, if you want to try AI Generated course, checkout "library" for community generated courses.'
                    messages.value.push({ role: 'assistant', text: fake, timestamp: Date.now() })
                    isLoading.value = false
                    scrollToBottom()
                    return
                }

                const formData = new FormData()
                formData.append('message', userMessage || 'Please analyze this content')
                if (sessionId.value) formData.append('session_id', sessionId.value)
                if (file) formData.append('file', file)
                if (url) formData.append('url', url)
                if (authStore.user?.username) formData.append('username', authStore.user.username)

                const response = await api.post('/chat/message', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
                console.log('Chat API response:', response)

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
                } else {
                    if (response.data.reply && response.data.reply.trim()) {
                        messages.value.push({ role: 'assistant', text: response.data.reply, timestamp: Date.now() })
                    } else {
                        messages.value.push({ role: 'system', text: '⚠️ No reply received from AI. Please check backend logs or try again later.', timestamp: Date.now() })
                    }
                }

                scrollToBottom()
            } catch (err) {
                console.error('Error sending message:', err)
                error.value = err.response?.data?.detail || err.message || 'Failed to send message'
                messages.value.pop()
                messages.value.push({ role: 'system', text: `⚠️ Error: ${error.value}`, timestamp: Date.now() })
                scrollToBottom()
            } finally {
                isLoading.value = false
            }
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

        // Watch messages and save to localStorage whenever they change
        watch(messages, () => {
            saveChatMessages()
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
            handleFileSelect,
            removeFile,
            toggleUrlInput,
            handleUrlSubmit,
            removeUrl,
            sendExamplePrompt,
            sendMessage,
            showGoogleLinkButton,
            linkGoogleAccount,
            reachedNgLimit
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
    padding: 0;
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
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
    background: var(--bg-tertiary);
    border: 2px solid var(--border-color);
}

.user-message .message-avatar {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    border: none;
}

.stitch-logo {
    width: 24px;
    height: 24px;
    object-fit: contain;
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
</style>
