import { apiClient } from './apiClient.js'

function register(credentials) {
  return apiClient.post('/register', credentials)
}

function login(credentials) {
  return apiClient.post('/login', credentials)
}

function getCurrentUser() {
  return apiClient.get('/me')
}

export const authService = {
  register,
  login,
  getCurrentUser,
}
