import { Link, useLocation } from 'react-router'

function TransactionNavigation() {
  const { pathname } = useLocation()
  return (
    <nav className="navbar navbar-expand bg-light border-bottom" aria-label="Transaction navigation">
      <div className="container">
        <Link className="navbar-brand" to="/transactions">Expense Tracker</Link>
        <div className="navbar-nav flex-row gap-3">
          <Link className={`nav-link${pathname.startsWith('/transactions/new') ? ' active' : ''}`} to="/transactions/new">Add transaction</Link>
          <Link className={`nav-link${pathname === '/transactions' || pathname.includes('/edit') ? ' active' : ''}`} to="/transactions">Transaction history</Link>
        </div>
      </div>
    </nav>
  )
}

export default TransactionNavigation
