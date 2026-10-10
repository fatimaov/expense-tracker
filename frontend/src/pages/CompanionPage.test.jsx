import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router'
import CompanionPage from './CompanionPage.jsx'
import { companionService } from '../services/companionService.js'

vi.mock('../services/companionService.js', () => ({
  companionService: { queryCompanion: vi.fn() },
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
})
