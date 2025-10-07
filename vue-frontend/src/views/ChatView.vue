<template>
    <div class="chat-view">
        <div class="container">
            <!-- Chat Messages Feed -->
            <div ref="chatFeed" class="chat-feed">
                <!-- Welcome Message -->
                <div v-if="messages.length === 0" class="welcome-message">
                    <div class="welcome-icon">✨</div>
                    <h2>What do you want to learn today?</h2>
                    <p>Ask AI Loom anything, upload notes, or paste a URL to get started.</p>
                    <div class="example-prompts">
                        <button v-for="(example, index) in examplePrompts" :key="index" class="example-prompt"
                            @click="sendExamplePrompt(example)">
                            {{ example }}
                        </button>
                    </div>
                </div>

                <!-- Message List -->
                <div v-for="(msg, index) in messages" :key="index"
                    :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']">
                    <div class="message-avatar">
                        <span v-if="msg.role === 'user'">👤</span>
                        <span v-else>🤖</span>
                    </div>
                    <div class="message-content">
                        <div class="message-header">
                            <span class="message-sender">{{ msg.role === 'user' ? 'You' : 'AI Loom' }}</span>
                            <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
                        </div>
                        <div class="message-text" v-html="formatMessage(msg.text)" />
                        <!-- Attachments -->
                        <div v-if="msg.attachment" class="message-attachment">
                            <span class="attachment-icon">📎</span>
                            <span class="attachment-name">{{ msg.attachment.name }}</span>
                        </div>
                    </div>
                </div>

                <!-- Loading Indicator -->
                <div v-if="isLoading" class="message ai-message loading">
                    <div class="message-avatar">
                        <span>🤖</span>
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
                <!-- File/URL Attachment Preview -->
                <div v-if="selectedFile || urlInput" class="attachment-preview">
                    <div v-if="selectedFile" class="preview-item">
                        <span class="preview-icon">📄</span>
                        <span class="preview-name">{{ selectedFile.name }}</span>
                        <button class="preview-remove" @click="removeFile">×</button>
                    </div>
                    <div v-if="urlInput" class="preview-item">
                        <span class="preview-icon">🔗</span>
                        <span class="preview-name">{{ urlInput }}</span>
                        <button class="preview-remove" @click="removeUrl">×</button>
                    </div>
                </div>

                <!-- Error Message -->
                <div v-if="error" class="chat-error">
                    {{ error }}
                </div>

                <!-- Input Group -->
                <div class="input-group">
                    <!-- File Upload Button -->
                    <label class="input-btn file-btn" title="Upload file">
                        <input ref="fileInput" type="file" accept=".pdf,.docx,.doc,.txt,.pptx,.ppt,.xlsx,.xls,.md,.rtf"
                            hidden @change="handleFileSelect">
                        📎
                    </label>

                    <!-- URL Input Toggle -->
                    <button class="input-btn url-btn" :class="{ active: showUrlInput }" title="Add URL"
                        @click="toggleUrlInput">
                        🔗
                    </button>

                    <!-- URL Input Field (conditionally shown) -->
                    <input v-if="showUrlInput" v-model="urlInput" type="url" class="url-input"
                        placeholder="Paste URL here..." @keydown.enter="handleUrlSubmit"
                        @keydown.esc="showUrlInput = false">

                    <!-- Message Input -->
                    <input v-else v-model="messageInput" type="text" class="message-input"
                        placeholder="Ask AI Loom or upload notes..." @keydown.enter="sendMessage" :disabled="isLoading">

                    <!-- Send Button -->
                    <button class="input-btn send-btn" :disabled="!canSend || isLoading" @click="sendMessage">
                        {{ isLoading ? '⏳' : '🚀' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

export default {
    name: 'ChatView',
    setup() {
        const router = useRouter()
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

        // Example prompts for new users
        const examplePrompts = [
            'Create a course about Python basics',
            'Help me understand quantum physics',
            'Summarize this document'
        ]

        // Computed
        const canSend = computed(() => {
            return (messageInput.value.trim() || selectedFile.value || urlInput.value) && !isLoading.value
        })

        // Whether current user is authenticated (guest => false)
        const isAuthenticated = computed(() => !!authStore.user)

        // Methods
        const scrollToBottom = () => {
            nextTick(() => {
                if (chatFeed.value) {
                    chatFeed.value.scrollTop = chatFeed.value.scrollHeight
                }
            })
        }

        const formatTime = (timestamp) => {
            const date = new Date(timestamp)
            return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
        }

        // Initialize markdown-it with common options
        const md = new MarkdownIt({
            html: false,
            linkify: true,
            typographer: true
        })

        const formatMessage = (text, role = 'assistant') => {
            if (!text) return ''

            // Convert reference-style citation links like [1](https://...)
            const withCitations = text.replace(/\[(\d+)\]\((https?:\/\/[^)]+)\)/g, '[$1]($2)')

            if (role === 'assistant') {
                // Render markdown to HTML and sanitize
                const rendered = md.render(withCitations)
                const clean = DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } })
                return clean
            }

            // For user messages, keep simple escaping: replace newlines with <br>
            return withCitations.replace(/\n/g, '<br>')
        }

        const handleFileSelect = (event) => {
            const file = event.target.files[0]
            if (file) {
                // Validate file size (20MB limit)
                if (file.size > 20 * 1024 * 1024) {
                    error.value = 'File size must be less than 20MB'
                    return
                }
                selectedFile.value = file
                error.value = null
            }
        }

        const removeFile = () => {
            selectedFile.value = null
            if (fileInput.value) {
                fileInput.value.value = ''
            }
        }

        const toggleUrlInput = () => {
            showUrlInput.value = !showUrlInput.value
            if (showUrlInput.value) {
                messageInput.value = ''
            }
        }

        const handleUrlSubmit = () => {
            showUrlInput.value = false
        }

        const removeUrl = () => {
            urlInput.value = ''
        }

        const sendExamplePrompt = (prompt) => {
            messageInput.value = prompt
            sendMessage()
        }

        const sendMessage = async () => {
            if (!canSend.value) return

            const userMessage = messageInput.value.trim()
            const url = urlInput.value.trim()
            const file = selectedFile.value

            // Add user message to chat
            const userMsg = {
                role: 'user',
                text: userMessage || (url ? `Analyzing URL: ${url}` : 'Uploaded file'),
                timestamp: Date.now(),
                attachment: file ? { name: file.name, type: file.type } : null
            }
            messages.value.push(userMsg)

            // Clear inputs
            messageInput.value = ''
            urlInput.value = ''
            removeFile()
            showUrlInput.value = false
            error.value = null
            isLoading.value = true

            scrollToBottom()

            try {
                // If user is not authenticated, immediately return the fake assistant reply
                if (!isAuthenticated.value) {
                    const fakeReply = 'You need to be logged in to use AI features, if you want to try AI Generated course, checkout "library" for community generated courses.'
                    // Add assistant message
                    messages.value.push({ role: 'assistant', text: fakeReply, timestamp: Date.now() })
                    isLoading.value = false
                    scrollToBottom()
                    return
                }

                // Prepare form data for API request
                const formData = new FormData()
                formData.append('message', userMessage || 'Please analyze this content')

                if (sessionId.value) {
                    formData.append('session_id', sessionId.value)
                }

                if (file) {
                    formData.append('file', file)
                }

                if (url) {
                    formData.append('url', url)
                }

                // Always send username as a form field for backend auth
                if (authStore.user && authStore.user.username) {
                    formData.append('username', authStore.user.username)
                }

                // Send to backend chat endpoint
                const response = await api.post('/chat/message', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                })

                if (response.data.success) {
                    // Store session ID for multi-turn conversation
                    sessionId.value = response.data.session_id

                    // Save to localStorage for persistence
                    localStorage.setItem('chat_session_id', sessionId.value)

                    // Debug logging
                    console.log('[ChatView] Response:', {
                        is_course: response.data.is_course,
                        has_course_data: !!response.data.course_data,
                        reply_length: response.data.reply?.length
                    })

                    // Check if this is a course generation response
                    if (response.data.is_course && response.data.course_data) {
                        // AI generated a course - save it and redirect
                        console.log('[ChatView] Course detected, saving...')
                        console.log('[ChatView] Course data:', response.data.course_data)

                        try {
                            const saveResult = await courseStore.saveCourse(
                                response.data.course_data.sections,
                                response.data.course_data.course_title
                            )

                            if (saveResult.success) {
                                // Add a system message to chat feed
                                messages.value.push({
                                    role: 'system',
                                    text: `🎓 Course "${response.data.course_data.course_title}" created successfully! Redirecting...`,
                                    timestamp: Date.now()
                                })

                                scrollToBottom()

                                // Redirect to the course after a brief delay
                                setTimeout(() => {
                                    router.push(`/course/${saveResult.courseId}`)
                                }, 1500)
                            } else {
                                throw new Error(saveResult.error || 'Failed to save course')
                            }
                        } catch (saveErr) {
                            console.error('[ChatView] Error saving course:', saveErr)
                            error.value = 'Course generated but failed to save: ' + saveErr.message
                        }
                    } else {
                        // Normal conversation response
                        messages.value.push({
                            role: 'assistant',
                            text: response.data.reply,
                            timestamp: Date.now()
                        })
                    }

                    scrollToBottom()
                } else {
                    throw new Error(response.data.error || 'Failed to get response')
                }
            } catch (err) {
                console.error('Error sending message:', err)
                error.value = err.response?.data?.detail || err.message || 'Failed to send message'

                // Remove user message on error
                messages.value.pop()
            } finally {
                isLoading.value = false
            }
        }

        // Load session ID on mount
        onMounted(() => {
            const savedSessionId = localStorage.getItem('chat_session_id')
            if (savedSessionId) {
                sessionId.value = savedSessionId
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
            sendMessage
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
    /* only show scrollbar when content overflows */
    overflow-y: auto;
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
    background: linear-gradient(135deg, #7733ff, #00d4ff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
    box-shadow: 0 3px 10px rgba(119, 51, 255, 0.18);
}

.user-message .message-avatar {
    background: linear-gradient(135deg, #00d4ff, #7733ff);
}

.message-content {
    /* Shrink-to-fit container for the message bubble. It won't grow unnecessarily, but will cap at a percentage of the row. */
    display: inline-block;
    flex: 0 0 auto;
    /* do not grow; size to content */
    max-width: 70%;
    vertical-align: top;
}

.user-message .message-text {
    /* Balanced padding and left-aligned text inside the right-side bubble */
    padding: 0.6rem 0.9rem;
    text-align: left;
}

.ai-message .message-text {
    /* ensure AI bubbles use similar balanced padding */
    padding: 0.9rem 1rem;
    text-align: left;
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
    padding: 1rem;
    background: var(--card-bg);
    border-radius: 1.25rem;
    color: var(--text-primary);
    line-height: 1.6;
    font-size: 0.95rem;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 8px var(--shadow-color);
}

.ai-message .message-text {
    border-top-left-radius: 0.25rem;
}

.user-message .message-text {
    background: linear-gradient(135deg, #7733ff, #00d4ff);
    color: white;
    border: none;
    border-top-right-radius: 0.25rem;
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
    margin: 0.75rem 0;
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
        max-width: 85%;
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
