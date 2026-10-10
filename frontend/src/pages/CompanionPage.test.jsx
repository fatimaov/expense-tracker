import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router'
import CompanionPage from './CompanionPage.jsx'
import { companionService } from '../services/companionService.js'
import { transactionService } from '../services/transactionService.js'

vi.mock('../services/companionService.js', () => ({
  companionService: { queryCompanion: vi.fn(), reviewCompanionProposal: vi.fn() },
}))
vi.mock('../services/transactionService.js', () => ({
  transactionService: { updateTransaction: vi.fn(), deleteTransaction: vi.fn() },
}))

afterEach(() => { cleanup(); vi.clearAllMocks() })

function answer(message, scope = 'current_month') {
  return { data: {
    kind: 'answer', message, scope,
    period: { start: '2026-10-01', end_exclusive: '2026-11-01' },
    evidence: {
      scope, timezone: 'Europe/Madrid', period: { start: '2026-10-01', end_exclusive: '2026-11-01' },
      included_record_count: 1, total: { expense: '12.50' }, exclusions: { soft_deleted: 1 }, warnings: ['Some expenses are missing optional context.'],
    },
  } }
}

function matchingAnswer(message = 'I found one matching record.') {
  return { data: {
    kind: 'answer', message, scope: 'current_month',
    period: { start: '2026-10-01', end_exclusive: '2026-11-01' },
    evidence: {
      scope: 'current_month', timezone: 'Europe/Madrid',
      period: { start: '2026-10-01', end_exclusive: '2026-11-01' },
      matching_count: 1, truncated: false, exclusions: {}, warnings: [],
      records: [{ id: 9, transaction_type: 'expense', amount: '12.50', transaction_date: '2026-10-08', category_key: 'expense_food', category_label: 'Food', notes: 'Lunch', b_u_c: null, reflective_context: null }],
    },
  } }
}

function proposal(operation = 'edit_transaction', fields = ['amount'], values = { amount: '15.00' }) {
  return { data: {
    kind: 'proposal', message: 'I prepared the requested change for review.', scope: 'current_month',
    period: { start: '2026-10-01', end_exclusive: '2026-11-01' },
    evidence: { scope: 'current_month', timezone: 'Europe/Madrid', period: { start: '2026-10-01', end_exclusive: '2026-11-01' }, exclusions: {}, warnings: [], target_transaction: {} },
    proposal: {
      operation, target_transaction_id: 9, affected_fields: fields,
      current_record: { id: 9, transaction_type: 'expense', amount: '12.50', transaction_date: '2026-10-08', category_key: 'expense_food', category_label: 'Food', notes: 'Lunch', b_u_c: null, reflective_context: null, updated_at: '2026-10-08T10:00:00+00:00' },
      proposed_values: values, uncertainty: 'The request was clear.',
      expected_effect: { kind: 'financial_change', monthly_deltas: [{ month: '2026-10', income_delta: '0.00', expense_delta: '2.50', net_delta: '-2.50', category_deltas: [{ category_key: 'expense_food', delta: '2.50' }] }] },
      proposal_version: '2026-10-08T10:00:00+00:00',
    },
  } }
}

function renderPage() {
  return render(<MemoryRouter initialEntries={['/companion']}><Routes><Route path="/companion" element={<CompanionPage />} /></Routes></MemoryRouter>)
}

describe('CompanionPage', () => {
  it('defaults to current month and shows the scoped answer and expandable evidence', async () => {
    const user = userEvent.setup()
    companionService.queryCompanion.mockResolvedValue(answer('You spent €12.50.'))
    renderPage()
    expect(screen.getByLabelText('Scope')).toHaveValue('current_month')
    expect(screen.getByRole('link', { name: 'Companion' })).toHaveAttribute('href', '/companion')
    await user.type(screen.getByLabelText('Question'), 'How much did I spend?')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    expect(await screen.findByText('You spent €12.50.')).toBeInTheDocument()
    expect(companionService.queryCompanion).toHaveBeenCalledWith('How much did I spend?', 'current_month')
    expect(screen.getByText(/Current month · 2026-10-01/)).toBeInTheDocument()
    expect(screen.getByText('Evidence and limitations').closest('details')).not.toHaveAttribute('open')
    await user.click(screen.getByText('Evidence and limitations'))
    expect(screen.getByText(/expense: €12.50/)).toBeInTheDocument()
    expect(screen.getByText(/soft deleted 1/)).toBeInTheDocument()
    expect(screen.getByText('Some expenses are missing optional context.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit|delete|confirm/i })).not.toBeInTheDocument()
  })

  it('uses all-history scope and replaces the active response after a later success', async () => {
    const user = userEvent.setup()
    companionService.queryCompanion.mockResolvedValueOnce(answer('First response.'))
      .mockResolvedValueOnce(answer('Second response.', 'all'))
    renderPage()
    await user.selectOptions(screen.getByLabelText('Scope'), 'all')
    await user.type(screen.getByLabelText('Question'), 'Show income by category')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    expect(await screen.findByText('First response.')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    expect(await screen.findByText('Second response.')).toBeInTheDocument()
    expect(screen.queryByText('First response.')).not.toBeInTheDocument()
    expect(companionService.queryCompanion).toHaveBeenNthCalledWith(2, 'Show income by category', 'all')
  })

  it('preserves the question and existing response after a failure, then remains usable', async () => {
    const user = userEvent.setup()
    companionService.queryCompanion.mockResolvedValueOnce(answer('Existing response.'))
      .mockRejectedValueOnce(new Error('The AI provider request timed out.'))
      .mockResolvedValueOnce(answer('Recovered response.'))
    renderPage()
    const question = screen.getByLabelText('Question')
    await user.type(question, 'How much did I spend?')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    await screen.findByText('Existing response.')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('The AI provider request timed out.')
    expect(question).toHaveValue('How much did I spend?')
    expect(screen.getByText('Existing response.')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    expect(await screen.findByText('Recovered response.')).toBeInTheDocument()
  })

  it('validates blank and over-limit questions before submitting and exposes loading', async () => {
    const user = userEvent.setup()
    let resolveRequest
    companionService.queryCompanion.mockImplementation(() => new Promise((resolve) => { resolveRequest = resolve }))
    renderPage()
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    expect(screen.getByText('Enter a question of 1 to 1,000 characters.')).toBeInTheDocument()
    expect(companionService.queryCompanion).not.toHaveBeenCalled()
    const question = screen.getByLabelText('Question')
    fireEvent.change(question, { target: { value: 'x'.repeat(1000) } })
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    expect(screen.getByRole('status')).toHaveTextContent('Preparing an answer')
    await waitFor(() => expect(companionService.queryCompanion).toHaveBeenCalledWith('x'.repeat(1000), 'current_month'))
    resolveRequest(answer('Done.'))
    expect(await screen.findByText('Done.')).toBeInTheDocument()
  })

  it('selects one matching result and shows a transient reviewable proposal', async () => {
    const user = userEvent.setup()
    companionService.queryCompanion.mockResolvedValueOnce(matchingAnswer()).mockResolvedValueOnce(proposal())
    renderPage()
    await user.type(screen.getByLabelText('Question'), 'Find records matching: lunch')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    await screen.findByText('I found one matching record.')
    await user.click(screen.getByText('Evidence and limitations'))
    await user.click(screen.getByRole('button', { name: 'Prepare a change' }))
    expect(screen.getByText(/record #9/)).toBeInTheDocument()
    await user.type(screen.getByLabelText('Question'), 'Change the amount to €15')
    await user.click(screen.getByRole('button', { name: 'Ask for a change' }))
    expect(await screen.findByRole('region', { name: 'Companion proposal' })).toBeInTheDocument()
    expect(screen.getByText(/No change has been applied/)).toBeInTheDocument()
    expect(screen.getByText(/Proposal version/)).toBeInTheDocument()
    expect(companionService.queryCompanion).toHaveBeenNthCalledWith(2, 'Change the amount to €15', 'current_month', 9)
    expect(transactionService.updateTransaction).not.toHaveBeenCalled()
    expect(transactionService.deleteTransaction).not.toHaveBeenCalled()
  })

  it('edits an edit proposal and confirms through the normal update command with the captured version', async () => {
    const user = userEvent.setup()
    companionService.queryCompanion.mockResolvedValueOnce(matchingAnswer()).mockResolvedValueOnce(proposal())
      .mockResolvedValueOnce(matchingAnswer('The updated transaction is no longer in this match.'))
    companionService.reviewCompanionProposal.mockResolvedValue(proposal('edit_transaction', ['amount'], { amount: '16.25' }))
    const reviewed = proposal('edit_transaction', ['amount'], { amount: '16.25' }).data
    reviewed.proposal.expected_effect.monthly_deltas[0].expense_delta = '3.75'
    reviewed.proposal.expected_effect.monthly_deltas[0].net_delta = '-3.75'
    companionService.reviewCompanionProposal.mockResolvedValue({ data: reviewed })
    transactionService.updateTransaction.mockResolvedValue({ data: {} })
    renderPage()
    await user.type(screen.getByLabelText('Question'), 'Find records matching: lunch')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    await screen.findByText('I found one matching record.')
    await user.click(screen.getByText('Evidence and limitations'))
    await user.click(screen.getByRole('button', { name: 'Prepare a change' }))
    await user.type(screen.getByLabelText('Question'), 'Change the amount')
    await user.click(screen.getByRole('button', { name: 'Ask for a change' }))
    await screen.findByRole('region', { name: 'Companion proposal' })
    await user.click(screen.getByRole('button', { name: 'Edit proposal' }))
    const amount = screen.getByLabelText('Amount')
    await user.clear(amount)
    await user.type(amount, '16.25')
    await user.click(screen.getByRole('button', { name: 'Save proposal edits' }))
    await waitFor(() => expect(companionService.reviewCompanionProposal).toHaveBeenCalledWith('Change the amount', 'current_month', expect.objectContaining({ proposed_values: { amount: '16.25' } })))
    expect(screen.getByText(/expenses \+€3.75/)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Confirm change' }))
    expect(await screen.findByRole('status')).toHaveTextContent('confirmed successfully')
    expect(transactionService.updateTransaction).toHaveBeenCalledWith(9, {
      amount: '16.25', transaction_date: '2026-10-08', category_key: 'expense_food', notes: 'Lunch',
      b_u_c: null, reflective_context: null, updated_at: '2026-10-08T10:00:00+00:00',
    })
    expect(companionService.queryCompanion).toHaveBeenNthCalledWith(3, 'Find records matching: lunch', 'current_month')
    expect(screen.getByText('The updated transaction is no longer in this match.')).toBeInTheDocument()
  })

  it('does not let users edit delete proposals and requires confirmation before replacing any proposal', async () => {
    const user = userEvent.setup()
    companionService.queryCompanion.mockResolvedValueOnce(matchingAnswer()).mockResolvedValueOnce(proposal('soft_delete_transaction', [], {}))
    renderPage()
    await user.type(screen.getByLabelText('Question'), 'Find records matching: lunch')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    await screen.findByText('I found one matching record.')
    await user.click(screen.getByText('Evidence and limitations'))
    await user.click(screen.getByRole('button', { name: 'Prepare a change' }))
    await user.type(screen.getByLabelText('Question'), 'Delete this record')
    await user.click(screen.getByRole('button', { name: 'Ask for a change' }))
    await screen.findByRole('region', { name: 'Companion proposal' })
    expect(screen.queryByRole('button', { name: 'Edit proposal' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Confirm deletion' })).toBeInTheDocument()
    await user.clear(screen.getByLabelText('Question'))
    await user.type(screen.getByLabelText('Question'), 'Another request')
    await user.click(screen.getByRole('button', { name: 'Ask for a change' }))
    expect(screen.getByRole('alert')).toHaveTextContent('Discard the active proposal')
    expect(companionService.queryCompanion).toHaveBeenCalledTimes(2)
    await user.click(screen.getByRole('button', { name: 'Keep proposal' }))
    expect(screen.getByRole('button', { name: 'Confirm deletion' })).toBeInTheDocument()
  })

  it('confirms a delete proposal only through the normal soft-delete command', async () => {
    const user = userEvent.setup()
    companionService.queryCompanion.mockResolvedValueOnce(matchingAnswer()).mockResolvedValueOnce(proposal('soft_delete_transaction', [], {}))
      .mockResolvedValueOnce(matchingAnswer('No matching records remain.'))
    transactionService.deleteTransaction.mockResolvedValue({ data: { deleted: true } })
    renderPage()
    await user.type(screen.getByLabelText('Question'), 'Find records matching: lunch')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    await screen.findByText('I found one matching record.')
    await user.click(screen.getByText('Evidence and limitations'))
    await user.click(screen.getByRole('button', { name: 'Prepare a change' }))
    await user.type(screen.getByLabelText('Question'), 'Delete this record')
    await user.click(screen.getByRole('button', { name: 'Ask for a change' }))
    await screen.findByRole('region', { name: 'Companion proposal' })
    await user.click(screen.getByRole('button', { name: 'Confirm deletion' }))
    expect(await screen.findByRole('status')).toHaveTextContent('confirmed successfully')
    expect(transactionService.deleteTransaction).toHaveBeenCalledWith(9)
    expect(transactionService.updateTransaction).not.toHaveBeenCalled()
    expect(companionService.queryCompanion).toHaveBeenNthCalledWith(3, 'Find records matching: lunch', 'current_month')
    expect(await screen.findByText('No matching records remain.')).toBeInTheDocument()
  })

  it('discards a stale proposal and refreshes the bounded matching evidence', async () => {
    const user = userEvent.setup()
    companionService.queryCompanion.mockResolvedValueOnce(matchingAnswer()).mockResolvedValueOnce(proposal())
      .mockResolvedValueOnce(matchingAnswer('The selected record has changed.'))
    transactionService.updateTransaction.mockRejectedValue({ status: 409, message: 'Conflict' })
    renderPage()
    await user.type(screen.getByLabelText('Question'), 'Find records matching: lunch')
    await user.click(screen.getByRole('button', { name: 'Ask Companion' }))
    await screen.findByText('I found one matching record.')
    await user.click(screen.getByText('Evidence and limitations'))
    await user.click(screen.getByRole('button', { name: 'Prepare a change' }))
    await user.type(screen.getByLabelText('Question'), 'Change the amount')
    await user.click(screen.getByRole('button', { name: 'Ask for a change' }))
    await screen.findByRole('region', { name: 'Companion proposal' })
    await user.click(screen.getByRole('button', { name: 'Confirm change' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('changed since the proposal')
    expect(screen.queryByRole('region', { name: 'Companion proposal' })).not.toBeInTheDocument()
    expect(await screen.findByText('The selected record has changed.')).toBeInTheDocument()
    expect(companionService.queryCompanion).toHaveBeenNthCalledWith(3, 'Find records matching: lunch', 'current_month')
  })
})
