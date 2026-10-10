import React from 'react'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router'
import AddTransactionPage from './AddTransactionPage.jsx'
import { transactionService } from '../services/transactionService.js'

vi.mock('../services/transactionService.js', () => ({
  transactionService: { createTransaction: vi.fn(), createTextDraft: vi.fn(), createReceiptDraft: vi.fn() },
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

  it('keeps the full manual form available while the text panel is collapsed', () => {
    renderPage()
    expect(screen.getByLabelText('Amount (€)')).toBeInTheDocument()
    expect(screen.queryByLabelText('Transaction description')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Describe a transaction' })).toHaveAttribute('aria-expanded', 'false')
    expect(screen.getByRole('button', { name: 'Upload a receipt' })).toHaveAttribute('aria-expanded', 'false')
  })

  it('creates a receipt-derived draft for review and saves only through the normal transaction command', async () => {
    const user = userEvent.setup()
    const file = new File(['valid-image'], 'receipt.png', { type: 'image/png' })
    transactionService.createReceiptDraft.mockResolvedValue({ data: {
      draft: { transaction_type: 'expense', amount: '18.75', transaction_date: '2026-10-09', category_key: 'expense_food', notes: 'Cafe Example' },
      missing_fields: [], uncertainties: [],
    } })
    transactionService.createTransaction.mockResolvedValue({ data: {} })
    renderPage()

    await user.click(screen.getByRole('button', { name: 'Upload a receipt' }))
    const picker = screen.getByLabelText('Receipt image')
    expect(picker).toHaveAttribute('accept', 'image/jpeg,image/png,image/webp')
    expect(picker).not.toHaveAttribute('multiple')
    fireEvent.change(picker, { target: { files: [file] } })
    expect(screen.getByText(/Selected: receipt.png/)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Create draft' }))

    expect(await screen.findByText(/This draft came from a receipt image/)).toBeInTheDocument()
    expect(screen.getByLabelText('Amount (€)')).toHaveValue('18.75')
    expect(screen.getByLabelText('Date')).toHaveValue('2026-10-09')
    expect(screen.getByLabelText('Category')).toHaveValue('expense_food')
    expect(screen.getByLabelText(/Notes/)).toHaveValue('Cafe Example')
    await user.clear(screen.getByLabelText(/Notes/))
    await user.type(screen.getByLabelText(/Notes/), 'Corrected merchant')
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))
    await waitFor(() => expect(transactionService.createTransaction).toHaveBeenCalledWith(expect.objectContaining({
      transaction_type: 'expense', amount: '18.75', transaction_date: '2026-10-09',
      category_key: 'expense_food', notes: 'Corrected merchant', b_u_c: null, reflective_context: null,
    })))
    expect(transactionService.createReceiptDraft).toHaveBeenCalledWith(file)
  })

  it('rejects missing, unsupported, and oversized receipt files before provider processing', async () => {
    const user = userEvent.setup()
    renderPage()
    await user.click(screen.getByRole('button', { name: 'Upload a receipt' }))
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByText('Choose one receipt image before creating a draft.')).toBeInTheDocument()

    const picker = screen.getByLabelText('Receipt image')
    fireEvent.change(picker, { target: { files: [new File(['x'], 'receipt.txt', { type: 'text/plain' })] } })
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByText('Choose a JPEG, PNG, or WebP image.')).toBeInTheDocument()

    const oversized = new File([new Uint8Array((10 * 1024 * 1024) + 1)], 'large.png', { type: 'image/png' })
    fireEvent.change(picker, { target: { files: [oversized] } })
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByText('Choose an image that is 10 MB or smaller.')).toBeInTheDocument()
    expect(transactionService.createReceiptDraft).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Amount (€)')).toBeInTheDocument()
  })

  it('preserves the selected receipt and keeps manual entry usable after provider errors', async () => {
    const user = userEvent.setup()
    const file = new File(['valid-image'], 'receipt.webp', { type: 'image/webp' })
    transactionService.createReceiptDraft.mockRejectedValue({
      message: 'The AI provider request timed out.',
      data: { error: { message: 'The AI provider request timed out.' } },
    })
    transactionService.createTransaction.mockResolvedValue({ data: {} })
    renderPage()
    await user.click(screen.getByRole('button', { name: 'Upload a receipt' }))
    fireEvent.change(screen.getByLabelText('Receipt image'), { target: { files: [file] } })
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByRole('alert')).toHaveTextContent(/enter the transaction manually/i)
    expect(screen.getByText(/Selected: receipt.webp/)).toBeInTheDocument()
    await user.type(screen.getByLabelText('Amount (€)'), '12.50')
    await user.selectOptions(screen.getByLabelText('Category'), 'expense_food')
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))
    await waitFor(() => expect(transactionService.createTransaction).toHaveBeenCalledOnce())
  })

  it('requires confirmation before a receipt draft replaces manual values and supports discard', async () => {
    const user = userEvent.setup()
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
    const file = new File(['valid-image'], 'receipt.jpg', { type: 'image/jpeg' })
    transactionService.createReceiptDraft.mockResolvedValue({ data: {
      draft: { transaction_type: 'expense', amount: '10.00', transaction_date: '2026-10-09', category_key: 'expense_food', notes: 'Cafe' },
      missing_fields: [], uncertainties: [],
    } })
    renderPage()
    await user.type(screen.getByLabelText('Amount (€)'), '99.00')
    await user.click(screen.getByRole('button', { name: 'Upload a receipt' }))
    fireEvent.change(screen.getByLabelText('Receipt image'), { target: { files: [file] } })
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(confirm).toHaveBeenCalledOnce()
    expect(transactionService.createReceiptDraft).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Amount (€)')).toHaveValue('99.00')

    confirm.mockReturnValue(true)
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByLabelText('Amount (€)')).toHaveValue('10.00')
    await user.click(screen.getByRole('button', { name: 'Discard draft' }))
    expect(screen.getByLabelText('Amount (€)')).toHaveValue('')
    expect(screen.queryByText(/Review before saving/)).not.toBeInTheDocument()
  })

  it('rejects blank and over-limit text locally without calling the provider', async () => {
    const user = userEvent.setup()
    renderPage()
    await user.click(screen.getByRole('button', { name: 'Describe a transaction' }))
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByText('Enter a transaction description.')).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Transaction description'), { target: { value: 'x'.repeat(1001) } })
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByText('Use 1,000 characters or fewer.')).toBeInTheDocument()
    expect(transactionService.createTextDraft).not.toHaveBeenCalled()
  })

  it('loads a transient draft into the editable form and saves through normal transaction creation', async () => {
    const user = userEvent.setup()
    transactionService.createTextDraft.mockResolvedValue({ data: {
      draft: { transaction_type: 'expense', amount: '12.50', transaction_date: '2026-10-09', category_key: 'expense_food', notes: 'Lunch', b_u_c: null, reflective_context: null },
      missing_fields: [], uncertainties: [],
    } })
    transactionService.createTransaction.mockResolvedValue({ data: {} })
    renderPage()
    await user.click(screen.getByRole('button', { name: 'Describe a transaction' }))
    await user.type(screen.getByLabelText('Transaction description'), 'I spent €12.50 on lunch today')
    await user.click(screen.getByRole('button', { name: 'Create draft' }))

    expect(await screen.findByText(/Review before saving/)).toBeInTheDocument()
    expect(screen.getByLabelText('Amount (€)')).toHaveValue('12.50')
    expect(screen.getByLabelText('Date')).toHaveValue('2026-10-09')
    expect(screen.getByLabelText('Category')).toHaveValue('expense_food')
    expect(screen.getByLabelText(/Notes/)).toHaveValue('Lunch')
    await user.clear(screen.getByLabelText(/Notes/))
    await user.type(screen.getByLabelText(/Notes/), 'Lunch with Alex')
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))
    await waitFor(() => expect(transactionService.createTransaction).toHaveBeenCalledWith(expect.objectContaining({
      transaction_type: 'expense', amount: '12.50', transaction_date: '2026-10-09',
      category_key: 'expense_food', notes: 'Lunch with Alex', b_u_c: null, reflective_context: null,
    })))
    expect(transactionService.createTextDraft).toHaveBeenCalledWith('I spent €12.50 on lunch today')
  })

  it('requires confirmation before replacing manual form values and discard restores a blank form', async () => {
    const user = userEvent.setup()
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
    transactionService.createTextDraft.mockResolvedValue({ data: {
      draft: { transaction_type: 'expense', amount: '12.50', transaction_date: '2026-10-09', category_key: 'expense_food', notes: 'Lunch' },
      missing_fields: [], uncertainties: [],
    } })
    renderPage()
    await user.type(screen.getByLabelText('Amount (€)'), '99.00')
    await user.click(screen.getByRole('button', { name: 'Describe a transaction' }))
    await user.type(screen.getByLabelText('Transaction description'), 'Lunch')
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(confirm).toHaveBeenCalledOnce()
    expect(transactionService.createTextDraft).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Amount (€)')).toHaveValue('99.00')

    confirm.mockReturnValue(true)
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByLabelText('Amount (€)')).toHaveValue('12.50')
    await user.click(screen.getByRole('button', { name: 'Discard draft' }))
    expect(screen.getByLabelText('Amount (€)')).toHaveValue('')
    expect(screen.queryByText(/Review before saving/)).not.toBeInTheDocument()
  })

  it('preserves typed text and leaves the manual form usable after a safe provider failure', async () => {
    const user = userEvent.setup()
    transactionService.createTextDraft.mockRejectedValue({
      message: 'AI request limit reached. Try again after the current window expires.',
      data: { error: { message: 'AI request limit reached. Try again after the current window expires.' } },
    })
    transactionService.createTransaction.mockResolvedValue({ data: {} })
    renderPage()
    await user.click(screen.getByRole('button', { name: 'Describe a transaction' }))
    await user.type(screen.getByLabelText('Transaction description'), 'Typed text stays here')
    await user.click(screen.getByRole('button', { name: 'Create draft' }))
    expect(await screen.findByRole('alert')).toHaveTextContent(/enter the transaction manually/i)
    expect(screen.getByLabelText('Transaction description')).toHaveValue('Typed text stays here')
    await user.type(screen.getByLabelText('Amount (€)'), '12.50')
    await user.selectOptions(screen.getByLabelText('Category'), 'expense_food')
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))
    await waitFor(() => expect(transactionService.createTransaction).toHaveBeenCalledOnce())
  })
})
