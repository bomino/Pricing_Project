import { Routes, Route, Navigate } from 'react-router-dom'
import { SearchProvider } from './contexts/SearchContext'
import { AuthProvider } from './contexts/AuthContext'
import { SearchPage, MaterialDetailPage, AdminPage } from './pages'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/search" replace />} />
        <Route
          path="/search"
          element={
            <SearchProvider>
              <SearchPage />
            </SearchProvider>
          }
        />
        <Route path="/materials/:id" element={<MaterialDetailPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
