import { createBrowserRouter } from 'react-router'
import ProtectedRoute from '../components/ProtectedRoute.jsx'
import PublicRoute from '../components/PublicRoute.jsx'
import AddExpensePage from '../pages/AddExpensePage.jsx'
import AddTransactionPage from '../pages/AddTransactionPage.jsx'
import EditTransactionPage from '../pages/EditTransactionPage.jsx'
import EditExpensePage from '../pages/EditExpensePage.jsx'
import ExpensesPage from '../pages/ExpensesPage.jsx'
import TransactionHistoryPage from '../pages/TransactionHistoryPage.jsx'
import LoginPage from '../pages/LoginPage.jsx'
import RegisterPage from '../pages/RegisterPage.jsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: '/register',
    element: (
      <PublicRoute>
        <RegisterPage />
      </PublicRoute>
    ),
  },
  {
    path: '/expenses',
    element: (
      <ProtectedRoute>
        <ExpensesPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/transactions',
    element: (
      <ProtectedRoute>
        <TransactionHistoryPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/transactions/:id/edit',
    element: (
      <ProtectedRoute>
        <EditTransactionPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/transactions/new',
    element: (
      <ProtectedRoute>
        <AddTransactionPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/expenses/new',
    element: (
      <ProtectedRoute>
        <AddExpensePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/expenses/:id/edit',
    element: (
      <ProtectedRoute>
        <EditExpensePage />
      </ProtectedRoute>
    ),
  },
])

export default router
