import { apiClient } from './apiClient.js'
import { getToken } from './tokenStorage.js'

function createTransaction(transaction) {
  return apiClient.post('/v2/transactions', transaction, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Idempotency-Key': globalThis.crypto.randomUUID(),
    },
  })
}

function createTextDraft(text) {
  return apiClient.post('/v2/assisted-entry/text', { text }, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
}

function createReceiptDraft(file) {
  const body = new FormData()
  body.append('receipt', file)
  return apiClient.post('/v2/assisted-entry/receipt', body, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
}

function getTransactions({ scope = 'current_month', page = 1, pageSize = 25 } = {}) {
  const params = new URLSearchParams({ scope, page: String(page), page_size: String(pageSize) })
  return apiClient.get(`/v2/transactions?${params}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
}

function getTransaction(id) {
  return apiClient.get(`/v2/transactions/${id}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
}

function updateTransaction(id, transaction) {
  return apiClient.put(`/v2/transactions/${id}`, transaction, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Idempotency-Key': globalThis.crypto.randomUUID(),
    },
  })
}

function deleteTransaction(id) {
  return apiClient.delete(`/v2/transactions/${id}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Idempotency-Key': globalThis.crypto.randomUUID(),
    },
  })
}

export const transactionService = { createTransaction, createTextDraft, createReceiptDraft, getTransactions, getTransaction, updateTransaction, deleteTransaction }
