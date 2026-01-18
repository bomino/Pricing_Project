import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchCurrentUser = useCallback(async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
      } else {
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        setUser(null)
      }
    } catch (err) {
      console.error('Error fetching user:', err)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchCurrentUser()
  }, [fetchCurrentUser])

  const login = async (email, password) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Login failed')
    }

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    setUser(data.user)

    return data.user
  }

  const register = async (username, email, password, companyName = null, role = 'buyer') => {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username,
        email,
        password,
        company_name: companyName,
        role
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed')
    }

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    setUser(data.user)

    return data.user
  }

  const logout = async () => {
    const token = localStorage.getItem('token')
    if (token) {
      try {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      } catch (err) {
        console.error('Logout error:', err)
      }
    }

    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    setUser(null)
  }

  const refreshToken = async () => {
    const refresh = localStorage.getItem('refreshToken')
    if (!refresh) return false

    try {
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refresh}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('token', data.access_token)
        return true
      }
    } catch (err) {
      console.error('Token refresh error:', err)
    }

    return false
  }

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshToken,
    refetchUser: fetchCurrentUser
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
