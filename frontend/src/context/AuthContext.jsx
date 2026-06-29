import { useCallback, useEffect, useMemo, useState } from 'react'
import { AuthContext } from './authContext.js'
import { authService } from '../services/authService.js'
import {
  getToken,
  removeToken,
  saveToken,
} from '../services/tokenStorage.js'

function getResponseToken(response) {
  return (
    response?.token ??
    response?.access_token ??
    response?.data?.token ??
    response?.data?.access_token ??
    null
  )
}

function getResponseUser(response) {
  if (response?.user) return response.user
  if (response?.data?.user) return response.data.user
  if (response?.id && response?.email) return response
  return null
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => getToken())
  const [isLoading, setIsLoading] = useState(true)

  const clearAuth = useCallback(() => {
    removeToken()
    setToken(null)
    setUser(null)
  }, [])

  const applyAuthResponse = useCallback((response) => {
    const responseToken = getResponseToken(response)
    const responseUser = getResponseUser(response)

    if (responseToken) {
      saveToken(responseToken)
      setToken(responseToken)
    }

    if (responseUser) {
      setUser(responseUser)
    }

    return response
  }, [])

  const register = useCallback(
    async (credentials) => {
      const response = await authService.register(credentials)
      return applyAuthResponse(response)
    },
    [applyAuthResponse],
  )

  const login = useCallback(
    async (credentials) => {
      const response = await authService.login(credentials)
      return applyAuthResponse(response)
    },
    [applyAuthResponse],
  )

  const logout = useCallback(() => {
    clearAuth()
  }, [clearAuth])

  const checkCurrentUser = useCallback(async () => {
    const storedToken = getToken()

    if (!storedToken) {
      clearAuth()
      setIsLoading(false)
      return null
    }

    setIsLoading(true)
    try {
      const response = await authService.getCurrentUser(storedToken)
      setToken(storedToken)
      setUser(getResponseUser(response))
      return response
    } catch {
      clearAuth()
      return null
    } finally {
      setIsLoading(false)
    }
  }, [clearAuth])

  useEffect(() => {
    checkCurrentUser()
  }, [checkCurrentUser])

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      isLoading,
      register,
      login,
      logout,
      checkCurrentUser,
    }),
    [
      user,
      token,
      isLoading,
      register,
      login,
      logout,
      checkCurrentUser,
    ],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
