import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import ExpenseForm from '../components/ExpenseForm.jsx'
import LoadingState from '../components/LoadingState.jsx'
import { expenseService } from '../services/expenseService.js'

function EditExpensePage() {
  const [expense, setExpense] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState('')
  const [loadAttempt, setLoadAttempt] = useState(0)
  const { id } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    let isCurrent = true

    async function loadExpense() {
      setIsLoading(true)
      setError('')

      try {
        const response = await expenseService.getExpense(id)

        if (isCurrent) {
          if (!response.expense) {
            throw new Error('Expense data was not returned.')
          }

          setExpense({
            ...response.expense,
            notes: response.expense.notes ?? '',
          })
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(requestError.message || 'Unable to load expense.')
        }
      } finally {
        if (isCurrent) setIsLoading(false)
      }
    }

    loadExpense()

    return () => {
      isCurrent = false
    }
  }, [id, loadAttempt])

  async function handleSubmit(updatedExpense) {
    setError('')
    setIsSubmitting(true)

    try {
      await expenseService.updateExpense(id, updatedExpense)
      navigate('/expenses', { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Unable to update expense.')
      setIsSubmitting(false)
    }
  }

  async function handleDelete() {
    const shouldDelete = window.confirm(
      `Delete “${expense.title}”? This action cannot be undone.`,
    )

    if (!shouldDelete) return

    setError('')
    setIsDeleting(true)

    try {
      await expenseService.deleteExpense(id)
      navigate('/expenses', { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Unable to delete expense.')
      setIsDeleting(false)
    }
  }

  const isBusy = isSubmitting || isDeleting

  return (
    <main className="container py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-md-8 col-lg-6">
          <h1 className="mb-2">Edit Expense</h1>
          <p className="text-secondary mb-4">
            Update the details, save your changes, or delete this expense.
          </p>

          {isLoading && <LoadingState message="Loading expense..." />}

          {!isLoading && error && !expense && (
            <>
              <div
                className="alert alert-danger"
                role="alert"
                aria-live="polite"
              >
                <p className="mb-2">{error}</p>
                <button
                  className="btn btn-outline-danger btn-sm"
                  type="button"
                  onClick={() => setLoadAttempt((attempt) => attempt + 1)}
                >
                  Try Again
                </button>
              </div>
              <button
                className="btn btn-outline-secondary"
                type="button"
                onClick={() => navigate('/expenses')}
              >
                Back to Expenses
              </button>
            </>
          )}

          {!isLoading && expense && (
            <>
              {error && (
                <div
                  className="alert alert-danger"
                  role="alert"
                  aria-live="polite"
                >
                  {error}
                </div>
              )}

              <ExpenseForm
                initialValues={expense}
                onSubmit={handleSubmit}
                onCancel={() => navigate('/expenses')}
                submitLabel="Save"
                submittingLabel="Saving..."
                isSubmitting={isBusy}
              />

              <button
                className="btn btn-outline-danger mt-4"
                type="button"
                onClick={handleDelete}
                disabled={isBusy}
              >
                {isDeleting ? 'Deleting...' : 'Delete Expense'}
              </button>
            </>
          )}
        </div>
      </div>
    </main>
  )
}

export default EditExpensePage
