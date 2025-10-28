import axios from 'axios'

// Configure API URL based on environment
// Production: Use the Render backend URL
// Development: Use localhost:8000
export const getApiBaseUrl = () => {
  // Check if VITE_API_URL is set in environment variables
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // Check if we're in production (deployed)
  if (import.meta.env.PROD) {
    return 'https://ai-loom-backend.onrender.com'
  }
  
  // Local development - backend runs on port 8000
  return 'http://localhost:8000'
}

const API_BASE_URL = getApiBaseUrl()

console.log('API Base URL:', API_BASE_URL) // Debug log

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large file uploads
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token if available
api.interceptors.request.use(
  (config) => {
    const username = localStorage.getItem('username')
    if (username) {
      config.params = {
        ...config.params,
        username
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('username')
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
