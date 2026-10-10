import { afterEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from './apiClient.js'

afterEach(() => vi.restoreAllMocks())

describe('apiClient multipart requests', () => {
  it('passes FormData through without setting a content type boundary manually', async () => {
    const receipt = new File(['image-bytes'], 'receipt.png', { type: 'image/png' })
    const body = new FormData()
    body.append('receipt', receipt)
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, status: 200, text: async () => '{"data":{}}' }))

    await apiClient.post('/v2/assisted-entry/receipt', body, { headers: { Authorization: 'Bearer token' } })

    const [url, options] = fetch.mock.calls[0]
    expect(url).toContain('/v2/assisted-entry/receipt')
    expect(options.body).toBe(body)
    expect(options.headers).toEqual({ Authorization: 'Bearer token' })
  })
})
