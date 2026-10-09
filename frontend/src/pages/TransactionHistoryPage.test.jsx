import React from 'react'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router'
import TransactionHistoryPage from './TransactionHistoryPage.jsx'
import { transactionService } from '../services/transactionService.js'

vi.mock('../services/transactionService.js', () => ({
  transactionService: { getTransactions: vi.fn(), deleteTransaction: vi.fn() },
}))

afterEach(() => { cleanup(); vi.clearAllMocks() })

function response(data = []) {
  return { data, meta: {
    scope: 'current_month', pagination: { page: 1, page_size: 25, total_records: data.length, total_pages: 1 },
    summary: { record_count: data.length, total_income: '12.00', total_expense: '10.00', category_totals: [] },
  } }
}

const transaction = { id: 2, transaction_type: 'expense', amount: '10.00', transaction_date: '2026-10-08', category_label: 'Food', notes: 'Lunch', b_u_c: 'bill', reflective_context: 'love' }

function renderPage(row = transaction) {
  transactionService.getTransactions.mockResolvedValue(response([row]))
  return render(<MemoryRouter initialEntries={['/transactions']}><Routes><Route path="/transactions" element={<TransactionHistoryPage />} /><Route path="/transactions/2/edit" element={<h1>Edit page</h1>} /></Routes></MemoryRouter>)
}

describe('TransactionHistoryPage', () => {
  it('defaults to current month, shows the summary and switches to all history', async () => {
    const user = userEvent.setup()
    renderPage()
    expect(await screen.findByRole('heading', { name: 'Transaction history' })).toBeInTheDocument()
    expect(transactionService.getTransactions).toHaveBeenCalledWith({ scope: 'current_month', page: 1, pageSize: 25 })
    expect(screen.getByRole('row', { name: /2026-10-08/ }).textContent).toContain('−€10.00')
    expect(screen.getByText('Bill')).toHaveClass('badge', 'text-bg-light')
    expect(screen.getByText('Love')).toHaveClass('badge', 'text-bg-light')
    await user.click(screen.getByRole('button', { name: 'All history' }))
    await waitFor(() => expect(transactionService.getTransactions).toHaveBeenLastCalledWith({ scope: 'all', page: 1, pageSize: 25 }))
  })

  it('requires modal confirmation and supports cancel before soft deletion', async () => {
    const user = userEvent.setup()
    renderPage()
    await screen.findByText('Lunch')
    await user.click(screen.getByRole('button', { name: 'Delete' }))
    expect(screen.getByRole('dialog', { name: 'Delete transaction?' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(transactionService.deleteTransaction).not.toHaveBeenCalled()
    await user.click(screen.getByRole('button', { name: 'Delete' }))
    transactionService.deleteTransaction.mockResolvedValue({ data: {} })
    await user.click(screen.getByRole('button', { name: 'Delete transaction' }))
    expect(await screen.findByRole('status')).toHaveTextContent('Transaction deleted.')
    expect(transactionService.deleteTransaction).toHaveBeenCalledWith(2)
  })

  it('does not show context badges when values are unset', async () => {
    renderPage({ ...transaction, b_u_c: null, reflective_context: null })
    await screen.findByText('Lunch')
    expect(screen.queryByText('Bill')).not.toBeInTheDocument()
    expect(screen.queryByText('Love')).not.toBeInTheDocument()
  })
})
