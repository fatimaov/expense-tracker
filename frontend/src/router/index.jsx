import { createBrowserRouter } from 'react-router'
import ProtectedRoute from '../components/ProtectedRoute.jsx'
import PublicRoute from '../components/PublicRoute.jsx'
import AddExpensePage from '../pages/AddExpensePage.jsx'
import EditExpensePage from '../pages/EditExpensePage.jsx'
import ExpensesPage from '../pages/ExpensesPage.jsx'
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
