import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useDebounce } from '../hooks/useDebounce'

const SearchContext = createContext(null)

const SORT_OPTIONS = [
  { value: 'name', label: 'Name' },
  { value: 'price', label: 'Price' },
  { value: 'lead_time_days', label: 'Lead Time' },
  { value: 'availability', label: 'Availability' },
]

export function SearchProvider({ children }) {
  const [searchParams, setSearchParams] = useSearchParams()

  const [materials, setMaterials] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '')
  const [priceRange, setPriceRange] = useState({
    min: searchParams.get('min_price') || '',
    max: searchParams.get('max_price') || ''
  })
  const [selectedSupplier, setSelectedSupplier] = useState(searchParams.get('supplier_id') || '')
  const [availabilityFilter, setAvailabilityFilter] = useState(searchParams.get('availability') || '')
  const [sortBy, setSortBy] = useState(searchParams.get('sort_by') || 'name')
  const [sortOrder, setSortOrder] = useState(searchParams.get('sort_order') || 'asc')

  const [currentPage, setCurrentPage] = useState(parseInt(searchParams.get('page')) || 1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalMaterials, setTotalMaterials] = useState(0)

  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  const syncUrlParams = useCallback(() => {
    const params = new URLSearchParams()
    if (debouncedSearchQuery) params.set('q', debouncedSearchQuery)
    if (selectedCategory) params.set('category', selectedCategory)
    if (priceRange.min) params.set('min_price', priceRange.min)
    if (priceRange.max) params.set('max_price', priceRange.max)
    if (selectedSupplier) params.set('supplier_id', selectedSupplier)
    if (availabilityFilter) params.set('availability', availabilityFilter)
    if (sortBy !== 'name') params.set('sort_by', sortBy)
    if (sortOrder !== 'asc') params.set('sort_order', sortOrder)
    if (currentPage > 1) params.set('page', currentPage.toString())
    setSearchParams(params, { replace: true })
  }, [debouncedSearchQuery, selectedCategory, priceRange, selectedSupplier, availabilityFilter, sortBy, sortOrder, currentPage, setSearchParams])

  const fetchCategories = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/categories')
      const data = await response.json()
      setCategories(data.categories || [])
    } catch (err) {
      console.error('Error fetching categories:', err)
    }
  }, [])

  const fetchMaterials = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: '12',
        sort_by: sortBy,
        sort_order: sortOrder
      })

      if (debouncedSearchQuery) params.append('q', debouncedSearchQuery)
      if (selectedCategory) params.append('category', selectedCategory)
      if (priceRange.min) params.append('min_price', priceRange.min)
      if (priceRange.max) params.append('max_price', priceRange.max)
      if (selectedSupplier) params.append('supplier_id', selectedSupplier)
      if (availabilityFilter) params.append('availability', availabilityFilter)

      const response = await fetch(`/api/v1/materials/search?${params}`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      setMaterials(data.materials || [])
      setTotalPages(data.pages || 1)
      setTotalMaterials(data.total || 0)
      setError(null)
    } catch (err) {
      console.error('Error fetching materials:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [currentPage, sortBy, sortOrder, debouncedSearchQuery, selectedCategory, priceRange, selectedSupplier, availabilityFilter])

  useEffect(() => {
    fetchCategories()
  }, [fetchCategories])

  useEffect(() => {
    syncUrlParams()
    fetchMaterials()
  }, [syncUrlParams, fetchMaterials])

  const clearFilters = useCallback(() => {
    setSearchQuery('')
    setSelectedCategory('')
    setPriceRange({ min: '', max: '' })
    setSelectedSupplier('')
    setAvailabilityFilter('')
    setSortBy('name')
    setSortOrder('asc')
    setCurrentPage(1)
  }, [])

  const toggleSortOrder = useCallback(() => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
  }, [])

  const suppliers = [...new Set(materials.map(m => m.supplier_name))].filter(Boolean)

  const value = {
    materials,
    categories,
    suppliers,
    loading,
    error,
    searchQuery,
    setSearchQuery,
    debouncedSearchQuery,
    selectedCategory,
    setSelectedCategory,
    priceRange,
    setPriceRange,
    selectedSupplier,
    setSelectedSupplier,
    availabilityFilter,
    setAvailabilityFilter,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    currentPage,
    setCurrentPage,
    totalPages,
    totalMaterials,
    clearFilters,
    toggleSortOrder,
    fetchMaterials,
    SORT_OPTIONS,
  }

  return (
    <SearchContext.Provider value={value}>
      {children}
    </SearchContext.Provider>
  )
}

export function useSearch() {
  const context = useContext(SearchContext)
  if (!context) {
    throw new Error('useSearch must be used within a SearchProvider')
  }
  return context
}
