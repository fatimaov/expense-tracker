import { apiClient } from './apiClient.js'
import { getToken } from './tokenStorage.js'

function getAuthorizationHeaders() {
  return {
    Authorization: `Bearer ${getToken()}`,
  }
}

function getExpenses() {
  return apiClient.get('/expenses', {
    headers: getAuthorizationHeaders(),
  })
}

function createExpense(expense) {
  return apiClient.post('/expenses', expense, {
    headers: getAuthorizationHeaders(),
  })
}

function updateExpense(id, expense) {
  return apiClient.put(`/expenses/${id}`, expense, {
    headers: getAuthorizationHeaders(),
  })
}

function deleteExpense(id) {
  return apiClient.delete(`/expenses/${id}`, {
    headers: getAuthorizationHeaders(),
  })
}

export const expenseService = {
  getExpenses,
  createExpense,
  updateExpense,
  deleteExpense,
}
