/**
 * Chat Streaming Service
 * Handles Server-Sent Events (SSE) for real-time chat streaming
 * with reconnection logic, exponential backoff, timeout detection,
 * and fallback to POST endpoint
 */

import { getApiBaseUrl } from './api'

// Configuration constants
const MAX_RETRY_ATTEMPTS = 3
const INITIAL_RETRY_DELAY = 1000
const MAX_RETRY_DELAY = 8000
const STREAM_TIMEOUT = 60000

/**
 * Stream a chat message using Server-Sent Events
 * @param {Object} options - Streaming options
 * @param {string} options.message - The user's message
 * @param {string|null} options.sessionId - Current session ID (optional)
 * @param {string|null} options.url - URL to analyze (optional)
 * @param {string|null} options.username - Username for authentication (optional)
 * @param {Function} options.onStatus - Callback for status updates
 * @param {Function} options.onChunk - Callback for text chunks
 * @param {Function} options.onCourse - Callback for course data
 * @param {Function} options.onFlashcard - Callback for flashcard data
 * @param {Function} options.onComplete - Callback for completion
 * @param {Function} options.onError - Callback for errors
 * @param {Function} options.onRetry - Callback for retry attempts (receives {retryCount, maxRetries})
 * @param {Function} options.onFallback - Callback when max retries exhausted, triggers fallback to POST
 * @returns {Object} Controller object with close(), getReadyState(), and getRetryState() methods
 */
export function streamChatMessage({
  message,
  sessionId,
  url,
  username,
  onStatus,
  onChunk,
  onCourse,
  onFlashcard,
  onComplete,
  onError,
  onRetry,
  onFallback
}) {
  // Build the streaming URL with query parameters
  const baseUrl = getApiBaseUrl()
  const params = new URLSearchParams()
  
  // Add non-null parameters
  if (message) params.append('message', message)
  if (sessionId) params.append('session_id', sessionId)
  if (url) params.append('url', url)
  if (username) params.append('username', username)
  
  const streamUrl = `${baseUrl}/chat/message/stream?${params.toString()}`
  
  // Retry state tracking
  let retryCount = 0
  let retryDelay = INITIAL_RETRY_DELAY
  let lastEventTime = Date.now()
  let timeoutCheckInterval = null
  let isManualClose = false
  let shouldFallback = false
  let lastSeenSequence = -1  // Track last seen sequence number for deduplication
  
  // Create EventSource connection
  let eventSource = null
  let isClosed = false
  
  /**
   * Determine if an error is retriable
   */
  function isRetriableError(errorData, readyState) {
    // Network errors or connection errors are retriable
    if (readyState === EventSource.CONNECTING) return true
    
    // If no error data, it's likely a connection error
    if (!errorData) return true
    
    // Server errors with explicit data are not retriable
    if (errorData.retriable === false) return false
    if (errorData.error_type === 'quota_exceeded') return false
    if (errorData.error_type === 'auth_error') return false
    
    // Timeouts and other transient errors are retriable
    return true
  }
  
  /**
   * Create a new EventSource connection
   */
  function createConnection() {
    try {
      console.log(`[ChatStream] Creating connection attempt (retryCount=${retryCount})`)
      eventSource = new EventSource(streamUrl)
      lastEventTime = Date.now()
      isClosed = false
      
      // Handle connection open
      eventSource.addEventListener('open', () => {
        console.log('[ChatStream] Connection established')
        lastEventTime = Date.now()
        
        // Reset retry state on successful reconnection
        if (retryCount > 0) {
          console.log('[ChatStream] Successful reconnection, resetting retry state')
          retryCount = 0
          retryDelay = INITIAL_RETRY_DELAY
          shouldFallback = false
          // Note: Keep lastSeenSequence to deduplicate chunks from previous attempt
          
          // Notify UI that connection is recovered (update status if needed)
          if (onStatus) {
            onStatus({
              type: 'thinking',
              message: 'Connection recovered, resuming...'
            })
          }
        }
      })
      
      // Handle status events
      eventSource.addEventListener('status', (event) => {
        try {
          lastEventTime = Date.now()
          const statusData = JSON.parse(event.data)
          if (onStatus) {
            onStatus(statusData)
          }
        } catch (err) {
          console.error('[ChatStream] Failed to parse status event:', err)
          if (onError) {
            onError('Failed to parse status data')
          }
        }
      })
      
      // Handle text chunk events
      eventSource.addEventListener('chunk', (event) => {
        try {
          lastEventTime = Date.now()
          
          // Parse chunk data (now includes seq for deduplication)
          let chunkText = ''
          let chunkSeq = -1
          
          try {
            const chunkData = JSON.parse(event.data)
            chunkText = chunkData.text || ''
            chunkSeq = chunkData.seq || -1
          } catch {
            // Fallback for plain text chunks (backward compatibility)
            chunkText = event.data
            chunkSeq = -1
          }
          
          // Deduplicate by sequence number (skip if we've already seen this seq)
          if (chunkSeq > 0 && chunkSeq <= lastSeenSequence) {
            console.log(`[ChatStream] Skipping duplicate chunk with seq=${chunkSeq}, last seen=${lastSeenSequence}`)
            return
          }
          
          if (chunkSeq > 0) {
            lastSeenSequence = chunkSeq
          }
          
          if (onChunk) {
            onChunk(chunkText)
          }
        } catch (err) {
          console.error('[ChatStream] Failed to process chunk event:', err)
          if (onError) {
            onError('Failed to process text chunk')
          }
        }
      })
      
      // Handle course events
      eventSource.addEventListener('course', (event) => {
        try {
          lastEventTime = Date.now()
          const courseData = JSON.parse(event.data)
          if (onCourse) {
            onCourse(courseData)
          }
        } catch (err) {
          console.error('[ChatStream] Failed to parse course event:', err)
          if (onError) {
            onError('Failed to parse course data')
          }
        }
      })
      
      // Handle flashcard events
      eventSource.addEventListener('flashcard', (event) => {
        try {
          lastEventTime = Date.now()
          const flashcardData = JSON.parse(event.data)
          if (onFlashcard) {
            onFlashcard(flashcardData)
          }
        } catch (err) {
          console.error('[ChatStream] Failed to parse flashcard event:', err)
          if (onError) {
            onError('Failed to parse flashcard data')
          }
        }
      })
      
      // Handle complete events
      eventSource.addEventListener('complete', (event) => {
        try {
          lastEventTime = Date.now()
          const completeData = JSON.parse(event.data)
          if (onComplete) {
            onComplete(completeData.session_id, completeData.grounding_metadata)
          }
          // Clear timeout interval before closing
          if (timeoutCheckInterval) {
            clearInterval(timeoutCheckInterval)
            timeoutCheckInterval = null
          }
          closeConnection()
        } catch (err) {
          console.error('[ChatStream] Failed to parse complete event:', err)
          if (onError) {
            onError('Failed to parse completion data')
          }
          if (timeoutCheckInterval) {
            clearInterval(timeoutCheckInterval)
            timeoutCheckInterval = null
          }
          closeConnection()
        }
      })
      
      // Handle error events from server
      eventSource.addEventListener('error', (evt) => {
        try {
          lastEventTime = Date.now()
          
          // Ignore network-layer errors (when readyState is not OPEN)
          // Network errors are handled by onerror, only process server-sent error events
          if (eventSource.readyState !== EventSource.OPEN) {
            console.log('[ChatStream] Ignoring network-layer error event, letting onerror handle it')
            return
          }
          
          // Process server-sent error events only
          let errorData = null
          let retriable = true
          
          if (evt.data) {
            try {
              errorData = JSON.parse(evt.data)
              retriable = isRetriableError(errorData, eventSource.readyState)
            } catch {
              retriable = true
            }
          }
          
          if (!retriable) {
            // Fatal server error, don't retry
            console.log('[ChatStream] Fatal server error, not retrying')
            if (onError) {
              onError(errorData?.error || 'A fatal error occurred during streaming')
            }
            if (timeoutCheckInterval) {
              clearInterval(timeoutCheckInterval)
              timeoutCheckInterval = null
            }
            closeConnection()
          } else {
            // Retriable error, attempt reconnection
            console.log('[ChatStream] Retriable server error detected, attempting reconnection')
            handleReconnection()
          }
        } catch (err) {
          console.error('[ChatStream] Failed to parse error event:', err)
          if (onError) {
            onError('An error occurred during streaming')
          }
          if (timeoutCheckInterval) {
            clearInterval(timeoutCheckInterval)
            timeoutCheckInterval = null
          }
          closeConnection()
        }
      })
      
      // Handle network connection errors (onerror is the main network error handler)
      eventSource.onerror = () => {
        const readyState = eventSource ? eventSource.readyState : EventSource.CLOSED
        console.error('[ChatStream] Network connection error, readyState:', readyState)
        
        // Only handle network-layer errors here, not server-sent errors
        if (readyState === EventSource.CLOSED || readyState === EventSource.CONNECTING) {
          console.log('[ChatStream] Connection lost or failed, attempting reconnection')
          handleReconnection()
        }
      }
      
      // Start timeout check interval
      if (!timeoutCheckInterval) {
        timeoutCheckInterval = setInterval(() => {
          if (isClosed) return
          
          const timeSinceLastEvent = Date.now() - lastEventTime
          if (timeSinceLastEvent > STREAM_TIMEOUT) {
            console.log(`[ChatStream] Stream timeout after ${STREAM_TIMEOUT}ms, last event ${timeSinceLastEvent}ms ago`)
            handleReconnection()
          }
        }, 5000)
      }
      
    } catch (err) {
      console.error('[ChatStream] Failed to create EventSource:', err)
      if (onError) {
        onError('Failed to establish streaming connection')
      }
    }
  }
  
  /**
   * Handle reconnection with exponential backoff
   */
  function handleReconnection() {
    if (isClosed && isManualClose) return // Manual close, don't retry
    
    // Check if we can still retry (before incrementing)
    if (retryCount < MAX_RETRY_ATTEMPTS) {
      retryCount++
      
      // Calculate exponential backoff
      retryDelay = Math.min(retryDelay * 2, MAX_RETRY_DELAY)
      
      console.log(`[ChatStream] Reconnection attempt ${retryCount}/${MAX_RETRY_ATTEMPTS} in ${retryDelay}ms`)
      
      // Notify about retry
      if (onRetry) {
        onRetry({
          retryCount,
          maxRetries: MAX_RETRY_ATTEMPTS
        })
      }
      
      // Close current connection and wait before reconnecting
      if (eventSource) {
        eventSource.close()
        eventSource = null
      }
      
      setTimeout(() => {
        if (!isClosed) {
          createConnection()
        }
      }, retryDelay)
    } else {
      // Max retries exhausted, trigger fallback
      console.log('[ChatStream] Max retries exhausted, triggering fallback to POST endpoint')
      shouldFallback = true
      
      if (onFallback) {
        onFallback()
      }
      
      if (timeoutCheckInterval) {
        clearInterval(timeoutCheckInterval)
        timeoutCheckInterval = null
      }
      
      closeConnection()
    }
  }
  
  /**
   * Close the EventSource connection
   */
  function closeConnection() {
    if (isClosed) return
    isClosed = true
    
    if (eventSource) {
      console.log('[ChatStream] Closing connection')
      eventSource.close()
      eventSource = null
    }
    
    if (timeoutCheckInterval) {
      clearInterval(timeoutCheckInterval)
      timeoutCheckInterval = null
    }
  }
  
  // Create initial connection
  try {
    createConnection()
  } catch (err) {
    console.error('[ChatStream] Failed to initialize streaming:', err)
    if (onError) {
      onError('Failed to establish streaming connection')
    }
  }
  
  // Return controller object
  return {
    /**
     * Close the streaming connection manually
     */
    close() {
      isManualClose = true
      closeConnection()
    },
    
    /**
     * Get the current connection state
     * @returns {number} EventSource.CONNECTING (0), EventSource.OPEN (1), or EventSource.CLOSED (2)
     */
    getReadyState() {
      return eventSource ? eventSource.readyState : EventSource.CLOSED
    },
    
    /**
     * Get current retry state
     * @returns {Object} {retryCount, maxRetries, shouldFallback}
     */
    getRetryState() {
      return {
        retryCount,
        maxRetries: MAX_RETRY_ATTEMPTS,
        shouldFallback
      }
    }
  }
}
