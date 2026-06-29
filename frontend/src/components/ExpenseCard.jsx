function formatAmount(amount) {
  return new Intl.NumberFormat('en', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount)
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(`${date}T00:00:00`))
}

function ExpenseCard({ expense, onEdit }) {
  return (
    <article className="card shadow-sm">
      <div className="card-body">
        <div className="d-flex flex-column flex-sm-row justify-content-between align-items-sm-start gap-2 gap-sm-3">
          <div className="flex-grow-1">
            <h2 className="h5 card-title text-break mb-1">
              {expense.title}
            </h2>
            <p className="text-secondary mb-2">
              {formatDate(expense.expense_date)} · {expense.category}
            </p>
          </div>
          <strong className="fs-5 text-nowrap">
            {formatAmount(expense.amount)}
          </strong>
        </div>

        {expense.notes && (
          <p className="card-text text-break mb-0">{expense.notes}</p>
        )}

        {onEdit && (
          <button
            className="btn btn-outline-primary btn-sm mt-3"
            type="button"
            onClick={() => onEdit(expense)}
          >
            Edit
          </button>
        )}
      </div>
    </article>
  )
}

export default ExpenseCard
