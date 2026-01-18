import { useState, useCallback } from 'react'
import { useAuth } from '@/contexts/AuthContext'

export function useSavedSearches() {
  const { token, isAuthenticated } = useAuth()
  const [savedSearches, setSavedSearches] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const getHeaders = useCallback(() => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }), [token])

  const fetchSavedSearches = useCallback(async () => {
    if (!isAuthenticated) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/saved-searches', {
        headers: getHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setSavedSearches(data.saved_searches || [])
      return data.saved_searches
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated, getHeaders])

  const createSavedSearch = useCallback(async ({ name, query_params, alert_enabled = false }) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch('/api/v1/saved-searches', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ name, query_params, alert_enabled })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const newSearch = await response.json()
      setSavedSearches(prev => [newSearch, ...prev])
      return newSearch
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders])

  const updateSavedSearch = useCallback(async (searchId, updates) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/saved-searches/${searchId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(updates)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const updatedSearch = await response.json()
      setSavedSearches(prev =>
        prev.map(s => s.id === searchId ? updatedSearch : s)
      )
      return updatedSearch
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders])

  const deleteSavedSearch = useCallback(async (searchId) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/saved-searches/${searchId}`, {
        method: 'DELETE',
        headers: getHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      setSavedSearches(prev => prev.filter(s => s.id !== searchId))
      return true
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders])

  const toggleAlert = useCallback(async (searchId, enabled) => {
    return updateSavedSearch(searchId, { alert_enabled: enabled })
  }, [updateSavedSearch])

  return {
    savedSearches,
    loading,
    error,
    fetchSavedSearches,
    createSavedSearch,
    updateSavedSearch,
    deleteSavedSearch,
    toggleAlert
  }
}
