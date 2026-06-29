import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router/dom'
import 'bootstrap/dist/css/bootstrap.min.css'
import './styles/global.css'
import { AuthProvider } from './context/AuthContext.jsx'
import router from './router/index.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
