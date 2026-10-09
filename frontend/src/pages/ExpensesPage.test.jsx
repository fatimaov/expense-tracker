import React from 'react'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router'
import ExpensesPage from './ExpensesPage.jsx'
import { expenseService } from '../services/expenseService.js'

vi.mock('../context/useAuth.js', () => ({ useAuth: () => ({ logout: vi.fn() }) }))
vi.mock('../services/expenseService.js', () => ({
  expenseService: { getExpenses: vi.fn().mockResolvedValue({ expenses: [] }) },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('ExpensesPage navigation', () => {
  it('links the primary Add transaction action to the V2 route', async () => {
    render(
      <MemoryRouter initialEntries={['/expenses']}>
        <Routes>
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route path="/transactions/new" element={<h1>V2 entry</h1>} />
        </Routes>
      </MemoryRouter>,
    )
    const link = await screen.findByRole('link', { name: 'Add transaction' })
    expect(link).toHaveAttribute('href', '/transactions/new')
    expect(expenseService.getExpenses).toHaveBeenCalledOnce()
  })
})
