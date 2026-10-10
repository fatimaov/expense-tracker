import { apiClient } from './apiClient.js'
import { getToken } from './tokenStorage.js'

function queryCompanion(question, scope) {
  return apiClient.post('/v2/companion/query', { question, scope }, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
}

export const companionService = { queryCompanion }
