import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useAuth } from './AuthContext'

const FavoritesContext = createContext(null)

export function FavoritesProvider({ children }) {
  const { user, isAuthenticated } = useAuth()
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchFavorites = useCallback(async () => {
    if (!isAuthenticated) {
      setFavorites([])
      return
    }

    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/favorites', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch favorites')
      }

      const data = await response.json()
      setFavorites(data.favorites || [])
    } catch (err) {
      console.error('Error fetching favorites:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated])

  useEffect(() => {
    fetchFavorites()
  }, [fetchFavorites, user])

  const addFavorite = useCallback(async (materialId, notes = '') => {
    if (!isAuthenticated) {
      throw new Error('Must be logged in to add favorites')
    }

    const token = localStorage.getItem('token')
    const response = await fetch('/api/v1/favorites', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ material_id: materialId, notes })
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.error || 'Failed to add favorite')
    }

    const data = await response.json()
    setFavorites(prev => [...prev, data.favorite])
    return data.favorite
  }, [isAuthenticated])

  const removeFavorite = useCallback(async (materialId) => {
    if (!isAuthenticated) {
      throw new Error('Must be logged in to remove favorites')
    }

    const favorite = favorites.find(f => f.material_id === materialId)
    if (!favorite) return

    const token = localStorage.getItem('token')
    const response = await fetch(`/api/v1/favorites/${favorite.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.error || 'Failed to remove favorite')
    }

    setFavorites(prev => prev.filter(f => f.id !== favorite.id))
  }, [isAuthenticated, favorites])

  const isFavorite = useCallback((materialId) => {
    return favorites.some(f => f.material_id === materialId)
  }, [favorites])

  const toggleFavorite = useCallback(async (materialId) => {
    if (isFavorite(materialId)) {
      await removeFavorite(materialId)
    } else {
      await addFavorite(materialId)
    }
  }, [isFavorite, removeFavorite, addFavorite])

  const value = {
    favorites,
    loading,
    error,
    fetchFavorites,
    addFavorite,
    removeFavorite,
    isFavorite,
    toggleFavorite,
    favoritesCount: favorites.length
  }

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  )
}

export function useFavoritesContext() {
  const context = useContext(FavoritesContext)
  if (!context) {
    throw new Error('useFavoritesContext must be used within a FavoritesProvider')
  }
  return context
}
