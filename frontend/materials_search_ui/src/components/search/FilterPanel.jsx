import { Filter, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { useSearch } from '../../contexts/SearchContext'

export function FilterPanel() {
  const [showFilters, setShowFilters] = useState(false)
  const {
    categories,
    suppliers,
    selectedCategory,
    setSelectedCategory,
    priceRange,
    setPriceRange,
    selectedSupplier,
    setSelectedSupplier,
    availabilityFilter,
    setAvailabilityFilter,
    clearFilters,
    setCurrentPage,
    fetchMaterials,
  } = useSearch()

  const handleSearch = (e) => {
    e.preventDefault()
    setCurrentPage(1)
    fetchMaterials()
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
        >
          <Filter className="h-4 w-4" />
          <span>Filters</span>
          <ChevronDown className={`h-4 w-4 transform transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>

        <div className="flex space-x-2">
          <button
            type="button"
            onClick={clearFilters}
            className="px-4 py-2 text-gray-600 hover:text-gray-900"
          >
            Clear All
          </button>
          <button
            type="button"
            onClick={handleSearch}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Search
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Price Range</label>
            <div className="flex space-x-2">
              <input
                type="number"
                placeholder="Min"
                value={priceRange.min}
                onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="number"
                placeholder="Max"
                value={priceRange.max}
                onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Supplier</label>
            <select
              value={selectedSupplier}
              onChange={(e) => setSelectedSupplier(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Suppliers</option>
              {suppliers.map(supplier => (
                <option key={supplier} value={supplier}>{supplier}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Availability</label>
            <select
              value={availabilityFilter}
              onChange={(e) => setAvailabilityFilter(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All</option>
              <option value="In Stock">In Stock</option>
              <option value="Limited Stock">Limited Stock</option>
              <option value="Out of Stock">Out of Stock</option>
            </select>
          </div>
        </div>
      )}
    </div>
  )
}
