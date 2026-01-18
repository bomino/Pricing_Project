import { MaterialCard } from './MaterialCard'
import { useSearch } from '../../contexts/SearchContext'

export function MaterialGrid() {
  const {
    materials,
    loading,
    error,
    clearFilters,
    fetchMaterials,
    currentPage,
    setCurrentPage,
    totalPages,
  } = useSearch()

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <p className="text-lg">Error: {error}</p>
        </div>
        <button
          onClick={fetchMaterials}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-gray-600 mt-4">Loading materials...</p>
      </div>
    )
  }

  if (materials.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 text-lg">No materials found matching your criteria</p>
        <button
          onClick={clearFilters}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Clear Filters
        </button>
      </div>
    )
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {materials.map((material) => (
          <MaterialCard key={material.id} material={material} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center items-center space-x-2 mt-8">
          <button
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
            className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>

          <span className="px-4 py-2 text-gray-700">
            Page {currentPage} of {totalPages}
          </span>

          <button
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}
    </>
  )
}
