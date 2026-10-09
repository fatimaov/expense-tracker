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
})
