export const TOKEN_STORAGE_KEY = 'expense_tracker_token'

export function saveToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

export function getToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
}
