import React from 'react'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import TransactionForm from './TransactionForm.jsx'

afterEach(cleanup)

describe('TransactionForm', () => {
  it('shows the category choices for the selected transaction type', async () => {
    const user = userEvent.setup()
    render(<TransactionForm onSubmit={vi.fn()} isSubmitting={false} />)
    const category = screen.getByRole('combobox', { name: 'Category' })

    expect(category).toHaveDisplayValue('Select a category')
    expect([...category.options].map((option) => option.value)).toEqual([
      '', 'expense_transport', 'expense_accommodation', 'expense_food', 'expense_activities', 'expense_other',
    ])

    await user.click(screen.getByRole('radio', { name: 'Income' }))
    expect([...category.options].map((option) => option.value)).toEqual(['', 'income_salary', 'income_other'])
  })

  it('shows accessible client validation errors for required fields', async () => {
    const user = userEvent.setup()
    render(<TransactionForm onSubmit={vi.fn()} isSubmitting={false} />)
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))

    expect(screen.getByLabelText('Amount (€)')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByText('Enter a positive amount with up to 12 digits and 2 decimal places.')).toBeInTheDocument()
    expect(screen.getByLabelText('Category')).toHaveAttribute('aria-invalid', 'true')
  })

  it('shows optional context values and supportive guidance for expenses', () => {
    render(<TransactionForm onSubmit={vi.fn()} isSubmitting={false} />)
    expect([...screen.getByLabelText(/Spending context/).options].map((option) => option.value)).toEqual(['', 'bill', 'usage', 'choice'])
    expect([...screen.getByLabelText(/Reflective context/).options].map((option) => option.value)).toEqual(['', 'need', 'love', 'like', 'want'])
    expect(screen.getByText(/optional descriptive tools, not scores or judgements/i)).toBeInTheDocument()
    expect(screen.getByText(/Bill is a fixed obligation/)).toBeInTheDocument()
  })

  it('clears hidden expense context when switching to income and omits it on submit', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<TransactionForm onSubmit={onSubmit} isSubmitting={false} />)
    await user.selectOptions(screen.getByLabelText(/Spending context/), 'bill')
    await user.selectOptions(screen.getByLabelText(/Reflective context/), 'need')
    await user.click(screen.getByRole('radio', { name: 'Income' }))
    expect(screen.queryByLabelText(/Spending context/)).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/Reflective context/)).not.toBeInTheDocument()
    await user.type(screen.getByLabelText('Amount (€)'), '12.00')
    await user.selectOptions(screen.getByLabelText('Category'), 'income_salary')
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))
    expect(onSubmit).toHaveBeenCalledWith(expect.not.objectContaining({ b_u_c: expect.anything(), reflective_context: expect.anything() }))
  })

  it('submits explicit null values when expense context is not set', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<TransactionForm onSubmit={onSubmit} isSubmitting={false} />)
    await user.type(screen.getByLabelText('Amount (€)'), '12.00')
    await user.selectOptions(screen.getByLabelText('Category'), 'expense_food')
    await user.click(screen.getByRole('button', { name: 'Save transaction' }))
    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ b_u_c: null, reflective_context: null }))
  })
})
