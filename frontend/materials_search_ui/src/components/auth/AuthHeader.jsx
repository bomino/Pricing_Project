import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { useFavoritesContext } from '@/contexts/FavoritesContext'
import { AuthModal } from './AuthModal'
import { User, LogOut, ChevronDown, Settings, Heart, ClipboardList } from 'lucide-react'

export function AuthHeader() {
  const { user, isAuthenticated, loading, logout } = useAuth()
  const { favoritesCount } = useFavoritesContext()
  const [showModal, setShowModal] = useState(false)
  const [modalView, setModalView] = useState('login')
  const [showDropdown, setShowDropdown] = useState(false)

  const openLogin = () => {
    setModalView('login')
    setShowModal(true)
  }

  const openRegister = () => {
    setModalView('register')
    setShowModal(true)
  }

  const handleLogout = async () => {
    setShowDropdown(false)
    await logout()
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <div className="h-8 w-20 bg-gray-200 animate-pulse rounded"></div>
      </div>
    )
  }

  if (isAuthenticated && user) {
    return (
      <div className="flex items-center gap-3">
        <Link
          to="/favorites"
          className="relative flex items-center gap-1 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
        >
          <Heart className="h-4 w-4" />
          <span className="hidden sm:inline">Favorites</span>
          {favoritesCount > 0 && (
            <span className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center text-xs bg-red-500 text-white rounded-full">
              {favoritesCount > 99 ? '99+' : favoritesCount}
            </span>
          )}
        </Link>

        <Link
          to="/bom"
          className="flex items-center gap-1 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
        >
          <ClipboardList className="h-4 w-4" />
          <span className="hidden sm:inline">BOMs</span>
        </Link>

        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
          >
            <User className="h-4 w-4" />
            <span>{user.username || user.email}</span>
            <ChevronDown className="h-4 w-4" />
          </button>

          {showDropdown && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowDropdown(false)}
              />
              <div className="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-20">
                <div className="px-4 py-3 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900">{user.username}</p>
                  <p className="text-xs text-gray-500 truncate">{user.email}</p>
                  {user.company_name && (
                    <p className="text-xs text-gray-500">{user.company_name}</p>
                  )}
                </div>
                <Link
                  to="/favorites"
                  onClick={() => setShowDropdown(false)}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Heart className="h-4 w-4" />
                  My Favorites
                </Link>
                <Link
                  to="/bom"
                  onClick={() => setShowDropdown(false)}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <ClipboardList className="h-4 w-4" />
                  My BOMs
                </Link>
                <Link
                  to="/admin"
                  onClick={() => setShowDropdown(false)}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Settings className="h-4 w-4" />
                  Admin Panel
                </Link>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <button
          onClick={openLogin}
          className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
        >
          Sign In
        </button>
        <button
          onClick={openRegister}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Sign Up
        </button>
      </div>

      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        initialView={modalView}
      />
    </>
  )
}
