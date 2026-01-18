import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Heart } from 'lucide-react'
import { MaterialCard } from '@/components/materials'
import { FavoriteButton } from '@/components/favorites'
import { AuthHeader } from '@/components/auth'
import { useAuth } from '@/contexts/AuthContext'
import { useFavoritesContext } from '@/contexts/FavoritesContext'

export function FavoritesPage() {
  const navigate = useNavigate()
  const { isAuthenticated, loading: authLoading } = useAuth()
  const { favorites, loading, error, fetchFavorites } = useFavoritesContext()

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/search')
    }
  }, [isAuthenticated, authLoading, navigate])

  const handleBack = () => {
    navigate(-1)
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading favorites...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <p className="text-lg">Error: {error}</p>
          </div>
          <button
            onClick={fetchFavorites}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-4">
              <img src="/logo.png" alt="Versatex" className="h-10 w-auto" />
              <button
                onClick={handleBack}
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </button>
            </div>
            <AuthHeader />
          </div>
          <div className="flex items-center gap-3">
            <Heart className="h-6 w-6 text-red-500 fill-red-500" />
            <h1 className="text-3xl font-bold text-gray-900">My Favorites</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {favorites.length === 0 ? (
          <div className="text-center py-12">
            <Heart className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 text-lg mb-4">You haven't saved any favorites yet</p>
            <p className="text-gray-500 mb-6">
              Click the heart icon on any material to save it here
            </p>
            <button
              onClick={() => navigate('/search')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Browse Materials
            </button>
          </div>
        ) : (
          <>
            <p className="text-gray-600 mb-6">{favorites.length} saved materials</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {favorites.map((favorite) => (
                <div key={favorite.id} className="relative">
                  <div className="absolute top-4 right-4 z-10">
                    <FavoriteButton materialId={favorite.material_id} />
                  </div>
                  <MaterialCard material={favorite.material} />
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
