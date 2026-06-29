import { Navigate } from 'react-router'
import { useAuth } from '../context/useAuth.js'

function PublicRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return null

  return isAuthenticated ? <Navigate to="/expenses" replace /> : children
}

export default PublicRoute
