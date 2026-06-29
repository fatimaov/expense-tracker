import { apiClient } from './apiClient.js'

function register(credentials) {
  return apiClient.post('/auth/register', credentials)
}

function login(credentials) {
  return apiClient.post('/auth/login', credentials)
}

function getCurrentUser(token) {
  return apiClient.get('/users/me', {
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
