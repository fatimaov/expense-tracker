import { Navigate } from 'react-router'
import { useAuth } from '../context/useAuth.js'

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return null

  return isAuthenticated ? children : <Navigate to="/" replace />
}

export default ProtectedRoute
