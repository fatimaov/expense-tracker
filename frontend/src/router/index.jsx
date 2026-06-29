import { createBrowserRouter } from 'react-router'
import AddExpensePage from '../pages/AddExpensePage.jsx'
import EditExpensePage from '../pages/EditExpensePage.jsx'
import ExpensesPage from '../pages/ExpensesPage.jsx'
import LoginPage from '../pages/LoginPage.jsx'
import RegisterPage from '../pages/RegisterPage.jsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/expenses',
    element: <ExpensesPage />,
  },
  {
    path: '/expenses/new',
    element: <AddExpensePage />,
  },
  {
    path: '/expenses/:id/edit',
    element: <EditExpensePage />,
  },
])

export default router
