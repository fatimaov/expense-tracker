import { useEffect, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router'
import LoadingState from '../components/LoadingState.jsx'
import TransactionForm from '../components/TransactionForm.jsx'
import TransactionNavigation from '../components/TransactionNavigation.jsx'
import { transactionService } from '../services/transactionService.js'

function EditTransactionPage() {
  const [transaction, setTransaction] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [conflict, setConflict] = useState(false)
  const [loadAttempt, setLoadAttempt] = useState(0)
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    let active = true
    async function load() {
      setIsLoading(true)
      setError('')
      try {
        const response = await transactionService.getTransaction(id)
        if (active) setTransaction({ ...response.data, notes: response.data.notes ?? '' })
      } catch (requestError) {
        if (active) setError(requestError.message || 'Unable to load transaction.')
      } finally {
        if (active) setIsLoading(false)
      }
    }
    load()
    return () => { active = false }
  }, [id, loadAttempt])

  async function handleSubmit(values) {
    setIsSubmitting(true)
    setError('')
    setConflict(false)
    try {
      await transactionService.updateTransaction(id, {
        amount: values.amount,
        transaction_date: values.transaction_date,
        category_key: values.category_key,
        notes: values.notes,
        ...(values.transaction_type === 'expense' ? {
          b_u_c: values.b_u_c,
          reflective_context: values.reflective_context,
        } : {}),
        updated_at: transaction.updated_at,
      })
      navigate('/transactions', { replace: true, state: { successMessage: 'Transaction updated.', ...location.state } })
    } catch (requestError) {
      if (requestError.status === 409) {
        setConflict(true)
        try {
          const latest = await transactionService.getTransaction(id)
          setTransaction({ ...latest.data, notes: latest.data.notes ?? '' })
        } catch (refreshError) {
          setError(refreshError.message || 'Unable to refresh the latest transaction.')
        }
      } else {
        setError(requestError.message || 'Unable to update this transaction.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return <>
    <TransactionNavigation />
    <main className="container py-4">
      <div className="row justify-content-center"><div className="col-12 col-md-8 col-lg-6">
        <h1 className="mb-2">Edit transaction</h1>
        <p className="text-secondary mb-4">Update amount, date, category, notes, or optional expense context. Transaction type cannot be changed.</p>
        {isLoading && <LoadingState message="Loading transaction..." />}
        {!isLoading && error && !transaction && <div className="alert alert-danger" role="alert"><p>{error}</p><button className="btn btn-outline-danger btn-sm" type="button" onClick={() => setLoadAttempt((attempt) => attempt + 1)}>Try again</button></div>}
        {!isLoading && transaction && <>
          {conflict && <div className="alert alert-warning" role="alert" aria-live="assertive">This transaction changed elsewhere. We refreshed it below; review the latest values and submit again to save your changes.</div>}
          {error && <div className="alert alert-danger" role="alert">{error}</div>}
          <TransactionForm key={transaction.updated_at} initialValues={{ ...transaction, category_key: transaction.category_key }} typeReadOnly onSubmit={handleSubmit} isSubmitting={isSubmitting} submitLabel="Save changes" onCancel={() => navigate('/transactions')} />
        </>}
      </div></div>
    </main>
  </>
}

export default EditTransactionPage
