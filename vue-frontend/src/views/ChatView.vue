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

        <div
          v-if="reachedNgLimit"
          class="ng-limit-block"
        >
          <div
            class="danger-warning"
            style="margin-bottom:0.75rem"
          >
            <strong>You've reached the free chat limit.</strong>
            <p style="margin:0.25rem 0 0; color:var(--text-muted)">
              Link your Google account to continue
              chatting with your personal quota, or visit the Danger Zone in your account.
            </p>
          </div>
          <div class="input-group">
            <button
              class="btn btn-primary"
              @click.prevent="goToDangerZone"
            >
              Go to Danger Zone
            </button>
            <button
              class="btn"
              style="margin-left:0.5rem"
              @click.prevent="linkGoogleAccount"
            >
              Link Google
              Account
            </button>
          </div>
        </div>
        <div
          v-else
          class="input-group"
        >
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

          <button
            class="input-btn url-btn"
            :class="{ active: showUrlInput }"
            title="Add URL"
            @click="toggleUrlInput"
          >
            🔗
          </button>

          <input
            v-if="showUrlInput"
            v-model="urlInput"
            type="url"
            class="url-input"
            placeholder="Paste URL here..."
            @keydown.enter="handleUrlSubmit"
            @keydown.esc="showUrlInput = false"
          >

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
import { useChatStore } from '../stores/chat'
import api from '../services/api'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

export default {
    name: 'ChatView',
    setup() {
        // ...existing code...
        // Watch for clearing current chat (New Chat) after stores are initialized
        nextTick(() => {
            watch(() => chatStore.currentChat, (newVal) => {
                if (newVal === null) {
                    chatId.value = null
                    sessionId.value = null
                    messages.value = []
                    resumedWithHistory.value = false
                }
            })
        })
        const router = useRouter()
        const route = useRoute()
        const courseStore = useCourseStore()
        const authStore = useAuthStore()
        const chatStore = useChatStore()

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
        const chatId = ref(null)
        const resumedWithHistory = ref(false)  // Track if we've injected history for resume

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

        const nonGoogleCount = ref(authStore.user?.username ? getNgCount(authStore.user.username) : 0)
        const reachedNgLimit = computed(() => {
            // Skip limit if user is Google-linked
            if (authStore.user?.isGoogleUser) return false
            return !!authStore.user && nonGoogleCount.value >= 6
        })

        // Clear the counter when a user becomes Google-linked and keep in sync on user change
        watch(() => authStore.user, (newUser) => {
            if (newUser?.isGoogleUser && newUser.username) {
                localStorage.removeItem(ngStorageKey(newUser.username))
                nonGoogleCount.value = 0
            }
            if (newUser?.username) {
                nonGoogleCount.value = getNgCount(newUser.username)
            }
        }, { deep: true })

        // Watch messages and typeset math when they change
        watch(messages, () => {
            typesetMath()
        }, { deep: true })

        // Load chat by ID helper (must be defined before watcher)
        const loadChatById = async (id) => {
            if (!id) return

            try {
                const chat = await chatStore.loadChat(id)
                if (chat) {
                    chatId.value = chat.chat_id
                    sessionId.value = chat.session_id || null
                    // Convert MongoDB messages to UI format
                    messages.value = (chat.messages || []).map(msg => ({
                        role: msg.role,
                        text: msg.text,
                        timestamp: new Date(msg.timestamp).getTime(),
                        attachment: msg.attachment || null
                    }))
                    resumedWithHistory.value = false  // Reset on load
                    scrollToBottom()
                }
            } catch (err) {
                console.error('Failed to load chat:', err)
            }
        }

        // Watch for chat_id changes in route query
        const chatIdWatcher = async (newChatId) => {
            if (newChatId && newChatId !== chatId.value) {
                // Only load if chat_id is non-empty and not null
                if (typeof newChatId === 'string' && newChatId.trim() !== '') {
                    await loadChatById(newChatId)
                } else {
                    // Reset state if chat_id is missing or empty
                    chatId.value = null
                    sessionId.value = null
                    messages.value = []
                    resumedWithHistory.value = false
                }
            }
        }
        watch(() => route.query.chat_id, chatIdWatcher, { immediate: true })

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
                const resp = await api.get('/auth/google/url')
                if (resp.data?.url) {
                    window.location.href = resp.data.url
                } else {
                    error.value = 'Failed to get Google login URL.'
                }
            } catch (e) {
                error.value = 'Failed to get Google login URL.'
            }
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

        // ...existing code...

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

        const goToDangerZone = () => {
            router.push({ path: '/account', query: { tab: 'danger' } })
        }

        const sendMessage = async () => {
            if (!canSend.value) return

            const userMessage = messageInput.value.trim()
            const url = urlInput.value.trim()
            const file = selectedFile.value

            // Check if this is a resumed chat and we need to inject history
            let messageToSend = userMessage || 'Please analyze this content'
            if (chatId.value && !resumedWithHistory.value && messages.value.length > 0) {
                // Inject history context only once when resuming
                const historyContext = messages.value.slice(0, -1).map(msg => 
                    `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.text}`
                ).join('\n')
                
                messageToSend = `[Previous conversation context for continuity - do not acknowledge this directly]:\n${historyContext}\n\n[Current message]: ${userMessage || 'Please analyze this content'}`
                resumedWithHistory.value = true
            }

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
                formData.append('message', messageToSend)
                if (sessionId.value) formData.append('session_id', sessionId.value)
                if (chatId.value) formData.append('chat_id', chatId.value)
                if (file) formData.append('file', file)
                if (url) formData.append('url', url)
                if (authStore.user?.username) formData.append('username', authStore.user.username)

                const response = await api.post('/chat/message', formData, { headers: { 'Content-Type': 'multipart/form-data' } })

                if (!response.data.success) throw new Error(response.data.error || 'Failed to get response')

                sessionId.value = response.data.session_id
                chatId.value = response.data.chat_id || chatId.value

                // Update chat store with new chat ID if created
                if (response.data.chat_id && authStore.user?.username) {
                    await chatStore.loadUserChats(authStore.user.username)
                }

                // Detect course generation (raw JSON)
                if (response.data.is_course && response.data.course_data) {
                    const courseTitle = response.data.course_data.course_title
                    const saveResult = await courseStore.saveCourse(response.data.course_data.sections, courseTitle)
                    if (saveResult.success) {
                        // Show clickable link instead of raw JSON
                        messages.value.push({
                            role: 'system',
                            text: `<a href='/course/${saveResult.courseId}' class='course-link' style='color:var(--accent-primary);text-decoration:underline;'>(${courseTitle}) generated</a>`,
                            timestamp: Date.now()
                        })
                        scrollToBottom()
                        setTimeout(() => router.push(`/course/${saveResult.courseId}`), 1200)
                    } else {
                        throw new Error(saveResult.error || 'Failed to save course')
                    }
                } else {
                    // AI reply
                    messages.value.push({ role: 'assistant', text: response.data.reply, timestamp: Date.now() })

                    // If this is the first AI reply, auto-generate chat name
                    if (messages.value.length === 2 && chatId.value) {
                        // Use first 8 words of reply as chat name
                        const firstReply = response.data.reply
                        const chatName = firstReply.split(' ').slice(0, 8).join(' ') + (firstReply.length > 60 ? '...' : '')
                        await chatStore.updateChatTitle(chatId.value, chatName)
                    }
                }

                // Update chat store messages
                if (chatId.value) {
                    chatStore.updateChatMessages(chatId.value, messages.value)
                }

                scrollToBottom()
            } catch (err) {
                console.error('Error sending message:', err)
                error.value = err.response?.data?.detail || err.message || 'Failed to send message'
                messages.value.pop()
            } finally {
                isLoading.value = false
            }
        }

        onMounted(() => {
            // Check for chat_id in URL query
            if (route.query.chat_id && typeof route.query.chat_id === 'string' && route.query.chat_id.trim() !== '') {
                loadChatById(route.query.chat_id)
            } else {
                // Reset state if chat_id is missing or empty
                chatId.value = null
                sessionId.value = null
                messages.value = []
                resumedWithHistory.value = false
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
            reachedNgLimit,
            goToDangerZone
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
    flex-shrink: 0;
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
}

.send-btn:hover:not(:disabled) {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 20px rgba(119, 51, 255, 0.4);
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
