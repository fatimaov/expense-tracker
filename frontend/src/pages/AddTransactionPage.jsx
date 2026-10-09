import { useRef, useState } from 'react'
import TransactionForm from '../components/TransactionForm.jsx'
import { transactionService } from '../services/transactionService.js'

function AddTransactionPage() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [fieldErrors, setFieldErrors] = useState({})
  const [pageError, setPageError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [successCount, setSuccessCount] = useState(0)
  const submissionLock = useRef(false)

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
    } catch (requestError) {
      const serverFields = requestError?.data?.error?.fields ?? {}
      const allowedFields = ['transaction_type', 'amount', 'transaction_date', 'category_key', 'notes']
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
    <main className="container py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-md-8 col-lg-6">
          <h1 className="mb-2">Add transaction</h1>
          <p className="text-secondary mb-4">Record one-time income or an expense. The date defaults to today.</p>

          {successMessage && <div className="alert alert-success" role="status" aria-live="polite">{successMessage}</div>}
          {pageError && <div className="alert alert-danger" role="alert" aria-live="polite">{pageError}</div>}

          <TransactionForm
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
            fieldErrors={fieldErrors}
            successCount={successCount}
          />
        </div>
      </div>
    </main>
  )
}

export default AddTransactionPage
