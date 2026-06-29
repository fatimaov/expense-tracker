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
  let response

  try {
    response = await fetch(url, {
      method,
      headers: {
        ...(hasBody && { 'Content-Type': 'application/json' }),
        ...headers,
      },
      ...(hasBody && { body: JSON.stringify(body) }),
    })
  } catch {
    throw new ApiError(
      'Unable to connect to the server. Check your connection and try again.',
      0,
      null,
    )
  }

  let data = null

  if (response.status !== 204) {
    const responseText = await response.text()

    if (responseText) {
      try {
        data = JSON.parse(responseText)
      } catch {
        throw new ApiError(
          'The server returned an invalid response. Please try again.',
          response.status,
          null,
        )
      }
    }
  }

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
