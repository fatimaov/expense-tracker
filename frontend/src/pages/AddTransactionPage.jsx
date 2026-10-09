import { useRef, useState } from 'react'
import TransactionForm from '../components/TransactionForm.jsx'
import TransactionNavigation from '../components/TransactionNavigation.jsx'
import { transactionService } from '../services/transactionService.js'

const DRAFT_FIELD_LABELS = {
  transaction_type: 'transaction type',
  amount: 'amount',
  transaction_date: 'date',
  category_key: 'category',
  notes: 'notes',
}

function AddTransactionPage() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [fieldErrors, setFieldErrors] = useState({})
  const [pageError, setPageError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [successCount, setSuccessCount] = useState(0)
  const [describeOpen, setDescribeOpen] = useState(false)
  const [description, setDescription] = useState('')
  const [assistedError, setAssistedError] = useState('')
  const [assistedFieldError, setAssistedFieldError] = useState('')
  const [isCreatingDraft, setIsCreatingDraft] = useState(false)
  const [assistedDraft, setAssistedDraft] = useState(null)
  const submissionLock = useRef(false)
  const manualValuesRef = useRef(null)

  function hasManualValues(values = manualValuesRef.current) {
    if (!values) return false
    const parts = new Intl.DateTimeFormat('en', { timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date())
    const dateParts = Object.fromEntries(parts.map(({ type, value }) => [type, value]))
    const today = `${dateParts.year}-${dateParts.month}-${dateParts.day}`
    return Boolean(
      values.amount || values.category_key || values.notes?.trim() || values.b_u_c ||
      values.reflective_context || values.transaction_type !== 'expense' ||
      (values.transaction_date && values.transaction_date !== today)
    )
  }

  function confirmReplacement() {
    return !hasManualValues() || window.confirm('Replace the values in the manual form with this draft?')
  }

  function handleManualValuesChange(values) {
    manualValuesRef.current = values
  }

  async function handleCreateDraft(event) {
    event.preventDefault()
    setAssistedError('')
    setAssistedFieldError('')
    if (!description.trim()) {
      setAssistedFieldError('Enter a transaction description.')
      return
    }
    if (description.length > 1000) {
      setAssistedFieldError('Use 1,000 characters or fewer.')
      return
    }
    if (!confirmReplacement()) return
    const manualValuesAtStart = JSON.stringify(manualValuesRef.current ?? null)

    setIsCreatingDraft(true)
    try {
      const response = await transactionService.createTextDraft(description)
      if (JSON.stringify(manualValuesRef.current ?? null) !== manualValuesAtStart && hasManualValues() && !window.confirm('Replace the values entered in the manual form while the draft was being created?')) return
      setAssistedDraft(response.data)
      setFieldErrors({})
      setPageError('')
      setSuccessMessage('')
    } catch (requestError) {
      const message = requestError?.data?.error?.message || requestError.message
      setAssistedError(`${message || 'Unable to create a draft.'} Your text is still here, and you can enter the transaction manually.`)
    } finally {
      setIsCreatingDraft(false)
    }
  }

  function discardDraft() {
    setAssistedDraft(null)
    manualValuesRef.current = null
    setFieldErrors({})
    setPageError('')
  }

  async function handleSubmit(transaction) {
    if (submissionLock.current) return
    submissionLock.current = true
    setIsSubmitting(true)
    setFieldErrors({})
    setPageError('')
    setSuccessMessage('')
    try {
      await transactionService.createTransaction(transaction)
      setSuccessMessage('Transaction saved. You can add another one.')
      setSuccessCount((count) => count + 1)
      setAssistedDraft(null)
      manualValuesRef.current = null
    } catch (requestError) {
      const serverFields = requestError?.data?.error?.fields ?? {}
      const allowedFields = ['transaction_type', 'amount', 'transaction_date', 'category_key', 'notes', 'b_u_c', 'reflective_context']
      const errors = Object.fromEntries(Object.entries(serverFields).filter(([key]) => allowedFields.includes(key)))
      setFieldErrors(errors)
      if (Object.keys(serverFields).length === 0 || Object.keys(errors).length !== Object.keys(serverFields).length) {
        setPageError(requestError.message || 'Unable to save this transaction.')
      }
    } finally {
      submissionLock.current = false
      setIsSubmitting(false)
    }
  }

  return (
    <>
    <TransactionNavigation />
    <main className="container py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-md-8 col-lg-6">
          <h1 className="mb-2">Add transaction</h1>
          <p className="text-secondary mb-4">Record one-time income or an expense. The date defaults to today.</p>

          <section className="card mb-4" aria-labelledby="describe-transaction-heading">
            <div className="card-body">
              <h2 className="h5 mb-0" id="describe-transaction-heading">
                <button
                  className="btn btn-link p-0 text-decoration-none"
                  type="button"
                  aria-expanded={describeOpen}
                  aria-controls="describe-transaction-panel"
                  onClick={() => setDescribeOpen((open) => !open)}
                >
                  Describe a transaction
                </button>
              </h2>
              {describeOpen && <div id="describe-transaction-panel" className="pt-3">
                <p className="text-secondary">For example, “I spent €12.50 on lunch today”. You can describe it in your own words.</p>
                <form onSubmit={handleCreateDraft}>
                  <label className="form-label" htmlFor="transaction-description">Transaction description</label>
                  <textarea
                    className={`form-control${assistedFieldError ? ' is-invalid' : ''}`}
                    id="transaction-description"
                    rows="3"
                    maxLength={1000}
                    value={description}
                    onChange={(event) => { setDescription(event.target.value); setAssistedFieldError(''); setAssistedError('') }}
                    aria-invalid={Boolean(assistedFieldError)}
                    aria-describedby={assistedFieldError ? 'transaction-description-error transaction-description-count' : 'transaction-description-count'}
                  />
                  {assistedFieldError && <div className="invalid-feedback" id="transaction-description-error">{assistedFieldError}</div>}
                  <div id="transaction-description-count" className="form-text mb-3">{description.length}/1,000 characters</div>
                  {assistedError && <div className="alert alert-danger" role="alert">{assistedError}</div>}
                  <button className="btn btn-outline-primary" type="submit" disabled={isCreatingDraft}>
                    {isCreatingDraft ? 'Creating draft…' : 'Create draft'}
                  </button>
                </form>
              </div>}
            </div>
          </section>

          {assistedDraft && <div className="alert alert-info" role="status" aria-live="polite">
            <strong>Review before saving.</strong> Check every field, fill any missing details, then save through the normal transaction form.
            {assistedDraft.missing_fields?.length > 0 && <p className="mb-1 mt-2">Needs your input: {assistedDraft.missing_fields.map((field) => DRAFT_FIELD_LABELS[field] ?? field).join(', ')}.</p>}
            {assistedDraft.uncertainties?.length > 0 && <ul className="mb-2 mt-2">
              {assistedDraft.uncertainties.map(({ field, reason }) => <li key={field}><strong>{DRAFT_FIELD_LABELS[field] ?? field}:</strong> {reason}</li>)}
            </ul>}
            <button className="btn btn-sm btn-outline-secondary mt-2" type="button" onClick={discardDraft} disabled={isSubmitting}>Discard draft</button>
          </div>}

          {successMessage && <div className="alert alert-success" role="status" aria-live="polite">{successMessage}</div>}
          {pageError && <div className="alert alert-danger" role="alert" aria-live="polite">{pageError}</div>}

          <TransactionForm
            key={assistedDraft ? 'assisted-draft' : 'manual-form'}
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
            fieldErrors={fieldErrors}
            successCount={successCount}
            initialValues={assistedDraft ? {
              ...assistedDraft.draft,
              amount: assistedDraft.draft.amount ?? '',
              transaction_date: assistedDraft.draft.transaction_date ?? '',
              category_key: assistedDraft.draft.category_key ?? '',
              notes: assistedDraft.draft.notes ?? '',
              b_u_c: '',
              reflective_context: '',
            } : undefined}
            onValuesChange={handleManualValuesChange}
          />
        </div>
      </div>
    </main>
    </>
  )
}

export default AddTransactionPage
