import { useNavigate } from 'react-router'
import { useAuth } from '../context/useAuth.js'

function ExpensesPage() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  return (
    <main className="container">
      <div className="d-flex align-items-center justify-content-between gap-3">
        <h1 className="mb-0">Expenses List</h1>
        <button
          className="btn btn-outline-secondary"
          type="button"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </main>
  )
}

export default ExpensesPage
