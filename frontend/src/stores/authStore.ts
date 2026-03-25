import { create } from 'zustand'
import axios from 'axios'

// Get API base URL based on platform
const getApiBaseUrl = (): string => {
  // Check if running in Capacitor (mobile)
  if (typeof window !== 'undefined' && (window as any).Capacitor) {
    // For mobile, use the backend server URL
    // import.meta.env is the Vite way to access env vars in the browser build
    // fall back to localhost for development on device/emulator
    return (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'
  }
  // For web/Electron, use relative path or proxy
  return (import.meta as any).env?.VITE_API_URL || '/api'
}

// Configure axios base URL
const apiBaseUrl = getApiBaseUrl()
if (apiBaseUrl.startsWith('http')) {
  axios.defaults.baseURL = apiBaseUrl
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setTokens: (accessToken: string, refreshToken: string) => void
}

export const useAuthStore = create<AuthState>((set) => {
  // Load tokens from localStorage on init
  const storedAccessToken = localStorage.getItem('accessToken')
  const storedRefreshToken = localStorage.getItem('refreshToken')

  return {
    accessToken: storedAccessToken,
    refreshToken: storedRefreshToken,
    isAuthenticated: !!storedAccessToken,
    login: async (email: string, password: string) => {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const apiUrl = apiBaseUrl.startsWith('http') 
        ? `${apiBaseUrl}/auth/login` 
        : '/api/auth/login'

      const response = await axios.post(apiUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      const { access_token, refresh_token } = response.data
      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)

      set({
        accessToken: access_token,
        refreshToken: refresh_token,
        isAuthenticated: true,
      })
    },
    logout: () => {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      set({
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
      })
    },
    setTokens: (accessToken: string, refreshToken: string) => {
      localStorage.setItem('accessToken', accessToken)
      localStorage.setItem('refreshToken', refreshToken)
      set({
        accessToken,
        refreshToken,
        isAuthenticated: true,
      })
    },
  }
})

// Axios interceptor for adding auth token
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
