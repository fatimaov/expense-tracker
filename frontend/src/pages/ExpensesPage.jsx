import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import EmptyState from '../components/EmptyState.jsx'
import ExpenseCard from '../components/ExpenseCard.jsx'
import LoadingState from '../components/LoadingState.jsx'
import { useAuth } from '../context/useAuth.js'
import { expenseService } from '../services/expenseService.js'

function ExpensesPage() {
  const [expenses, setExpenses] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [loadAttempt, setLoadAttempt] = useState(0)
  const { logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    let isCurrent = true

    async function loadExpenses() {
      setIsLoading(true)
      setError('')

      try {
        const response = await expenseService.getExpenses()

        if (isCurrent) {
          const sortedExpenses = [...(response.expenses ?? [])].sort(
            (a, b) =>
              b.expense_date.localeCompare(a.expense_date) ||
              b.created_at.localeCompare(a.created_at),
          )
          setExpenses(sortedExpenses)
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(requestError.message || 'Unable to load expenses.')
        }
      } finally {
        if (isCurrent) setIsLoading(false)
      }
    }

    loadExpenses()

    return () => {
      isCurrent = false
    }
  }, [loadAttempt])

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  return (
    <main className="container py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-lg-10 col-xl-8">
          <div className="d-flex flex-column flex-sm-row align-items-stretch align-items-sm-center justify-content-between gap-3 mb-4">
            <h1 className="mb-0">Expenses</h1>
            <div className="d-grid d-sm-flex gap-2">
              {!isLoading && !error && expenses.length > 0 && (
                <Link className="btn btn-primary" to="/expenses/new">
                  Add Expense
                </Link>
              )}
              <button
                className="btn btn-outline-secondary"
                type="button"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </div>

          {isLoading && <LoadingState message="Loading expenses..." />}

          {!isLoading && error && (
            <div className="alert alert-danger" role="alert" aria-live="polite">
              <p className="mb-2">{error}</p>
              <button
                className="btn btn-outline-danger btn-sm"
                type="button"
                onClick={() => setLoadAttempt((attempt) => attempt + 1)}
              >
                Try Again
              </button>
            </div>
          )}

          {!isLoading && !error && expenses.length === 0 && (
            <EmptyState onAddExpense={() => navigate('/expenses/new')} />
          )}

          {!isLoading && !error && expenses.length > 0 && (
            <div className="d-grid gap-3">
              {expenses.map((expense) => (
                <ExpenseCard
                  key={expense.id}
                  expense={expense}
                  onEdit={() => navigate(`/expenses/${expense.id}/edit`)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  )
}

export default ExpensesPage
