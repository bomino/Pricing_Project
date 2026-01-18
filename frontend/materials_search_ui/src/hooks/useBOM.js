import { useState, useCallback } from 'react'
import { useAuth } from '@/contexts/AuthContext'

export function useBOM() {
  const { token, isAuthenticated } = useAuth()
  const [boms, setBoms] = useState([])
  const [currentBom, setCurrentBom] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const getHeaders = useCallback(() => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }), [token])

  const fetchBoms = useCallback(async (status = null) => {
    if (!isAuthenticated) return

    setLoading(true)
    setError(null)

    try {
      const url = status ? `/api/v1/boms?status=${status}` : '/api/v1/boms'
      const response = await fetch(url, { headers: getHeaders() })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setBoms(data.boms || [])
      return data.boms
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated, getHeaders])

  const fetchBom = useCallback(async (bomId) => {
    if (!isAuthenticated) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/v1/boms/${bomId}`, { headers: getHeaders() })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setCurrentBom(data)
      return data
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated, getHeaders])

  const createBom = useCallback(async ({ name, description = '', project_id = null }) => {
    if (!isAuthenticated) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/boms', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ name, description, project_id })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const newBom = await response.json()
      setBoms(prev => [...prev, newBom])
      return newBom
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated, getHeaders])

  const updateBom = useCallback(async (bomId, updates) => {
    if (!isAuthenticated) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/v1/boms/${bomId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(updates)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const updatedBom = await response.json()
      setBoms(prev => prev.map(b => b.id === bomId ? updatedBom : b))
      if (currentBom?.id === bomId) {
        setCurrentBom(updatedBom)
      }
      return updatedBom
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated, getHeaders, currentBom])

  const deleteBom = useCallback(async (bomId) => {
    if (!isAuthenticated) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/v1/boms/${bomId}`, {
        method: 'DELETE',
        headers: getHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      setBoms(prev => prev.filter(b => b.id !== bomId))
      if (currentBom?.id === bomId) {
        setCurrentBom(null)
      }
      return true
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated, getHeaders, currentBom])

  const addItem = useCallback(async (bomId, { material_id, quantity, notes = '' }) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/boms/${bomId}/items`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ material_id, quantity, notes })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const newItem = await response.json()

      if (currentBom?.id === bomId) {
        setCurrentBom(prev => ({
          ...prev,
          items: [...(prev.items || []), newItem]
        }))
      }

      return newItem
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders, currentBom])

  const updateItem = useCallback(async (bomId, itemId, updates) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/boms/${bomId}/items/${itemId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(updates)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const updatedItem = await response.json()

      if (currentBom?.id === bomId) {
        setCurrentBom(prev => ({
          ...prev,
          items: prev.items.map(item => item.id === itemId ? updatedItem : item)
        }))
      }

      return updatedItem
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders, currentBom])

  const removeItem = useCallback(async (bomId, itemId) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/boms/${bomId}/items/${itemId}`, {
        method: 'DELETE',
        headers: getHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (currentBom?.id === bomId) {
        setCurrentBom(prev => ({
          ...prev,
          items: prev.items.filter(item => item.id !== itemId)
        }))
      }

      return true
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders, currentBom])

  const getSummary = useCallback(async (bomId) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/boms/${bomId}/summary`, {
        headers: getHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders])

  const exportBom = useCallback(async (bomId, format = 'csv') => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/boms/${bomId}/export?format=${format}`, {
        headers: getHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const contentDisposition = response.headers.get('Content-Disposition')
      const filenameMatch = contentDisposition?.match(/filename="(.+)"/)
      const filename = filenameMatch ? filenameMatch[1] : `bom-${bomId}.${format}`

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      return true
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders])

  const duplicateBom = useCallback(async (bomId, newName = null) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/boms/${bomId}/duplicate`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ new_name: newName })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const newBom = await response.json()
      setBoms(prev => [...prev, newBom])
      return newBom
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders])

  const refreshPrices = useCallback(async (bomId) => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`/api/v1/boms/${bomId}/refresh-prices`, {
        method: 'POST',
        headers: getHeaders()
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      await fetchBom(bomId)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [isAuthenticated, getHeaders, fetchBom])

  return {
    boms,
    currentBom,
    loading,
    error,
    fetchBoms,
    fetchBom,
    createBom,
    updateBom,
    deleteBom,
    addItem,
    updateItem,
    removeItem,
    getSummary,
    exportBom,
    duplicateBom,
    refreshPrices,
    setCurrentBom
  }
}
