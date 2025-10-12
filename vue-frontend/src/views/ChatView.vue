<template>
  <div class="chat-view">
    <div class="container">
      <div
        ref="chatFeed"
        class="chat-feed"
      >
        <!-- Welcome Message -->
        <div
          v-if="messages.length === 0"
          class="welcome-message"
        >
          <div class="welcome-icon">
            ✨
          </div>
          <h2>Learning starts when you start talking.</h2>
          <p>Ask Stitch anything, upload notes, or paste a URL to get started.</p>
          <div class="example-prompts">
            <button
              v-for="(example, i) in examplePrompts"
              :key="i"
              class="example-prompt"
              @click="sendExamplePrompt(example)"
            >
              {{ example }}
            </button>
          </div>
        </div>

        <!-- Message List -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message', 'wrap']"
        >
          <div class="message-avatar">
            <span v-if="msg.role === 'user'">👤</span>
            <span v-else>
              <img
                src="/STITCH.png"
                alt="Stitch Logo"
                class="stitch-logo"
                style="width:2em;height:2em;vertical-align:middle;"
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
                style="width:2em;height:2em;vertical-align:middle;"
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
      <div class="chat-input-container">
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

        <div class="input-group">
          <label
            class="input-btn file-btn"
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
            class="url-input"
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
            class="message-input"
            placeholder="Ask Stitch or upload notes..."
            :disabled="isLoading"
            @keydown.enter="sendMessage"
          >

          <button
            v-if="!reachedNgLimit"
            class="input-btn send-btn"
            :disabled="!canSend || isLoading"
            @click="sendMessage"
          >
            {{
              isLoading ? '⏳' : '🚀' }}
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
.chat-view {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
}

.container {
    flex: 1;
    display: flex;
    flex-direction: column;
    /* stretch to fill available space so chat occupies full width */
    max-width: none;
    margin: 0;
    width: 100%;
    padding: 0;
    height: 100vh;
}

.chat-feed {
    flex: 1;
    /* only show vertical scrollbar when content overflows; never show horizontal */
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1.25rem 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.welcome-message {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-secondary);
    margin: auto 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.welcome-icon {
    font-size: 3.2rem;
    /* slightly smaller sparkle */
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 14px rgba(119, 51, 255, 0.25));
}

.welcome-message h2 {
    color: var(--text-primary);
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.welcome-message p {
    font-size: 1rem;
    max-width: 420px;
}

.example-prompts {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 3rem;
    max-width: 500px;
    width: 100%;
}

.example-prompt {
    padding: 0.75rem 1rem;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 1rem;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.25s;
    text-align: left;
    font-size: 0.95rem;
    box-shadow: 0 2px 8px var(--shadow-color);
}

.example-prompt:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-primary);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px var(--shadow-color);
}

.message {
    display: flex;
    gap: 1rem;
    animation: slideIn 0.3s ease;
    max-width: 100%;
    align-items: flex-start;
    /* ensure avatar and bubble align at top, avoid vertical stretch */
    width: 100%;
    /* allow margin-left:auto on user messages to push row to the right */
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.user-message {
    flex-direction: row-reverse;
    margin-left: auto;
}

.ai-message {
    margin-right: auto;
}

.message-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
    box-shadow: none;
}

.user-message .message-avatar {
    background: linear-gradient(135deg, #00d4ff, #7733ff);
}

.message-content {
    /* Make this a flex item that can shrink to avoid overflow in a flex row */
    display: block;
    flex: 1 1 auto;
    min-width: 0; /* critical: allow text to wrap instead of forcing overflow */
}

/* AI messages occupy remaining width of the row */
.ai-message .message-content {
    flex: 1 1 auto;
    min-width: 0;
}

.user-message .message-content {
    /* Keep user messages constrained, but shrink-to-fit content */
    flex: 0 1 auto; /* don't grow to fill the row */
    max-width: 70%;
}

.user-message .message-text {
    /* Balanced padding and left-aligned text inside the right-side bubble */
    text-align: left;
}

.ai-message .message-text {
    /* AI messages use full width with no extra padding for LaTeX */
    text-align: left;
    padding: 0.5rem 0;
}

.message-header {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.user-message .message-header {
    flex-direction: row-reverse;
}

.message-sender {
    font-weight: 600;
    color: var(--text-primary);
}

.message-time {
    color: var(--text-muted);
}

.message-text {
    line-height: 1.6;
    font-size: 0.95rem;
    color: var(--text-primary);
    white-space: normal; /* ensure standard wrapping */
    /* Ensure long words/URLs wrap instead of causing horizontal scroll */
    overflow-wrap: anywhere;
    word-break: break-word;
    max-width: 100%;
    overflow-x: hidden;
}

/* AI: no bubble, just aligned text */
.ai-message .message-text {
    padding: 0;
    background: transparent;
    border: none;
    box-shadow: none;
}

.user-message .message-text {
    /* Keep bubble styling for user messages */
    padding: 1rem;
    background: linear-gradient(135deg, #7733ff, #00d4ff);
    color: white;
    border: none;
    border-radius: 1.25rem;
    border-top-right-radius: 0.25rem;
    box-shadow: 0 2px 8px var(--shadow-color);
    display: inline-block; /* shrink bubble to content */
    max-width: 100%;
}

.message-attachment {
    margin-top: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--bg-tertiary);
    border-radius: 0.5rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
}

.attachment-icon {
    font-size: 1rem;
}

.typing-indicator {
    display: flex;
    gap: 0.35rem;
    padding: 1.25rem;
}

.typing-indicator span {
    width: 10px;
    height: 10px;
    background: var(--text-muted);
    border-radius: 50%;
    animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {

    0%,
    60%,
    100% {
        transform: translateY(0);
        opacity: 0.5;
    }

    30% {
        transform: translateY(-10px);
        opacity: 1;
    }
}

.chat-input-container {
    padding: 1.5rem;
    background: var(--card-bg);
    border-top: 1px solid var(--border-color);
}

.attachment-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.preview-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--bg-tertiary);
    border-radius: 0.75rem;
    font-size: 0.875rem;
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

.chat-error {
    padding: 0.75rem 1rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.75rem;
    color: #ef4444;
    margin-bottom: 0.75rem;
    font-size: 0.875rem;
}

.input-group {
    display: flex;
    gap: 0.6rem;
    align-items: center;
    max-width: 100%;
    width: 100%;
    box-sizing: border-box;
    /* prevent send button from being cut off on devices with notches */
    padding-right: max(env(safe-area-inset-right), 0.75rem);
    flex-wrap: nowrap; /* force single row */
}

.input-btn {
    width: 44px;
    height: 44px;
    border-radius: 0.9rem;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 1.1rem;
    cursor: pointer;
    transition: all 0.18s;
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
}

.input-btn:hover:not(:disabled) {
    background: var(--card-bg);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}

.input-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.input-btn.active {
    background: var(--accent-primary);
    color: white;
    border-color: var(--accent-primary);
}

.message-input,
.url-input {
    flex: 1;
    padding: 0.85rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: 1rem;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 0.95rem;
    transition: all 0.18s;
    min-width: 0; /* allow input to shrink properly inside flex */
}

.message-input:focus,
.url-input:focus {
    outline: none;
    border-color: var(--accent-primary);
    background: var(--card-bg);
    box-shadow: 0 0 0 3px rgba(119, 51, 255, 0.1);
}

.send-btn {
    background: linear-gradient(135deg, #7733ff, #00d4ff);
    color: white;
    border: none;
    box-shadow: 0 4px 15px rgba(119, 51, 255, 0.3);
    flex: 0 0 auto;
    min-width: 44px;
}

.send-btn:hover:not(:disabled) {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 20px rgba(119, 51, 255, 0.4);
}

.link-google-btn {
    flex: 1;
    padding: 0.85rem 1.5rem;
    border: none;
    border-radius: 1rem;
    background: linear-gradient(135deg, #4285f4, #34a853);
    color: white;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.link-google-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
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

@media (max-width: 768px) {
    .container {
        max-width: 100%;
    }

    .welcome-message {
        padding: 2rem 1rem;
    }

    .welcome-icon {
        font-size: 2.6rem;
    }

    .welcome-message h2 {
        font-size: 1.25rem;
    }

    .welcome-message p {
        font-size: 0.95rem;
    }

    .message-content {
        max-width: 95%;
    }

    .input-btn {
        width: 38px;
        height: 38px;
        font-size: 0.95rem;
    }

    .chat-input-container {
        padding: 1rem;
    }
}

/* Chat-feed scrollbar: hide by default on some platforms, show thin when needed */
.chat-feed {
    -ms-overflow-style: auto;
    /* IE/Edge */
    scrollbar-width: thin;
    /* Firefox */
}

.chat-feed::-webkit-scrollbar {
    width: 8px;
}

.chat-feed::-webkit-scrollbar-track {
    background: transparent;
}

.chat-feed::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.12);
    border-radius: 6px;
}

.chat-feed::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.2);
}
</style>
