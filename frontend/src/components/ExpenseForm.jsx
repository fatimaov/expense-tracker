import { useState } from 'react'

const EXPENSE_CATEGORIES = [
  'Transport',
  'Accommodation',
  'Food',
  'Activities',
  'Other',
]

function getToday() {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

function ExpenseForm({
  initialValues = {},
  onSubmit,
  onCancel,
  submitLabel = 'Save',
  submittingLabel = 'Saving...',
  isSubmitting = false,
}) {
  const [formData, setFormData] = useState({
    amount: '',
    title: '',
    expense_date: getToday(),
    category: '',
    notes: '',
    ...initialValues,
  })

  function handleChange(event) {
    const { name, value } = event.target
    setFormData((currentFormData) => ({
      ...currentFormData,
      [name]: value,
    }))
  }

  function handleSubmit(event) {
    event.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-3">
        <label className="form-label" htmlFor="amount">
          Amount (€)
        </label>
        <input
          className="form-control"
          id="amount"
          name="amount"
          type="number"
          min="0.01"
          step="0.01"
          inputMode="decimal"
          placeholder="0.00"
          value={formData.amount}
          onChange={handleChange}
          disabled={isSubmitting}
          autoFocus
          required
        />
      </div>

      <div className="mb-3">
        <label className="form-label" htmlFor="title">
          Title
        </label>
        <input
          className="form-control"
          id="title"
          name="title"
          type="text"
          placeholder="What did you spend on?"
          value={formData.title}
          onChange={handleChange}
          disabled={isSubmitting}
          required
        />
      </div>

      <div className="mb-3">
        <label className="form-label" htmlFor="expense_date">
          Date
        </label>
        <input
          className="form-control"
          id="expense_date"
          name="expense_date"
          type="date"
          value={formData.expense_date}
          onChange={handleChange}
          disabled={isSubmitting}
          required
        />
      </div>

      <div className="mb-3">
        <label className="form-label" htmlFor="category">
          Category
        </label>
        <select
          className="form-select"
          id="category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          disabled={isSubmitting}
          required
        >
          <option value="" disabled>
            Select a category
          </option>
          {EXPENSE_CATEGORIES.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-4">
        <label className="form-label" htmlFor="notes">
          Notes <span className="text-secondary">(optional)</span>
        </label>
        <textarea
          className="form-control"
          id="notes"
          name="notes"
          rows="3"
          placeholder="Add any useful details"
          value={formData.notes}
          onChange={handleChange}
          disabled={isSubmitting}
        />
      </div>

      <div className="d-grid d-sm-flex gap-2">
        <button
          className="btn btn-primary"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? submittingLabel : submitLabel}
        </button>
        {onCancel && (
          <button
            className="btn btn-outline-secondary"
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}

export default ExpenseForm
