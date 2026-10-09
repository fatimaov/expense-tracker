import React from 'react'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router'
import LoginPage from './LoginPage.jsx'

const mocks = vi.hoisted(() => ({ login: vi.fn() }))
vi.mock('../context/useAuth.js', () => ({ useAuth: () => ({ login: mocks.login }) }))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

function CurrentPath() {
  return <output>{useLocation().pathname}</output>
}

describe('LoginPage', () => {
  it('directs successful login to the manual transaction route', async () => {
    const user = userEvent.setup()
    mocks.login.mockResolvedValue({})
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/transactions/new" element={<CurrentPath />} />
        </Routes>
      </MemoryRouter>,
    )
    await user.type(screen.getByLabelText('Email'), 'person@example.com')
    await user.type(screen.getByLabelText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: 'Login' }))
    expect(await screen.findByText('/transactions/new')).toBeInTheDocument()
  })
})
