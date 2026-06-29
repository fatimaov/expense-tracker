import { Navigate } from 'react-router'
import { useAuth } from '../context/useAuth.js'
import LoadingState from './LoadingState.jsx'

function PublicRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <LoadingState message="Checking your session..." />

  return isAuthenticated ? <Navigate to="/expenses" replace /> : children
}

export default PublicRoute
