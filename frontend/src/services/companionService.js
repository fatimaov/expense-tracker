import { apiClient } from './apiClient.js'
import { getToken } from './tokenStorage.js'

function queryCompanion(question, scope, targetTransactionId) {
  const payload = { question, scope }
  if (targetTransactionId !== undefined && targetTransactionId !== null) {
    payload.target_transaction_id = targetTransactionId
  }
  return apiClient.post('/v2/companion/query', payload, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
}

function reviewCompanionProposal(question, scope, proposal) {
  return apiClient.post('/v2/companion/query', {
    question,
    scope,
    target_transaction_id: proposal.target_transaction_id,
    proposal_review: {
      operation: proposal.operation,
      affected_fields: proposal.affected_fields,
      proposed_values: proposal.proposed_values,
      proposal_version: proposal.proposal_version,
      uncertainty: proposal.uncertainty,
    },
  }, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
}

export const companionService = { queryCompanion, reviewCompanionProposal }
