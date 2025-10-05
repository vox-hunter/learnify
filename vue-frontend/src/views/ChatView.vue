<template>
    <div class="chat-view">
        <div class="container">
            <!-- Header -->
            <div class="chat-header">
                <div class="hero-logo">
                    <img src="/logo.png" alt="AI Loom" class="logo">
                </div>
                <h1 class="chat-title">AI Loom Chat</h1>
                <p class="chat-subtitle">
                    Chat with AI to create courses, analyze documents, or get help with learning
                </p>
            </div>

            <!-- Chat Messages Feed -->
            <div ref="chatFeed" class="chat-feed">
                <!-- Welcome Message -->
                <div v-if="messages.length === 0" class="welcome-message">
                    <div class="welcome-icon">💬</div>
                    <h2>Start a Conversation</h2>
                    <p>Upload a document, paste a URL, or just ask me anything!</p>
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
                        placeholder="Type a message..." @keydown.enter="sendMessage" :disabled="isLoading">

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
import api from '../services/api'

export default {
    name: 'ChatView',
    setup() {
        const router = useRouter()
        const courseStore = useCourseStore()

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

        const formatMessage = (text) => {
            // Convert markdown-style links to HTML
            return text
                .replace(/\[(\d+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" class="citation-link">[$1]</a>')
                .replace(/\n/g, '<br>')
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
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    padding: 0;
    height: 100vh;
}

.chat-header {
    text-align: center;
    padding: 2rem 1rem 1rem;
    background: var(--card-bg);
    border-bottom: 1px solid var(--border-color);
}

.hero-logo {
    margin-bottom: 1rem;
}

.logo {
    height: 60px;
    width: auto;
    filter: drop-shadow(0 0 10px rgba(6, 182, 212, 0.3));
}

.chat-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.chat-subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
}

.chat-feed {
    flex: 1;
    overflow-y: auto;
    padding: 2rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.welcome-message {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--text-secondary);
}

.welcome-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.welcome-message h2 {
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.example-prompts {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 2rem;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
}

.example-prompt {
    padding: 0.75rem 1rem;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
}

.example-prompt:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}

.message {
    display: flex;
    gap: 1rem;
    animation: slideIn 0.3s ease;
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
}

.message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--accent-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    flex-shrink: 0;
}

.user-message .message-avatar {
    background: var(--accent-secondary);
}

.message-content {
    flex: 1;
    max-width: 70%;
}

.user-message .message-content {
    text-align: right;
}

.message-header {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 0.25rem;
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
    border-radius: 1rem;
    color: var(--text-primary);
    line-height: 1.6;
    border: 1px solid var(--border-color);
}

.user-message .message-text {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    color: white;
    border: none;
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
    gap: 0.25rem;
    padding: 1rem;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
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
    padding: 1rem;
    background: var(--card-bg);
    border-top: 1px solid var(--border-color);
}

.attachment-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.preview-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--bg-tertiary);
    border-radius: 0.5rem;
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
    border-radius: 0.5rem;
    color: #ef4444;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.input-group {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.input-btn {
    width: 48px;
    height: 48px;
    border-radius: 0.75rem;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
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
    padding: 0.75rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 1rem;
    transition: all 0.2s;
}

.message-input:focus,
.url-input:focus {
    outline: none;
    border-color: var(--accent-primary);
    background: var(--card-bg);
}

.send-btn {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    color: white;
    border: none;
}

.send-btn:hover:not(:disabled) {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 4px 15px rgba(119, 51, 255, 0.3);
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

@media (max-width: 768px) {
    .chat-header {
        padding: 1rem;
    }

    .chat-title {
        font-size: 1.5rem;
    }

    .message-content {
        max-width: 85%;
    }

    .input-btn {
        width: 40px;
        height: 40px;
        font-size: 1rem;
    }
}
</style>
