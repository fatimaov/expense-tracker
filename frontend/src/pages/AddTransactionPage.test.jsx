import React from 'react'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router'
import AddTransactionPage from './AddTransactionPage.jsx'
import { transactionService } from '../services/transactionService.js'

vi.mock('../services/transactionService.js', () => ({
  transactionService: { createTransaction: vi.fn() },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/transactions/new']}>
      <Routes>
        <Route path="/transactions/new" element={<AddTransactionPage />} />
        <Route path="/after" element={<LocationPath />} />
      </Routes>
    </MemoryRouter>,
  )
}

function LocationPath() {
  return <output>{useLocation().pathname}</output>
}

describe('AddTransactionPage', () => {
  it('sends the V2 payload, confirms success, and resets values while keeping type', async () => {
    const user = userEvent.setup()
    transactionService.createTransaction.mockResolvedValue({ data: {} })
    renderPage()

    await user.click(screen.getByRole('radio', { name: 'Income' }))
    await user.type(screen.getByLabelText('Amount (€)'), '1200.50')
    await user.selectOptions(screen.getByLabelText('Category'), 'income_salary')
    await user.type(screen.getByLabelText(/Notes/), 'October salary')
    const selectedDate = screen.getByLabelText('Date').value
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))

    await waitFor(() => expect(transactionService.createTransaction).toHaveBeenCalledWith({
      transaction_type: 'income',
      amount: '1200.50',
      transaction_date: selectedDate,
      category_key: 'income_salary',
      notes: 'October salary',
    }))
    expect(await screen.findByRole('status')).toHaveTextContent('Transaction saved.')
    expect(screen.getByRole('radio', { name: 'Income' })).toBeChecked()
    expect(screen.getByLabelText('Amount (€)')).toHaveValue('')
    expect(screen.getByLabelText('Category')).toHaveValue('')
    expect(screen.getByLabelText(/Notes/)).toHaveValue('')
    expect(screen.getByLabelText('Date')).toHaveValue(selectedDate)
  })

  it('preserves the entered values and renders accessible server validation feedback', async () => {
    const user = userEvent.setup()
    transactionService.createTransaction.mockRejectedValue({
      message: 'Transaction details are invalid.',
      data: { error: { fields: { amount: 'Amount must be greater than zero.' } } },
    })
    renderPage()
    await user.type(screen.getByLabelText('Amount (€)'), '12.34')
    await user.selectOptions(screen.getByLabelText('Category'), 'expense_food')
    await user.type(screen.getByLabelText(/Notes/), 'Coffee')
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))

    const amount = screen.getByLabelText('Amount (€)')
    expect(await screen.findByText('Amount must be greater than zero.')).toBeInTheDocument()
    expect(amount).toHaveAttribute('aria-invalid', 'true')
    expect(amount).toHaveValue('12.34')
    expect(screen.getByLabelText('Category')).toHaveValue('expense_food')
    expect(screen.getByLabelText(/Notes/)).toHaveValue('Coffee')
  })

  it('sends selected context values when creating an expense', async () => {
    const user = userEvent.setup()
    transactionService.createTransaction.mockResolvedValue({ data: {} })
    renderPage()
    await user.type(screen.getByLabelText('Amount (€)'), '12.34')
    await user.selectOptions(screen.getByLabelText('Category'), 'expense_food')
    await user.selectOptions(screen.getByLabelText(/Spending context/), 'usage')
    await user.selectOptions(screen.getByLabelText(/Reflective context/), 'like')
    const selectedDate = screen.getByLabelText('Date').value
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))
    await waitFor(() => expect(transactionService.createTransaction).toHaveBeenCalledWith({
      transaction_type: 'expense', amount: '12.34', transaction_date: selectedDate,
      category_key: 'expense_food', notes: '', b_u_c: 'usage', reflective_context: 'like',
    }))
  })

  it('prevents another submission while the first request is pending', async () => {
    const user = userEvent.setup()
    let resolveRequest
    transactionService.createTransaction.mockReturnValue(new Promise((resolve) => { resolveRequest = resolve }))
    renderPage()
    await user.type(screen.getByLabelText('Amount (€)'), '12.34')
    await user.selectOptions(screen.getByLabelText('Category'), 'expense_food')
    const submit = screen.getByRole('button', { name: 'Save transaction' })
    await user.click(submit)
    expect(submit).toBeDisabled()
    expect(transactionService.createTransaction).toHaveBeenCalledTimes(1)
    resolveRequest({ data: {} })
  })
})
