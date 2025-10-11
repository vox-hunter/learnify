import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useChatStore = defineStore('chat', () => {
  // State
  const chats = ref([])
  const currentChat = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const sortedChats = computed(() => {
    return [...chats.value].sort((a, b) => {
      return new Date(b.updated_at) - new Date(a.updated_at)
    })
  })

  const activeChatId = computed(() => currentChat.value?.chat_id || null)

  // Actions
  async function loadUserChats(username) {
    if (!username) return

    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/chats/user/${username}`)
      
      if (response.data && response.data.chats) {
        chats.value = response.data.chats
      }
    } catch (err) {
      console.error('Failed to load chats:', err)
      error.value = err.response?.data?.detail || 'Failed to load chats'
      chats.value = []
    } finally {
      loading.value = false
    }
  }

  async function loadChat(chatId) {
    if (!chatId) return null

    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/chats/${chatId}`)
      
      if (response.data) {
        currentChat.value = response.data
        return response.data
      }
    } catch (err) {
      console.error('Failed to load chat:', err)
      error.value = err.response?.data?.detail || 'Failed to load chat'
      return null
    } finally {
      loading.value = false
    }
  }

  async function createChat(username, title = null, courseId = null) {
    if (!username) return null

    loading.value = true
    error.value = null

    try {
      const formData = new FormData()
      formData.append('username', username)
      if (title) formData.append('title', title)
      if (courseId) formData.append('course_id', courseId)

      const response = await api.post('/chats/create', formData)
      
      if (response.data) {
        currentChat.value = response.data
        // Add to chats list if not already there
        const exists = chats.value.find(c => c.chat_id === response.data.chat_id)
        if (!exists) {
          chats.value.unshift(response.data)
        }
        return response.data
      }
    } catch (err) {
      console.error('Failed to create chat:', err)
      error.value = err.response?.data?.detail || 'Failed to create chat'
      return null
    } finally {
      loading.value = false
    }
  }

  async function getCourseChat(username, courseId) {
    if (!username || !courseId) return null

    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/chats/course/${username}/${courseId}`)
      
      if (response.data) {
        currentChat.value = response.data
        // Update or add to chats list
        const index = chats.value.findIndex(c => c.chat_id === response.data.chat_id)
        if (index >= 0) {
          chats.value[index] = response.data
        } else {
          chats.value.unshift(response.data)
        }
        return response.data
      }
    } catch (err) {
      console.error('Failed to get course chat:', err)
      error.value = err.response?.data?.detail || 'Failed to get course chat'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateChatTitle(chatId, newTitle) {
    if (!chatId || !newTitle) return false

    try {
      const formData = new FormData()
      formData.append('title', newTitle)

      const response = await api.put(`/chats/${chatId}/title`, formData)
      
      if (response.data?.success) {
        // Update in current chat
        if (currentChat.value?.chat_id === chatId) {
          currentChat.value.title = newTitle
        }
        // Update in chats list
        const index = chats.value.findIndex(c => c.chat_id === chatId)
        if (index >= 0) {
          chats.value[index].title = newTitle
        }
        return true
      }
      return false
    } catch (err) {
      console.error('Failed to update chat title:', err)
      return false
    }
  }

  async function deleteChat(chatId, username) {
    if (!chatId || !username) return false

    try {
      const formData = new FormData()
      formData.append('username', username)

      const response = await api.delete(`/chats/${chatId}`, { data: formData })
      
      if (response.data?.success) {
        // Remove from chats list
        chats.value = chats.value.filter(c => c.chat_id !== chatId)
        // Clear current chat if it's the one being deleted
        if (currentChat.value?.chat_id === chatId) {
          currentChat.value = null
        }
        return true
      }
      return false
    } catch (err) {
      console.error('Failed to delete chat:', err)
      return false
    }
  }

  function setCurrentChat(chat) {
    currentChat.value = chat
  }

  function clearCurrentChat() {
    currentChat.value = null
  }

  function updateChatMessages(chatId, messages) {
    // Update messages in current chat
    if (currentChat.value?.chat_id === chatId) {
      currentChat.value.messages = messages
      currentChat.value.updated_at = new Date().toISOString()
    }

    // Update in chats list
    const index = chats.value.findIndex(c => c.chat_id === chatId)
    if (index >= 0) {
      chats.value[index].messages = messages
      chats.value[index].updated_at = new Date().toISOString()
    }
  }

  return {
    // State
    chats,
    currentChat,
    loading,
    error,

    // Getters
    sortedChats,
    activeChatId,

    // Actions
    loadUserChats,
    loadChat,
    createChat,
    getCourseChat,
    updateChatTitle,
    deleteChat,
    setCurrentChat,
    clearCurrentChat,
    updateChatMessages
  }
})
