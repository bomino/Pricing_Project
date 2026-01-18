import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

export function PriceHistoryChart({ materialId }) {
  const [priceData, setPriceData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [period, setPeriod] = useState('30d')

  useEffect(() => {
    const fetchPriceHistory = async () => {
      if (!materialId) return

      setLoading(true)
      try {
        const response = await fetch(`/api/v1/materials/${materialId}/price-history?period=${period}`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        setPriceData(data)
        setError(null)
      } catch (err) {
        console.error('Error fetching price history:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchPriceHistory()
  }, [materialId, period])

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const formatPrice = (price) => {
    return `$${price.toFixed(2)}`
  }

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="h-5 w-5 text-red-500" />
      case 'decreasing':
        return <TrendingDown className="h-5 w-5 text-green-500" />
      default:
        return <Minus className="h-5 w-5 text-gray-500" />
    }
  }

  const getTrendLabel = (trend) => {
    switch (trend) {
      case 'increasing':
        return 'Trending Up'
      case 'decreasing':
        return 'Trending Down'
      case 'stable':
        return 'Stable'
      default:
        return 'Insufficient Data'
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Price History</h3>
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Price History</h3>
        <div className="h-64 flex items-center justify-center text-gray-500">
          Unable to load price history
        </div>
      </div>
    )
  }

  const chartData = priceData?.history?.map(item => ({
    date: formatDate(item.recorded_at),
    price: item.price,
    fullDate: item.recorded_at
  })) || []

  const stats = priceData?.statistics || {}
  const trend = priceData?.trend || 'insufficient_data'

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Price History</h3>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="1y">Last year</option>
        </select>
      </div>

      {chartData.length > 0 ? (
        <>
          <div className="h-64 mb-6">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  tickLine={{ stroke: '#d1d5db' }}
                />
                <YAxis
                  tickFormatter={(value) => `$${value}`}
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  tickLine={{ stroke: '#d1d5db' }}
                  domain={['dataMin - 10', 'dataMax + 10']}
                />
                <Tooltip
                  formatter={(value) => [formatPrice(value), 'Price']}
                  labelFormatter={(label) => `Date: ${label}`}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#2563eb', strokeWidth: 2, fill: '#fff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
            <div className="text-center">
              <p className="text-sm text-gray-500">Current</p>
              <p className="text-lg font-semibold text-gray-900">
                {stats.current_price ? formatPrice(stats.current_price) : '-'}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Average</p>
              <p className="text-lg font-semibold text-gray-900">
                {stats.avg_price ? formatPrice(stats.avg_price) : '-'}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Range</p>
              <p className="text-lg font-semibold text-gray-900">
                {stats.min_price && stats.max_price
                  ? `${formatPrice(stats.min_price)} - ${formatPrice(stats.max_price)}`
                  : '-'}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Trend</p>
              <div className="flex items-center justify-center gap-1">
                {getTrendIcon(trend)}
                <span className="text-sm font-medium">{getTrendLabel(trend)}</span>
              </div>
              {stats.price_change_percent !== null && stats.price_change_percent !== undefined && (
                <p className={`text-xs ${stats.price_change_percent > 0 ? 'text-red-500' : stats.price_change_percent < 0 ? 'text-green-500' : 'text-gray-500'}`}>
                  {stats.price_change_percent > 0 ? '+' : ''}{stats.price_change_percent}%
                </p>
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="h-64 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2">No price history available</p>
            <p className="text-sm">Price data will appear as prices are recorded</p>
          </div>
        </div>
      )}
    </div>
  )
}
