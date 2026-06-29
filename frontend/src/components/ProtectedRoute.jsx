import { Navigate } from 'react-router'
import { useAuth } from '../context/useAuth.js'
import LoadingState from './LoadingState.jsx'

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <LoadingState message="Checking your session..." />

  return isAuthenticated ? children : <Navigate to="/" replace />
}

export default ProtectedRoute
