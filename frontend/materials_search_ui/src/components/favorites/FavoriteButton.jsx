import { memo, useCallback } from 'react'
import { Heart } from 'lucide-react'
import { useFavorites } from '@/hooks/useFavorites'
import { useAuth } from '@/contexts/AuthContext'
import { toast } from 'sonner'

export const FavoriteButton = memo(function FavoriteButton({
  materialId,
  size = 'default',
  className = ''
}) {
  const { user, isAuthenticated } = useAuth()
  const { isFavorite, toggleFavorite, isLoading } = useFavorites()

  const isFav = isFavorite(materialId)

  const handleClick = useCallback(async (e) => {
    e.stopPropagation()
    e.preventDefault()

    if (!isAuthenticated) {
      toast.error('Please log in to save favorites')
      return
    }

    try {
      await toggleFavorite(materialId)
      toast.success(isFav ? 'Removed from favorites' : 'Added to favorites')
    } catch (err) {
      toast.error('Failed to update favorites')
    }
  }, [isAuthenticated, toggleFavorite, materialId, isFav])

  const sizeClasses = {
    small: 'h-4 w-4',
    default: 'h-5 w-5',
    large: 'h-6 w-6'
  }

  const iconSize = sizeClasses[size] || sizeClasses.default

  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      className={`p-2 rounded-full transition-colors hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 ${className}`}
      aria-label={isFav ? 'Remove from favorites' : 'Add to favorites'}
    >
      <Heart
        className={`${iconSize} transition-colors ${
          isFav
            ? 'fill-red-500 text-red-500'
            : 'text-gray-400 hover:text-red-400'
        }`}
      />
    </button>
  )
})
