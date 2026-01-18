import { useState, useCallback } from 'react'
import { useFavoritesContext } from '@/contexts/FavoritesContext'

export function useFavorites() {
  const context = useFavoritesContext()
  const [isLoading, setIsLoading] = useState(false)

  const toggleFavorite = useCallback(async (materialId) => {
    setIsLoading(true)
    try {
      await context.toggleFavorite(materialId)
    } finally {
      setIsLoading(false)
    }
  }, [context])

  return {
    favorites: context.favorites,
    isFavorite: context.isFavorite,
    toggleFavorite,
    isLoading,
    favoritesCount: context.favoritesCount,
    fetchFavorites: context.fetchFavorites
  }
}
