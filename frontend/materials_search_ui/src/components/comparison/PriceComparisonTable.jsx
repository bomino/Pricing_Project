import { useState, useEffect } from 'react'
import { ArrowUpDown, ExternalLink, Star, Truck, Package } from 'lucide-react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

export function PriceComparisonTable({ materialId }) {
  const [comparisonData, setComparisonData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sortBy, setSortBy] = useState('price')
  const [sortOrder, setSortOrder] = useState('asc')

  useEffect(() => {
    const fetchComparison = async () => {
      if (!materialId) return

      setLoading(true)
      try {
        const response = await fetch(`/api/v1/materials/${materialId}/compare`)
        if (!response.ok) {
          if (response.status === 404) {
            setComparisonData({ comparisons: [] })
            setError(null)
            return
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        setComparisonData(data)
        setError(null)
      } catch (err) {
        console.error('Error fetching comparison:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchComparison()
  }, [materialId])

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('asc')
    }
  }

  const formatPrice = (price) => {
    if (price == null) return '-'
    return `$${Number(price).toFixed(2)}`
  }

  const getAvailabilityBadge = (availability) => {
    const styles = {
      'In Stock': 'bg-green-100 text-green-800',
      'Limited Stock': 'bg-yellow-100 text-yellow-800',
      'Out of Stock': 'bg-red-100 text-red-800',
      'Pre-Order': 'bg-blue-100 text-blue-800',
    }
    return styles[availability] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Comparison</h3>
        <div className="h-48 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Comparison</h3>
        <div className="h-48 flex items-center justify-center text-gray-500">
          Unable to load price comparison
        </div>
      </div>
    )
  }

  const comparisons = comparisonData?.comparisons || []
  const priceRange = comparisonData?.price_range || {}

  if (comparisons.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Comparison</h3>
        <div className="h-48 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <Package className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p className="text-lg mb-2">Single supplier</p>
            <p className="text-sm">No alternative suppliers available for comparison</p>
          </div>
        </div>
      </div>
    )
  }

  const sortedComparisons = [...comparisons].sort((a, b) => {
    let aVal, bVal
    switch (sortBy) {
      case 'price':
        aVal = a.price ?? Infinity
        bVal = b.price ?? Infinity
        break
      case 'lead_time':
        aVal = a.lead_time_days ?? Infinity
        bVal = b.lead_time_days ?? Infinity
        break
      case 'rating':
        aVal = a.supplier?.rating ?? 0
        bVal = b.supplier?.rating ?? 0
        return sortOrder === 'asc' ? bVal - aVal : aVal - bVal
      default:
        aVal = a.supplier?.name || ''
        bVal = b.supplier?.name || ''
        return sortOrder === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal)
    }
    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal
  })

  const minPrice = priceRange.min ?? Math.min(...comparisons.map(c => c.price || Infinity))

  const SortButton = ({ column, children }) => (
    <button
      onClick={() => handleSort(column)}
      className="flex items-center gap-1 hover:text-blue-600 transition-colors"
    >
      {children}
      <ArrowUpDown className={`h-3 w-3 ${sortBy === column ? 'text-blue-600' : 'text-gray-400'}`} />
    </button>
  )

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Price Comparison</h3>
        {priceRange.min != null && priceRange.max != null && (
          <div className="text-sm text-gray-500">
            Range: <span className="font-medium text-green-600">{formatPrice(priceRange.min)}</span>
            {' - '}
            <span className="font-medium">{formatPrice(priceRange.max)}</span>
          </div>
        )}
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>
              <SortButton column="supplier">Supplier</SortButton>
            </TableHead>
            <TableHead>
              <SortButton column="price">Price</SortButton>
            </TableHead>
            <TableHead>
              <SortButton column="lead_time">Lead Time</SortButton>
            </TableHead>
            <TableHead>Availability</TableHead>
            <TableHead>
              <SortButton column="rating">Rating</SortButton>
            </TableHead>
            <TableHead className="text-right">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedComparisons.map((comparison, index) => {
            const isBestPrice = comparison.price === minPrice
            return (
              <TableRow key={index} className={isBestPrice ? 'bg-green-50' : ''}>
                <TableCell>
                  <div className="font-medium">{comparison.supplier?.name || 'Unknown'}</div>
                  {comparison.unit && (
                    <div className="text-xs text-gray-500">per {comparison.unit}</div>
                  )}
                </TableCell>
                <TableCell>
                  <div className={`font-semibold ${isBestPrice ? 'text-green-600' : ''}`}>
                    {formatPrice(comparison.price)}
                    {isBestPrice && (
                      <span className="ml-2 text-xs bg-green-100 text-green-800 px-1.5 py-0.5 rounded">
                        Best
                      </span>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Truck className="h-4 w-4 text-gray-400" />
                    <span>
                      {comparison.lead_time_days != null
                        ? `${comparison.lead_time_days} days`
                        : '-'}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className={`px-2 py-1 text-xs rounded-full ${getAvailabilityBadge(comparison.availability)}`}>
                    {comparison.availability || 'Unknown'}
                  </span>
                </TableCell>
                <TableCell>
                  {comparison.supplier?.rating ? (
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span>{comparison.supplier.rating.toFixed(1)}</span>
                    </div>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  {comparison.supplier?.website ? (
                    <a
                      href={comparison.supplier.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Contact
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : comparison.supplier?.contact_email ? (
                    <a
                      href={`mailto:${comparison.supplier.contact_email}`}
                      className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Contact
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : (
                    <span className="text-gray-400 text-sm">-</span>
                  )}
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>

      {priceRange.avg != null && (
        <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-500 text-center">
          Average price: <span className="font-medium text-gray-900">{formatPrice(priceRange.avg)}</span>
          {' • '}
          {comparisons.length} supplier{comparisons.length !== 1 ? 's' : ''} compared
        </div>
      )}
    </div>
  )
}
