import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import ExpenseForm from '../components/ExpenseForm.jsx'
import { expenseService } from '../services/expenseService.js'

function EditExpensePage() {
  const [expense, setExpense] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState('')
  const { id } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    let isCurrent = true

    async function loadExpense() {
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
  }, [id])

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
      'Are you sure you want to delete this expense?',
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
          <h1 className="mb-4">Edit Expense</h1>

          {isLoading && (
            <div className="text-center py-5" role="status">
              <div
                className="spinner-border text-primary"
                aria-hidden="true"
              />
              <p className="text-secondary mt-2 mb-0">Loading expense...</p>
            </div>
          )}

          {!isLoading && error && !expense && (
            <>
              <div className="alert alert-danger" role="alert">
                {error}
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
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}

              <ExpenseForm
                initialValues={expense}
                onSubmit={handleSubmit}
                onCancel={() => navigate('/expenses')}
                submitLabel="Save Changes"
                isSubmitting={isBusy}
              />

              <button
                className="btn btn-outline-danger mt-3"
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
