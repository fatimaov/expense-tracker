import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router'
import LoadingState from '../components/LoadingState.jsx'
import TransactionNavigation from '../components/TransactionNavigation.jsx'
import { transactionService } from '../services/transactionService.js'

const PAGE_SIZE = 25
const CONTEXT_LABELS = {
  b_u_c: { bill: 'Bill', usage: 'Usage', choice: 'Choice' },
  reflective_context: { need: 'Need', love: 'Love', like: 'Like', want: 'Want' },
}

function formatAmount(value) {
  const [whole, fraction = ''] = String(value).split('.')
  const groupedWhole = whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return `${groupedWhole}.${fraction.padEnd(2, '0')}`
}

function TransactionHistoryPage() {
  const location = useLocation()
  const [scope, setScope] = useState(location.state?.scope ?? 'current_month')
  const [page, setPage] = useState(location.state?.page ?? 1)
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [loadAttempt, setLoadAttempt] = useState(0)
  const [selectedDelete, setSelectedDelete] = useState(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [success, setSuccess] = useState('')
  const [deleteError, setDeleteError] = useState('')

  useEffect(() => {
    if (location.state?.successMessage) setSuccess(location.state.successMessage)
  }, [location.state])

  useEffect(() => {
    let current = true
    async function load() {
      setIsLoading(true)
      setError('')
      try {
        const response = await transactionService.getTransactions({ scope, page, pageSize: PAGE_SIZE })
        if (current) setResult(response)
      } catch (requestError) {
        if (current) setError(requestError.message || 'Unable to load transaction history.')
      } finally {
        if (current) setIsLoading(false)
      }
    }
    load()
    return () => { current = false }
  }, [scope, page, loadAttempt])

  function changeScope(nextScope) {
    setScope(nextScope)
    setPage(1)
    setSuccess('')
  }

  async function confirmDelete() {
    if (!selectedDelete || isDeleting) return
    setIsDeleting(true)
    setDeleteError('')
    try {
      await transactionService.deleteTransaction(selectedDelete.id)
      setSelectedDelete(null)
      setSuccess('Transaction deleted.')
      setPage(1)
      setLoadAttempt((attempt) => attempt + 1)
    } catch (requestError) {
      setDeleteError(requestError.message || 'Unable to delete this transaction.')
    } finally {
      setIsDeleting(false)
    }
  }

  const rows = result?.data ?? []
  const meta = result?.meta
  const summary = meta?.summary

  return (
    <>
      <TransactionNavigation />
      <main className="container py-4">
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
          <div><h1 className="mb-1">Transaction history</h1><p className="text-secondary mb-0">Review and manage your income and expenses.</p></div>
          <Link className="btn btn-primary" to="/transactions/new">Add transaction</Link>
        </div>

        {success && <div className="alert alert-success" role="status" aria-live="polite">{success}</div>}
        <div className="btn-group mb-4" role="group" aria-label="History scope">
          <button className={`btn ${scope === 'current_month' ? 'btn-primary' : 'btn-outline-primary'}`} type="button" aria-pressed={scope === 'current_month'} onClick={() => changeScope('current_month')}>Current month</button>
          <button className={`btn ${scope === 'all' ? 'btn-primary' : 'btn-outline-primary'}`} type="button" aria-pressed={scope === 'all'} onClick={() => changeScope('all')}>All history</button>
        </div>

        {summary && !error && <section className="card mb-4" aria-label={`${scope === 'all' ? 'All history' : 'Current month'} summary`}>
          <div className="card-body">
            <h2 className="h5">{scope === 'all' ? 'All history' : 'Current month'} totals</h2>
            <div className="row g-3">
              <div className="col-6 col-lg-3"><span className="text-secondary d-block">Records</span><strong>{summary.record_count}</strong></div>
              <div className="col-6 col-lg-3"><span className="text-secondary d-block">Income</span><strong>+€{formatAmount(summary.total_income)}</strong></div>
              <div className="col-6 col-lg-3"><span className="text-secondary d-block">Expenses</span><strong>−€{formatAmount(summary.total_expense)}</strong></div>
              <div className="col-12 col-lg-3"><span className="text-secondary d-block">By category</span>
                {summary.category_totals.length ? <ul className="list-unstyled mb-0">{summary.category_totals.map((item) => <li key={item.category_key}>{item.category_label}: {item.transaction_type === 'income' ? '+' : '−'}€{formatAmount(item.total)}</li>)}</ul> : <span>—</span>}
              </div>
            </div>
          </div>
        </section>}

        {isLoading && <LoadingState message="Loading transaction history..." />}
        {!isLoading && error && <div className="alert alert-danger" role="alert"><p>{error}</p><button className="btn btn-outline-danger btn-sm" type="button" onClick={() => setLoadAttempt((attempt) => attempt + 1)}>Try again</button></div>}
        {!isLoading && !error && rows.length === 0 && <div className="alert alert-info" role="status">No transactions in {scope === 'all' ? 'your history' : 'the current month'} yet.</div>}

        {!isLoading && !error && rows.length > 0 && <>
          <div className="table-responsive">
            <table className="table table-striped align-middle">
              <thead><tr><th scope="col">Date</th><th scope="col">Type</th><th scope="col">Category</th><th scope="col">Notes</th><th scope="col" className="text-end">Amount</th><th scope="col">Actions</th></tr></thead>
              <tbody>{rows.map((transaction) => <tr key={transaction.id}>
                <td>{transaction.transaction_date}</td>
                <td><span className={`badge ${transaction.transaction_type === 'income' ? 'text-bg-success' : 'text-bg-secondary'}`}>{transaction.transaction_type === 'income' ? 'Income' : 'Expense'}</span></td>
                <td>
                  <div>{transaction.category_label}</div>
                  {(transaction.b_u_c || transaction.reflective_context) && <div className="mt-1 d-flex flex-wrap gap-1">
                    {transaction.b_u_c && <span className="badge text-bg-light text-dark border">{CONTEXT_LABELS.b_u_c[transaction.b_u_c]}</span>}
                    {transaction.reflective_context && <span className="badge text-bg-light text-dark border">{CONTEXT_LABELS.reflective_context[transaction.reflective_context]}</span>}
                  </div>}
                </td>
                <td>{transaction.notes || '—'}</td>
                <td className={`text-end fw-semibold ${transaction.transaction_type === 'income' ? 'text-success' : 'text-danger'}`}>{transaction.transaction_type === 'income' ? '+' : '−'}€{formatAmount(transaction.amount)}</td>
                <td><div className="d-flex gap-2"><Link className="btn btn-sm btn-outline-primary" to={`/transactions/${transaction.id}/edit`} state={{ scope, page }}>Edit</Link><button className="btn btn-sm btn-outline-danger" type="button" onClick={() => { setDeleteError(''); setSelectedDelete(transaction) }}>Delete</button></div></td>
              </tr>)}</tbody>
            </table>
          </div>
          <nav className="d-flex justify-content-between align-items-center" aria-label="Transaction pages">
            <button className="btn btn-outline-secondary" type="button" disabled={page <= 1 || isLoading} onClick={() => setPage((value) => value - 1)}>Previous</button>
            <span aria-live="polite">Page {meta.pagination.page} of {meta.pagination.total_pages}</span>
            <button className="btn btn-outline-secondary" type="button" disabled={page >= meta.pagination.total_pages || isLoading} onClick={() => setPage((value) => value + 1)}>Next</button>
          </nav>
        </>}
      </main>

      {selectedDelete && <div className="modal d-block" role="presentation" style={{ backgroundColor: 'rgba(0, 0, 0, .5)' }}>
        <div className="modal-dialog modal-dialog-centered" role="dialog" aria-modal="true" aria-labelledby="delete-title">
          <div className="modal-content">
            <div className="modal-header"><h2 className="modal-title fs-5" id="delete-title">Delete transaction?</h2><button type="button" className="btn-close" aria-label="Close" disabled={isDeleting} onClick={() => setSelectedDelete(null)} /></div>
            <div className="modal-body"><p>Delete this {selectedDelete.transaction_type} of €{formatAmount(selectedDelete.amount)}? It will be removed from your history and totals.</p>{deleteError && <div className="alert alert-danger" role="alert">{deleteError}</div>}</div>
            <div className="modal-footer"><button className="btn btn-secondary" type="button" disabled={isDeleting} onClick={() => setSelectedDelete(null)}>Cancel</button><button className="btn btn-danger" type="button" disabled={isDeleting} onClick={confirmDelete}>{isDeleting ? 'Deleting...' : 'Delete transaction'}</button></div>
          </div>
        </div>
      </div>}
    </>
  )
}

export default TransactionHistoryPage
