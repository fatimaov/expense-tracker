import { useState } from 'react'
import TransactionNavigation from '../components/TransactionNavigation.jsx'
import { companionService } from '../services/companionService.js'

const MAX_QUESTION_LENGTH = 1000

function formatPeriod(period) {
  if (!period?.start) return 'No transaction dates in this scope'
  return period.end_exclusive
    ? `${period.start} to ${period.end_exclusive} (end date exclusive)`
    : period.start
}

function EvidenceDetails({ evidence }) {
  const totals = evidence.totals ?? evidence.total
  const { category_totals: categories, records, matching_count: matchingCount, missing_context_count: missingCount } = evidence
  return (
    <details className="mt-3">
      <summary className="fw-semibold">Evidence and limitations</summary>
      <div className="pt-3">
        {evidence.included_record_count !== undefined && <p>Included {evidence.included_record_count} {evidence.transaction_type ?? ''} transaction{evidence.included_record_count === 1 ? '' : 's'} in this subset.</p>}
        {totals && <p className="mb-2">Included totals: {Object.entries(totals).map(([name, value]) => `${name}: €${value}`).join(' · ')}</p>}
        {categories && <ul className="mb-2">{categories.map((item) => <li key={item.category_key}>{item.category_label} ({item.transaction_type}): €{item.total}</li>)}</ul>}
        {matchingCount !== undefined && <p>{matchingCount} matching record{matchingCount === 1 ? '' : 's'} found{evidence.truncated ? ' (showing the 25 newest).' : '.'}</p>}
        {missingCount !== undefined && <p>{missingCount} expense{missingCount === 1 ? '' : 's'} missing optional context{evidence.truncated ? ' (showing the 25 newest).' : '.'}</p>}
        {records?.length > 0 && <ul className="mb-2">{records.map((record) => (
          <li key={record.id}>
            {record.transaction_date} · {record.category_label ?? record.category_key} · €{record.amount}
            {record.notes ? ` · ${record.notes}` : ''}
            {record.missing?.length ? ` · Missing: ${record.missing.join(', ')}` : ''}
          </li>
        ))}</ul>}
        <p className="mb-1">Excluded: {Object.entries(evidence.exclusions ?? {}).map(([name, count]) => `${name.replaceAll('_', ' ')} ${count}`).join(' · ') || 'None reported'}</p>
        {evidence.warnings?.length > 0 && <ul className="mb-0">{evidence.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>}
      </div>
    </details>
  )
}

function CompanionPage() {
  const [question, setQuestion] = useState('')
  const [scope, setScope] = useState('current_month')
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')
  const [fieldError, setFieldError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || trimmed.length > MAX_QUESTION_LENGTH) {
      setFieldError('Enter a question of 1 to 1,000 characters.')
      setError('')
      return
    }
    setFieldError('')
    setError('')
    setIsSubmitting(true)
    try {
      const result = await companionService.queryCompanion(trimmed, scope)
      setResponse(result?.data ?? null)
    } catch (requestError) {
      setError(requestError.message || 'The Companion could not answer. Try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <TransactionNavigation />
      <main className="container py-4" aria-labelledby="companion-title">
        <h1 id="companion-title">Companion</h1>
        <p>Ask a read-only question about your transaction history. Answers use the selected scope and available records.</p>
        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-3">
            <label className="form-label" htmlFor="companion-scope">Scope</label>
            <select id="companion-scope" className="form-select" value={scope} onChange={(event) => setScope(event.target.value)}>
              <option value="current_month">Current month</option>
              <option value="all">All history</option>
            </select>
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="companion-question">Question</label>
            <textarea id="companion-question" className={`form-control${fieldError ? ' is-invalid' : ''}`} rows="3" maxLength={MAX_QUESTION_LENGTH} value={question} onChange={(event) => setQuestion(event.target.value)} aria-describedby="companion-question-help companion-question-error" />
            <div id="companion-question-help" className="form-text">{question.length}/{MAX_QUESTION_LENGTH} characters. Supported topics include totals, category breakdowns, missing expense context, and “Find records matching: …”.</div>
            {fieldError && <div id="companion-question-error" className="invalid-feedback">{fieldError}</div>}
          </div>
          <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? <><span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />Asking…</> : 'Ask Companion'}
          </button>
        </form>
        {isSubmitting && <p className="mt-3" role="status" aria-live="polite">Preparing an answer from your transaction evidence…</p>}
        {error && <div className="alert alert-danger mt-3" role="alert" aria-live="polite">{error}</div>}
        {response && <section className="card mt-4" aria-label="Companion response">
          <div className="card-body">
            <h2 className="h5 card-title">{response.kind === 'clarification' ? 'Clarification' : 'Answer'}</h2>
            <p className="text-body-secondary mb-2">{response.scope === 'all' ? 'All history' : 'Current month'} · {formatPeriod(response.period)}</p>
            <p className="card-text" aria-live="polite">{response.message}</p>
            {response.evidence && <EvidenceDetails evidence={response.evidence} />}
          </div>
        </section>}
      </main>
    </>
  )
}

export default CompanionPage
