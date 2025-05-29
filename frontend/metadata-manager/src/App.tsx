import { BrowserRouter, Routes, Route } from 'react-router-dom'
import DBListPage from './pages/DBList'
import DBHomePage from './pages/DBHome'
import TableHome from './pages/TableHome'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DBListPage />} />
        <Route path="/dbs/:dbId" element={<DBHomePage />} />
        <Route path="/dbs/:dbId/tables/:tableId" element={<TableHome />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
