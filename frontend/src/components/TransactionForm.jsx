import { useEffect, useState } from 'react'

const CATEGORY_OPTIONS = {
  expense: [
    ['expense_transport', 'Transport'],
    ['expense_accommodation', 'Accommodation'],
    ['expense_food', 'Food'],
    ['expense_activities', 'Activities'],
    ['expense_other', 'Other'],
  ],
  income: [
    ['income_salary', 'Salary'],
    ['income_other', 'Other'],
  ],
}

function getTodayInMadrid() {
  const parts = new Intl.DateTimeFormat('en', {
    timeZone: 'Europe/Madrid',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(new Date())
  const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]))
  return `${values.year}-${values.month}-${values.day}`
}

function validate(formData) {
  const errors = {}
  if (!['income', 'expense'].includes(formData.transaction_type)) {
    errors.transaction_type = 'Choose income or expense.'
  }
  if (!/^(?:0|[1-9]\d{0,11})(?:\.\d{1,2})?$/.test(formData.amount)) {
    errors.amount = 'Enter a positive amount with up to 12 digits and 2 decimal places.'
  } else if (Number(formData.amount) <= 0) {
    errors.amount = 'Amount must be greater than zero.'
  }
  if (!formData.transaction_date) errors.transaction_date = 'Choose a date.'
  if (!CATEGORY_OPTIONS[formData.transaction_type]?.some(([key]) => key === formData.category_key)) {
    errors.category_key = 'Choose a category for this transaction type.'
  }
  return errors
}

function TransactionForm({ onSubmit, isSubmitting, fieldErrors = {}, successCount = 0, initialValues, typeReadOnly = false, onCancel, submitLabel = 'Save transaction', onValuesChange }) {
  const [formData, setFormData] = useState(() => ({
    transaction_type: 'expense',
    amount: '',
    transaction_date: getTodayInMadrid(),
    category_key: '',
    ...initialValues,
    notes: initialValues?.notes ?? '',
    b_u_c: initialValues?.b_u_c ?? '',
    reflective_context: initialValues?.reflective_context ?? '',
  }))
  const [clientErrors, setClientErrors] = useState({})
  const errors = { ...clientErrors, ...fieldErrors }
  const categories = CATEGORY_OPTIONS[formData.transaction_type] ?? CATEGORY_OPTIONS.expense

  useEffect(() => {
    if (successCount === 0) return
    setFormData((current) => ({
      transaction_type: current.transaction_type,
      amount: '',
      transaction_date: getTodayInMadrid(),
      category_key: '',
      notes: '',
      b_u_c: '',
      reflective_context: '',
    }))
    setClientErrors({})
  }, [successCount])

  function setField(name, value) {
    const next = { ...formData, [name]: value }
    setFormData(next)
    onValuesChange?.(next)
    setClientErrors((current) => ({ ...current, [name]: undefined }))
  }

  function handleTypeChange(event) {
    const transaction_type = event.target.value
    const next = {
      ...formData,
      transaction_type,
      category_key: '',
      ...(transaction_type === 'income' ? { b_u_c: '', reflective_context: '' } : {}),
    }
    setFormData(next)
    onValuesChange?.(next)
    setClientErrors((current) => ({ ...current, transaction_type: undefined, category_key: undefined }))
  }

  function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validate(formData)
    setClientErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    const submission = { ...formData }
    if (formData.transaction_type === 'expense') {
      submission.b_u_c = formData.b_u_c || null
      submission.reflective_context = formData.reflective_context || null
    } else {
      delete submission.b_u_c
      delete submission.reflective_context
    }
    onSubmit(submission)
  }

  function fieldAttributes(name) {
    return {
      'aria-invalid': Boolean(errors[name]),
      'aria-describedby': errors[name] ? `${name}-error` : undefined,
      className: `form-control${errors[name] ? ' is-invalid' : ''}`,
    }
  }

  function renderFieldError(name) {
    return errors[name] ? <div className="invalid-feedback" id={`${name}-error`}>{errors[name]}</div> : null
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <fieldset className="mb-3" disabled={isSubmitting}>
        <legend className="form-label fs-6">Type</legend>
        {['income', 'expense'].map((type) => (
          <div className="form-check form-check-inline" key={type}>
            <input
              className="form-check-input"
              id={`transaction-type-${type}`}
              type="radio"
              name="transaction_type"
              value={type}
              checked={formData.transaction_type === type}
              onChange={handleTypeChange}
              disabled={isSubmitting || typeReadOnly}
            />
            <label className="form-check-label" htmlFor={`transaction-type-${type}`}>
              {type === 'income' ? 'Income' : 'Expense'}
            </label>
          </div>
        ))}
        {renderFieldError('transaction_type')}
      </fieldset>

      <div className="mb-3">
        <label className="form-label" htmlFor="amount">Amount (€)</label>
        <input
          {...fieldAttributes('amount')}
          id="amount"
          name="amount"
          type="text"
          inputMode="decimal"
          placeholder="0.00"
          value={formData.amount}
          onChange={(event) => setField('amount', event.target.value)}
          disabled={isSubmitting}
          required
        />
        {renderFieldError('amount')}
      </div>

      <div className="mb-3">
        <label className="form-label" htmlFor="transaction_date">Date</label>
        <input
          {...fieldAttributes('transaction_date')}
          id="transaction_date"
          name="transaction_date"
          type="date"
          value={formData.transaction_date}
          onChange={(event) => setField('transaction_date', event.target.value)}
          disabled={isSubmitting}
          required
        />
        {renderFieldError('transaction_date')}
      </div>

      <div className="mb-3">
        <label className="form-label" htmlFor="category_key">Category</label>
        <select
          {...fieldAttributes('category_key')}
          id="category_key"
          name="category_key"
          value={formData.category_key}
          onChange={(event) => setField('category_key', event.target.value)}
          disabled={isSubmitting}
          required
        >
          <option value="">Select a category</option>
          {categories.map(([key, label]) => <option key={key} value={key}>{label}</option>)}
        </select>
        {renderFieldError('category_key')}
      </div>

      {formData.transaction_type === 'expense' && <>
        <div className="mb-3">
          <label className="form-label" htmlFor="b_u_c">Spending context <span className="text-secondary">(optional)</span></label>
          <select className={`form-select${errors.b_u_c ? ' is-invalid' : ''}`} id="b_u_c" name="b_u_c" value={formData.b_u_c} onChange={(event) => setField('b_u_c', event.target.value)} disabled={isSubmitting} aria-invalid={Boolean(errors.b_u_c)} aria-describedby={errors.b_u_c ? 'b_u_c-error' : undefined}>
            <option value="">Not set</option>
            <option value="bill">Bill</option>
            <option value="usage">Usage</option>
            <option value="choice">Choice</option>
          </select>
          {renderFieldError('b_u_c')}
        </div>
        <div className="mb-3">
          <label className="form-label" htmlFor="reflective_context">Reflective context <span className="text-secondary">(optional)</span></label>
          <select className={`form-select${errors.reflective_context ? ' is-invalid' : ''}`} id="reflective_context" name="reflective_context" value={formData.reflective_context} onChange={(event) => setField('reflective_context', event.target.value)} disabled={isSubmitting} aria-invalid={Boolean(errors.reflective_context)} aria-describedby={errors.reflective_context ? 'reflective_context-error' : undefined}>
            <option value="">Not set</option>
            <option value="need">Need</option>
            <option value="love">Love</option>
            <option value="like">Like</option>
            <option value="want">Want</option>
          </select>
          {renderFieldError('reflective_context')}
        </div>
        <div className="form-text mb-4">
          <p className="mb-1">Bill is a fixed obligation; Usage varies with use; Choice can be changed.</p>
          <p className="mb-1">Need supports wellbeing or functioning; Love creates lasting value or joy; Like creates temporary enjoyment; Want is mainly immediate gratification.</p>
          <p className="mb-0">Both fields are optional descriptive tools, not scores or judgements.</p>
        </div>
      </>}

      <div className="mb-4">
        <label className="form-label" htmlFor="notes">
          Notes <span className="text-secondary">(optional)</span>
        </label>
        <textarea
          className="form-control"
          id="notes"
          name="notes"
          rows="3"
          value={formData.notes}
          onChange={(event) => setField('notes', event.target.value)}
          disabled={isSubmitting}
        />
        {renderFieldError('notes')}
      </div>

      <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : submitLabel}
      </button>
      {onCancel && <button className="btn btn-outline-secondary ms-sm-2 mt-2 mt-sm-0" type="button" onClick={onCancel} disabled={isSubmitting}>Cancel</button>}
    </form>
  )
}

export default TransactionForm
