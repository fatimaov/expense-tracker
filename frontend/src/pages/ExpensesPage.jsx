import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import EmptyState from '../components/EmptyState.jsx'
import ExpenseCard from '../components/ExpenseCard.jsx'
import { useAuth } from '../context/useAuth.js'
import { expenseService } from '../services/expenseService.js'

function ExpensesPage() {
  const [expenses, setExpenses] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const { logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    let isCurrent = true

    async function loadExpenses() {
      try {
        const response = await expenseService.getExpenses()

        if (isCurrent) {
          const sortedExpenses = [...(response.expenses ?? [])].sort((a, b) =>
            b.expense_date.localeCompare(a.expense_date),
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
  }, [])

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  return (
    <main className="container py-4">
      <div className="d-flex align-items-center justify-content-between gap-3 mb-4">
        <h1 className="mb-0">Expenses</h1>
        <div className="d-flex gap-2">
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

      {isLoading && (
        <div className="text-center py-5" role="status">
          <div className="spinner-border text-primary" aria-hidden="true" />
          <p className="text-secondary mt-2 mb-0">Loading expenses...</p>
        </div>
      )}

      {!isLoading && error && (
        <div className="alert alert-danger" role="alert">
          {error}
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
    </main>
  )
}

export default ExpensesPage
