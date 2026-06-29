import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../context/useAuth.js'

function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await register({ email, password })
      navigate('/expenses', { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Unable to register.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="container py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-sm-8 col-md-6 col-lg-4">
          <h1 className="mb-2">Create Account</h1>
          <p className="text-secondary mb-4">
            Create an account to keep your expenses private.
          </p>

          {error && (
            <div className="alert alert-danger" role="alert" aria-live="polite">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label" htmlFor="email">
                Email
              </label>
              <input
                className="form-control"
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                disabled={isSubmitting}
                autoFocus
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label" htmlFor="register-password">
                Password
              </label>
              <input
                className="form-control"
                id="register-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="new-password"
                aria-describedby="password-help"
                minLength="8"
                disabled={isSubmitting}
                required
              />
              <div className="form-text" id="password-help">
                Use at least 8 characters.
              </div>
            </div>

            <button
              className="btn btn-primary w-100"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Registering...' : 'Register'}
            </button>
          </form>

          <p className="mt-3 mb-0">
            Already have an account? <Link to="/">Login</Link>
          </p>
        </div>
      </div>
    </main>
  )
}

export default RegisterPage
