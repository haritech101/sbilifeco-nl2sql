import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import "bootstrap/dist/css/bootstrap.min.css"
import App from './App.tsx'
import ApiProvider from './api/ApiProvider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ApiProvider>
      <App />
    </ApiProvider>
  </StrictMode>,
)
