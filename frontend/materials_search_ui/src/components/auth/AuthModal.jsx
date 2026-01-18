import { useState } from 'react'
import { X } from 'lucide-react'
import { LoginForm } from './LoginForm'
import { RegisterForm } from './RegisterForm'

export function AuthModal({ isOpen, onClose, initialView = 'login' }) {
  const [view, setView] = useState(initialView)

  if (!isOpen) return null

  const handleSuccess = () => {
    onClose()
  }

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={handleBackdropClick}
    >
      <div className="relative bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>

        {view === 'login' ? (
          <LoginForm
            onSuccess={handleSuccess}
            onSwitchToRegister={() => setView('register')}
          />
        ) : (
          <RegisterForm
            onSuccess={handleSuccess}
            onSwitchToLogin={() => setView('login')}
          />
        )}
      </div>
    </div>
  )
}
