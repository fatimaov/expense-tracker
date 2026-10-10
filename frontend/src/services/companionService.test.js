import { afterEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from './apiClient.js'
import { getToken } from './tokenStorage.js'
import { companionService } from './companionService.js'

vi.mock('./apiClient.js', () => ({ apiClient: { post: vi.fn() } }))
vi.mock('./tokenStorage.js', () => ({ getToken: vi.fn() }))

afterEach(() => vi.clearAllMocks())

describe('companionService', () => {
  it('posts the selected scope and question with the signed-in user token', async () => {
    getToken.mockReturnValue('session-token')
    apiClient.post.mockResolvedValue({ data: { kind: 'answer' } })
    await companionService.queryCompanion('How much did I spend?', 'all')
    expect(apiClient.post).toHaveBeenCalledWith('/v2/companion/query', {
      question: 'How much did I spend?', scope: 'all',
    }, { headers: { Authorization: 'Bearer session-token' } })
  })

  it('includes only the explicitly selected transaction as a proposal target', async () => {
    getToken.mockReturnValue('session-token')
    apiClient.post.mockResolvedValue({ data: { kind: 'proposal' } })
    await companionService.queryCompanion('Change this record', 'all', 42)
    expect(apiClient.post).toHaveBeenCalledWith('/v2/companion/query', {
      question: 'Change this record', scope: 'all', target_transaction_id: 42,
    }, { headers: { Authorization: 'Bearer session-token' } })
  })

  it('sends edited transient values back for deterministic server validation and preview', async () => {
    getToken.mockReturnValue('session-token')
    apiClient.post.mockResolvedValue({ data: { kind: 'proposal' } })
    await companionService.reviewCompanionProposal('Change this record', 'current_month', {
      target_transaction_id: 42,
      operation: 'edit_transaction',
      affected_fields: ['amount'],
      proposed_values: { amount: '16.25' },
      proposal_version: '2026-10-08T10:00:00Z',
      uncertainty: 'The amount was clear.',
    })
    expect(apiClient.post).toHaveBeenCalledWith('/v2/companion/query', {
      question: 'Change this record', scope: 'current_month', target_transaction_id: 42,
      proposal_review: {
        operation: 'edit_transaction', affected_fields: ['amount'], proposed_values: { amount: '16.25' },
        proposal_version: '2026-10-08T10:00:00Z', uncertainty: 'The amount was clear.',
      },
    }, { headers: { Authorization: 'Bearer session-token' } })
  })
})
