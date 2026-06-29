function EmptyState({ onAddExpense }) {
  return (
    <section className="text-center border rounded p-4 p-sm-5">
      <h2 className="h4">No expenses yet</h2>
      <p className="text-secondary mb-4">
        Add your first expense to start tracking your spending.
      </p>
      <button className="btn btn-primary" type="button" onClick={onAddExpense}>
        Add Expense
      </button>
    </section>
  )
}

export default EmptyState
