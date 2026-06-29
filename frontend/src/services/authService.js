import { apiClient } from './apiClient.js'

function register(credentials) {
  return apiClient.post('/register', credentials)
}

function login(credentials) {
  return apiClient.post('/login', credentials)
}

function getCurrentUser(token) {
  return apiClient.get('/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}

export const authService = {
  register,
  login,
  getCurrentUser,
}
