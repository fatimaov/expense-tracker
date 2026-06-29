import { useState } from 'react'
import { useNavigate } from 'react-router'
import ExpenseForm from '../components/ExpenseForm.jsx'
import { expenseService } from '../services/expenseService.js'

function AddExpensePage() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(expense) {
    setError('')
    setIsSubmitting(true)

    try {
      await expenseService.createExpense(expense)
      navigate('/expenses', { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Unable to create expense.')
      setIsSubmitting(false)
    }
  }

  return (
    <main className="container py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-md-8 col-lg-6">
          <h1 className="mb-4">Add Expense</h1>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          <ExpenseForm
            onSubmit={handleSubmit}
            onCancel={() => navigate('/expenses')}
            submitLabel="Add Expense"
            isSubmitting={isSubmitting}
          />
        </div>
      </div>
    </main>
  )
}

export default AddExpensePage
