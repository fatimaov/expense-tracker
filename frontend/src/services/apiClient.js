import { API_BASE_URL } from '../config.js'

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

export async function request(endpoint, { method = 'GET', body, headers = {} } = {}) {
  const url = `${API_BASE_URL.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`
  const hasBody = body !== undefined
  const response = await fetch(url, {
    method,
    headers: {
      ...(hasBody && { 'Content-Type': 'application/json' }),
      ...headers,
    },
    ...(hasBody && { body: JSON.stringify(body) }),
  })

  const data = response.status === 204 ? null : await response.json()

  if (!response.ok) {
    const message = data?.error?.message || data?.message || 'Request failed.'
    throw new ApiError(message, response.status, data)
  }

  return data
}

export const apiClient = {
  get: (endpoint, options) => request(endpoint, { ...options, method: 'GET' }),
  post: (endpoint, body, options) =>
    request(endpoint, { ...options, method: 'POST', body }),
  put: (endpoint, body, options) =>
    request(endpoint, { ...options, method: 'PUT', body }),
  patch: (endpoint, body, options) =>
    request(endpoint, { ...options, method: 'PATCH', body }),
  delete: (endpoint, options) =>
    request(endpoint, { ...options, method: 'DELETE' }),
}
