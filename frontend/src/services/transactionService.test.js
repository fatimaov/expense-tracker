import { afterEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from './apiClient.js'
import { getToken } from './tokenStorage.js'
import { transactionService } from './transactionService.js'

vi.mock('./apiClient.js', () => ({ apiClient: { post: vi.fn() } }))
vi.mock('./tokenStorage.js', () => ({ getToken: vi.fn(() => 'jwt-token') }))

afterEach(() => vi.restoreAllMocks())

describe('transactionService', () => {
  it('sends text drafts to the authenticated transient endpoint without a mutation key', async () => {
    await transactionService.createTextDraft('I spent €12.50 on lunch today')
    expect(apiClient.post).toHaveBeenCalledWith('/v2/assisted-entry/text', {
      text: 'I spent €12.50 on lunch today',
    }, { headers: { Authorization: 'Bearer jwt-token' } })
  })

  it('sends an authenticated V2 create with a fresh UUID v4 idempotency key', async () => {
    const uuid = '3b12f1df-5232-4804-897e-917bf397618a'
    const randomUUID = vi.spyOn(globalThis.crypto, 'randomUUID').mockReturnValue(uuid)
    const payload = {
      transaction_type: 'expense', amount: '12.34', transaction_date: '2026-10-08',
      category_key: 'expense_food', notes: 'Lunch',
    }

    await transactionService.createTransaction(payload)

    expect(randomUUID).toHaveBeenCalledOnce()
    expect(getToken).toHaveBeenCalledOnce()
    expect(apiClient.post).toHaveBeenCalledWith('/v2/transactions', payload, {
      headers: { Authorization: 'Bearer jwt-token', 'Idempotency-Key': uuid },
    })
  })
})
