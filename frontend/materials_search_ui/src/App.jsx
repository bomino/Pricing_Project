import { Routes, Route, Navigate } from 'react-router-dom'
import { SearchProvider } from './contexts/SearchContext'
import { AuthProvider } from './contexts/AuthContext'
import { FavoritesProvider } from './contexts/FavoritesContext'
import { SearchPage, MaterialDetailPage, AdminPage, FavoritesPage, BOMPage, BOMDetailPage } from './pages'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <FavoritesProvider>
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
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/bom" element={<BOMPage />} />
          <Route path="/bom/:id" element={<BOMDetailPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </FavoritesProvider>
    </AuthProvider>
  )
}

export default App
