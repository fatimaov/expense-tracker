import { useState } from 'react'
import TransactionNavigation from '../components/TransactionNavigation.jsx'
import { companionService } from '../services/companionService.js'
import { transactionService } from '../services/transactionService.js'

const MAX_QUESTION_LENGTH = 1000
const EXPENSE_CATEGORIES = [
  ['expense_transport', 'Transport'], ['expense_accommodation', 'Accommodation'],
  ['expense_food', 'Food'], ['expense_activities', 'Activities'], ['expense_other', 'Other'],
]
const INCOME_CATEGORIES = [['income_salary', 'Salary'], ['income_other', 'Other']]
const CONTEXT_OPTIONS = {
  b_u_c: [['bill', 'Bill'], ['usage', 'Usage'], ['choice', 'Choice']],
  reflective_context: [['need', 'Need'], ['love', 'Love'], ['like', 'Like'], ['want', 'Want']],
}

function formatPeriod(period) {
  if (!period?.start) return 'No transaction dates in this scope'
  return period.end_exclusive
    ? `${period.start} to ${period.end_exclusive} (end date exclusive)`
    : period.start
}

function EvidenceDetails({ evidence, selectedTargetId, onSelectTarget, selectionDisabled }) {
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
        {records?.length > 0 && <ul className="list-group mb-2">{records.map((record) => (
          <li key={record.id} className="list-group-item d-flex flex-wrap justify-content-between align-items-center gap-2">
            <span>
              {record.transaction_date} · {record.category_label ?? record.category_key} · {record.transaction_type === 'income' ? '+' : '−'}€{record.amount}
              {record.notes ? ` · ${record.notes}` : ''}
              {record.missing?.length ? ` · Missing: ${record.missing.join(', ')}` : ''}
            </span>
            {matchingCount !== undefined && <button
              className={`btn btn-sm ${selectedTargetId === record.id ? 'btn-secondary' : 'btn-outline-primary'}`}
              type="button"
              disabled={selectionDisabled}
              onClick={() => onSelectTarget(record)}
            >{selectedTargetId === record.id ? 'Selected target' : 'Prepare a change'}</button>}
          </li>
        ))}</ul>}
        <p className="mb-1">Excluded: {Object.entries(evidence.exclusions ?? {}).map(([name, count]) => `${name.replaceAll('_', ' ')} ${count}`).join(' · ') || 'None reported'}</p>
        {evidence.warnings?.length > 0 && <ul className="mb-0">{evidence.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>}
      </div>
    </details>
  )
}

function ProposalCard({ proposal, onCancel, onSave, onConfirm, isConfirming }) {
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [values, setValues] = useState(proposal.proposed_values)
  const isDelete = proposal.operation === 'soft_delete_transaction'
  const categoryOptions = proposal.current_record.transaction_type === 'income' ? INCOME_CATEGORIES : EXPENSE_CATEGORIES
  const operationLabel = {
    edit_transaction: 'Edit transaction',
    soft_delete_transaction: 'Soft-delete transaction',
    change_transaction_context: 'Change expense context',
  }[proposal.operation]

  function updateValue(field, value) {
    setValues((current) => ({ ...current, [field]: value }))
  }

  async function saveEdits(event) {
    event.preventDefault()
    const normalized = { ...values }
    for (const field of ['b_u_c', 'reflective_context']) {
      if (field in normalized && normalized[field] === '') normalized[field] = null
    }
    setIsSaving(true)
    try {
      if (await onSave({ ...proposal, proposed_values: normalized })) setIsEditing(false)
    } finally {
      setIsSaving(false)
    }
  }

  const valueFields = proposal.affected_fields.map((field) => {
    const label = {
      amount: 'Amount', transaction_date: 'Date', category_key: 'Category', notes: 'Notes',
      b_u_c: 'B/U/C', reflective_context: 'Reflective context',
    }[field]
    const value = values[field] ?? ''
    if (field === 'category_key') return <div className="mb-3" key={field}>
      <label className="form-label" htmlFor={`proposal-${field}`}>{label}</label>
      <select id={`proposal-${field}`} className="form-select" value={value} onChange={(event) => updateValue(field, event.target.value)}>
        {categoryOptions.map(([key, name]) => <option value={key} key={key}>{name}</option>)}
      </select>
    </div>
    if (field === 'b_u_c' || field === 'reflective_context') return <div className="mb-3" key={field}>
      <label className="form-label" htmlFor={`proposal-${field}`}>{label}</label>
      <select id={`proposal-${field}`} className="form-select" value={value} onChange={(event) => updateValue(field, event.target.value)}>
        <option value="">None</option>
        {CONTEXT_OPTIONS[field].map(([key, name]) => <option value={key} key={key}>{name}</option>)}
      </select>
    </div>
    if (field === 'notes') return <div className="mb-3" key={field}>
      <label className="form-label" htmlFor={`proposal-${field}`}>{label}</label>
      <textarea id={`proposal-${field}`} className="form-control" rows="2" value={value} onChange={(event) => updateValue(field, event.target.value)} />
    </div>
    return <div className="mb-3" key={field}>
      <label className="form-label" htmlFor={`proposal-${field}`}>{label}</label>
      <input id={`proposal-${field}`} className="form-control" type={field === 'transaction_date' ? 'date' : 'text'} inputMode={field === 'amount' ? 'decimal' : undefined} value={value} onChange={(event) => updateValue(field, event.target.value)} />
    </div>
  })

  return (
    <section className="card border-primary mt-4" aria-label="Companion proposal">
      <div className="card-body">
        <h2 className="h5 card-title">Review proposal: {operationLabel}</h2>
        <p className="mb-2">No change has been applied. Review this proposal before confirming it.</p>
        <dl className="row">
          <dt className="col-sm-3">Target</dt>
          <dd className="col-sm-9">{proposal.current_record.transaction_date} · {proposal.current_record.transaction_type} · {proposal.current_record.category_label} · {proposal.current_record.notes || 'No notes'} · {proposal.current_record.transaction_type === 'income' ? '+' : '−'}€{proposal.current_record.amount} (record #{proposal.target_transaction_id})</dd>
          <dt className="col-sm-3">Affected fields</dt>
          <dd className="col-sm-9">{proposal.affected_fields.join(', ') || 'Soft-delete operation'}</dd>
          <dt className="col-sm-3">Current values</dt>
          <dd className="col-sm-9">{proposal.affected_fields.map((field) => `${field}: ${proposal.current_record[field] ?? 'None'}`).join(' · ') || 'This record will be marked deleted.'}</dd>
          <dt className="col-sm-3">Proposed values</dt>
          <dd className="col-sm-9">{proposal.affected_fields.map((field) => `${field}: ${proposal.proposed_values[field] ?? 'None'}`).join(' · ') || 'Soft-delete this record.'}</dd>
          <dt className="col-sm-3">Uncertainty</dt>
          <dd className="col-sm-9">{proposal.uncertainty || 'No uncertainty reported.'}</dd>
          <dt className="col-sm-3">Proposal version</dt>
          <dd className="col-sm-9"><code>{proposal.proposal_version}</code></dd>
          <dt className="col-sm-3">Expected effect</dt>
          <dd className="col-sm-9">
            {proposal.expected_effect?.message && <p className="mb-1">{proposal.expected_effect.message}</p>}
            {proposal.expected_effect?.monthly_deltas?.length > 0
              ? <ul className="mb-0">{proposal.expected_effect.monthly_deltas.map((item) => <li key={item.month}>{item.month}: income {item.income_delta >= 0 ? '+' : ''}€{item.income_delta}; expenses {item.expense_delta >= 0 ? '+' : ''}€{item.expense_delta}; net {item.net_delta >= 0 ? '+' : ''}€{item.net_delta}{item.category_deltas?.length ? ` · category changes ${item.category_deltas.map((delta) => `${delta.category_key} ${delta.delta}`).join(', ')}` : ''}</li>)}</ul>
              : !proposal.expected_effect?.message && <span>Unavailable</span>}
          </dd>
        </dl>

        {isEditing && !isDelete && <form onSubmit={saveEdits} className="border-top pt-3">
          <h3 className="h6">Edit proposed values</h3>
          {valueFields}
          <p className="form-text">The deterministic effect above reflects the Companion proposal. Review the edited values carefully; normal transaction validation runs again when you confirm.</p>
          <button className="btn btn-primary me-2" type="submit" disabled={isSaving}>{isSaving ? 'Checking edits…' : 'Save proposal edits'}</button>
          <button className="btn btn-outline-secondary" type="button" onClick={() => setIsEditing(false)} disabled={isSaving}>Discard edits</button>
        </form>}

        <div className="d-flex flex-wrap gap-2 border-top pt-3">
          {!isDelete && !isEditing && <button className="btn btn-outline-primary" type="button" onClick={() => setIsEditing(true)}>Edit proposal</button>}
          <button className="btn btn-outline-secondary" type="button" onClick={onCancel} disabled={isConfirming}>Cancel proposal</button>
          {!isEditing && <button className="btn btn-primary" type="button" onClick={onConfirm} disabled={isConfirming}>
            {isConfirming ? 'Confirming…' : isDelete ? 'Confirm deletion' : 'Confirm change'}
          </button>}
        </div>
      </div>
    </section>
  )
}

function CompanionPage() {
  const [question, setQuestion] = useState('')
  const [scope, setScope] = useState('current_month')
  const [response, setResponse] = useState(null)
  const [proposal, setProposal] = useState(null)
  const [proposalQuestion, setProposalQuestion] = useState('')
  const [selectedTarget, setSelectedTarget] = useState(null)
  const [matchingQuestion, setMatchingQuestion] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [fieldError, setFieldError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isConfirming, setIsConfirming] = useState(false)
  const [confirmDiscard, setConfirmDiscard] = useState(false)

  async function performQuery(targetId = selectedTarget?.id) {
    const trimmed = question.trim()
    setFieldError('')
    setError('')
    setSuccess('')
    setIsSubmitting(true)
    try {
      const result = targetId === null || targetId === undefined
        ? await companionService.queryCompanion(trimmed, scope)
        : await companionService.queryCompanion(trimmed, scope, targetId)
      const data = result?.data ?? null
      setResponse(data)
      const nextProposal = data?.kind === 'proposal' ? data.proposal : null
      setProposal(nextProposal)
      setProposalQuestion(nextProposal ? trimmed : '')
      setConfirmDiscard(false)
      if (!targetId && data?.evidence?.matching_count !== undefined) setMatchingQuestion(trimmed)
    } catch (requestError) {
      setError(requestError.message || 'The Companion could not answer. Try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || trimmed.length > MAX_QUESTION_LENGTH) {
      setFieldError('Enter a question of 1 to 1,000 characters.')
      setError('')
      return
    }
    if (proposal) {
      setConfirmDiscard(true)
      return
    }
    await performQuery()
  }

  async function discardAndAsk() {
    setProposal(null)
    setResponse(null)
    setConfirmDiscard(false)
    await performQuery()
  }

  async function handleConfirmProposal() {
    if (!proposal || isConfirming) return
    setError('')
    setSuccess('')
    setIsConfirming(true)
    try {
      const current = proposal.current_record
      if (proposal.operation === 'soft_delete_transaction') {
        await transactionService.deleteTransaction(proposal.target_transaction_id)
      } else {
        const values = { ...current, ...proposal.proposed_values }
        await transactionService.updateTransaction(proposal.target_transaction_id, {
          amount: values.amount,
          transaction_date: values.transaction_date,
          category_key: values.category_key,
          notes: values.notes ?? '',
          b_u_c: values.b_u_c ?? null,
          reflective_context: values.reflective_context ?? null,
          updated_at: proposal.proposal_version,
        })
      }
      setProposal(null)
      setResponse(null)
      setSelectedTarget(null)
      setSuccess('The transaction change was confirmed successfully.')
      if (matchingQuestion) {
        try {
          const refreshed = await companionService.queryCompanion(matchingQuestion, scope)
          setResponse(refreshed?.data ?? null)
        } catch {
          setError('The transaction was changed, but the matching Companion evidence could not be refreshed. Ask again to reload it.')
        }
      }
    } catch (requestError) {
      setProposal(null)
      setProposalQuestion('')
      setResponse(null)
      setSelectedTarget(null)
      if (requestError.status === 409) setError('This transaction changed since the proposal was prepared. The proposal was discarded; refresh the record and ask again.')
      else if (requestError.status === 403 || requestError.status === 404) setError('This transaction is no longer available. The proposal was discarded; select a current record and ask again.')
      else setError(requestError.message || 'The transaction change failed validation. The proposal was discarded; review the record and ask again.')
      if (matchingQuestion) {
        try {
          const refreshed = await companionService.queryCompanion(matchingQuestion, scope)
          setResponse(refreshed?.data ?? null)
        } catch {
          // The failure message already asks the user to start a fresh request.
        }
      }
    } finally {
      setIsConfirming(false)
    }
  }

  async function handleSaveProposal(nextProposal) {
    setError('')
    try {
      const result = await companionService.reviewCompanionProposal(proposalQuestion, scope, nextProposal)
      const data = result?.data
      if (data?.kind !== 'proposal') throw new Error('The edited proposal could not be reviewed.')
      setProposal(data.proposal)
      setResponse(data)
      return true
    } catch (requestError) {
      if (requestError.status === 409) {
        setProposal(null)
        setProposalQuestion('')
        setResponse(null)
        setSelectedTarget(null)
        setError('This transaction changed while you were editing. The proposal was discarded; select the current record and ask again.')
        if (matchingQuestion) {
          try {
            const refreshed = await companionService.queryCompanion(matchingQuestion, scope)
            setResponse(refreshed?.data ?? null)
          } catch {
            // The stale proposal is discarded even if the read-only refresh fails.
          }
        }
      } else {
        setError(requestError.message || 'These proposal values are invalid. Correct them and try again.')
      }
      return false
    }
  }

  return (
    <>
      <TransactionNavigation />
      <main className="container py-4" aria-labelledby="companion-title">
        <h1 id="companion-title">Companion</h1>
        <p>Ask about your transaction history, or select one matching record to request a reviewable change.</p>
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
            <div id="companion-question-help" className="form-text">{question.length}/{MAX_QUESTION_LENGTH} characters. {selectedTarget ? 'For the selected record, clearly request an amount, date, category, or notes edit; deletion; or an expense-context change. Example: “Change the amount to €18.50”.' : 'Supported topics include totals, category breakdowns, missing expense context, and “Find records matching: …”.'}</div>
            {fieldError && <div id="companion-question-error" className="invalid-feedback">{fieldError}</div>}
          </div>
          {selectedTarget && <div className="alert alert-info" role="status">
            Preparing a request for {selectedTarget.transaction_date} · {selectedTarget.category_label} · €{selectedTarget.amount} (record #{selectedTarget.id}).
            <button className="btn btn-sm btn-link" type="button" onClick={() => setSelectedTarget(null)}>Clear selected record</button>
          </div>}
          <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? <><span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />Asking…</> : selectedTarget ? 'Ask for a change' : 'Ask Companion'}
          </button>
        </form>
        {confirmDiscard && <div className="alert alert-warning mt-3" role="alert">
          <p className="mb-2">Discard the active proposal before starting this question?</p>
          <button className="btn btn-sm btn-warning me-2" type="button" onClick={discardAndAsk} disabled={isSubmitting}>Discard proposal and ask</button>
          <button className="btn btn-sm btn-outline-secondary" type="button" onClick={() => setConfirmDiscard(false)}>Keep proposal</button>
        </div>}
        {isSubmitting && <p className="mt-3" role="status" aria-live="polite">Preparing an answer from your transaction evidence…</p>}
        {error && <div className="alert alert-danger mt-3" role="alert" aria-live="polite">{error}</div>}
        {success && <div className="alert alert-success mt-3" role="status" aria-live="polite">{success}</div>}
        {response && <section className="card mt-4" aria-label="Companion response">
          <div className="card-body">
            <h2 className="h5 card-title">{response.kind === 'clarification' ? 'Clarification' : response.kind === 'proposal' ? 'Change proposal' : 'Answer'}</h2>
            <p className="text-body-secondary mb-2">{response.scope === 'all' ? 'All history' : 'Current month'} · {formatPeriod(response.period)}</p>
            <p className="card-text" aria-live="polite">{response.message}</p>
            {response.evidence && <EvidenceDetails evidence={response.evidence} selectedTargetId={selectedTarget?.id} selectionDisabled={!!proposal || isSubmitting} onSelectTarget={(record) => {
              setSelectedTarget(record)
              setQuestion('')
              setFieldError('')
              setError('')
              setProposal(null)
              setResponse(response)
            }} />}
          </div>
        </section>}
        {proposal && <ProposalCard key={`${proposal.proposal_version}-${JSON.stringify(proposal.proposed_values)}`} proposal={proposal} onCancel={() => {
          setProposal(null)
          setProposalQuestion('')
          setResponse(null)
          setSuccess('Proposal cancelled. No transaction was changed.')
        }} onSave={handleSaveProposal} onConfirm={handleConfirmProposal} isConfirming={isConfirming} />}
      </main>
    </>
  )
}

export default CompanionPage
