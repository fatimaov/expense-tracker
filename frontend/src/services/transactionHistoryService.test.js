import { afterEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from './apiClient.js'
import { transactionService } from './transactionService.js'

vi.mock('./apiClient.js', () => ({ apiClient: { get: vi.fn(), put: vi.fn(), delete: vi.fn(), post: vi.fn() } }))
vi.mock('./tokenStorage.js', () => ({ getToken: vi.fn(() => 'token') }))

afterEach(() => vi.restoreAllMocks())

describe('transaction history service', () => {
  it('requests the default page and scope with authentication', async () => {
    await transactionService.getTransactions()
    expect(apiClient.get).toHaveBeenCalledWith('/v2/transactions?scope=current_month&page=1&page_size=25', {
      headers: { Authorization: 'Bearer token' },
    })
  })

  it('sends UUID idempotency keys for edits and deletes', async () => {
    const randomUUID = vi.spyOn(globalThis.crypto, 'randomUUID').mockReturnValue('198da5da-a4c4-4e29-862f-62c4fc1530b7')
    const payload = { amount: '4.00' }
    await transactionService.updateTransaction(7, payload)
    await transactionService.deleteTransaction(7)
    expect(randomUUID).toHaveBeenCalledTimes(2)
    expect(apiClient.put).toHaveBeenCalledWith('/v2/transactions/7', payload, { headers: { Authorization: 'Bearer token', 'Idempotency-Key': '198da5da-a4c4-4e29-862f-62c4fc1530b7' } })
    expect(apiClient.delete).toHaveBeenCalledWith('/v2/transactions/7', { headers: { Authorization: 'Bearer token', 'Idempotency-Key': '198da5da-a4c4-4e29-862f-62c4fc1530b7' } })
  })
})
