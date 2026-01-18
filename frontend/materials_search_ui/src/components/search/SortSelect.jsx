import { ArrowUpDown } from 'lucide-react'
import { useSearch } from '../../contexts/SearchContext'

export function SortSelect() {
  const { sortBy, setSortBy, sortOrder, toggleSortOrder, SORT_OPTIONS } = useSearch()

  return (
    <div className="flex items-center space-x-2">
      <label className="text-sm text-gray-600">Sort by:</label>
      <select
        value={sortBy}
        onChange={(e) => setSortBy(e.target.value)}
        className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 text-sm"
      >
        {SORT_OPTIONS.map(option => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
      <button
        onClick={toggleSortOrder}
        className="p-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-blue-500"
        title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
      >
        <ArrowUpDown className={`h-4 w-4 ${sortOrder === 'desc' ? 'transform rotate-180' : ''}`} />
      </button>
    </div>
  )
}
