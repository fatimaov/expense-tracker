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

export const transactionService = { createTransaction }
