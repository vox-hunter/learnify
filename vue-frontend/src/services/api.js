import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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
