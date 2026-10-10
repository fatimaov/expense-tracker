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
})
