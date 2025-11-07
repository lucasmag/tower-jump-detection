// API configuration that works in both development and production
const getApiBaseUrl = () => {
  // In development, use localhost:5000
  // In production (Docker), use relative path that nginx will proxy to backend
  if (import.meta.env.DEV) {
    return 'http://localhost:5000/api'
  }
  return '/api'
}

export const API_BASE_URL = getApiBaseUrl()