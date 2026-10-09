import React from 'react'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router'
import EditTransactionPage from './EditTransactionPage.jsx'
import { transactionService } from '../services/transactionService.js'

vi.mock('../services/transactionService.js', () => ({ transactionService: { getTransaction: vi.fn(), updateTransaction: vi.fn() } }))

afterEach(() => { cleanup(); vi.clearAllMocks() })

const current = { id: 2, transaction_type: 'expense', amount: '10.00', transaction_date: '2026-10-08', category_key: 'expense_food', category_label: 'Food', notes: 'Lunch', updated_at: '2026-10-08T12:00:00+00:00' }

function renderPage() {
  transactionService.getTransaction.mockResolvedValue({ data: current })
  return render(<MemoryRouter initialEntries={['/transactions/2/edit']}><Routes><Route path="/transactions/:id/edit" element={<EditTransactionPage />} /><Route path="/transactions" element={<h1>History</h1>} /></Routes></MemoryRouter>)
}

describe('EditTransactionPage', () => {
  it('prefills fields, keeps type read-only, and sends updated_at with the update', async () => {
    const user = userEvent.setup()
    transactionService.updateTransaction.mockResolvedValue({})
    renderPage()
    expect(await screen.findByDisplayValue('10.00')).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: 'Expense' })).toBeDisabled()
    await user.clear(screen.getByLabelText('Amount (€)'))
    await user.type(screen.getByLabelText('Amount (€)'), '12.00')
    await user.click(screen.getByRole('button', { name: 'Save changes' }))
    await waitFor(() => expect(transactionService.updateTransaction).toHaveBeenCalledWith('2', {
      amount: '12.00', transaction_date: '2026-10-08', category_key: 'expense_food', notes: 'Lunch', updated_at: current.updated_at,
    }))
    expect(await screen.findByRole('heading', { name: 'History' })).toBeInTheDocument()
  })

  it('refreshes a stale record and asks the user to review it', async () => {
    const user = userEvent.setup()
    const latest = { ...current, amount: '15.00', updated_at: '2026-10-08T13:00:00+00:00' }
    transactionService.getTransaction.mockResolvedValueOnce({ data: current }).mockResolvedValueOnce({ data: latest })
    transactionService.updateTransaction.mockRejectedValue({ status: 409, message: 'Conflict' })
    renderPage()
    await screen.findByDisplayValue('10.00')
    await user.click(screen.getByRole('button', { name: 'Save changes' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('changed elsewhere')
    expect(await screen.findByDisplayValue('15.00')).toBeInTheDocument()
  })
})
