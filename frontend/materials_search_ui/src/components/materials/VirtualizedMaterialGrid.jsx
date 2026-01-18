import { memo, useCallback, useMemo } from 'react'
import { FixedSizeGrid as Grid } from 'react-window'
import { MaterialCard } from './MaterialCard'
import { useSearch } from '../../contexts/SearchContext'

const CARD_WIDTH = 380
const CARD_HEIGHT = 320
const GAP = 24

const Cell = memo(function Cell({ columnIndex, rowIndex, style, data }) {
  const { materials, columnCount } = data
  const index = rowIndex * columnCount + columnIndex

  if (index >= materials.length) {
    return null
  }

  const material = materials[index]

  return (
    <div
      style={{
        ...style,
        left: style.left + GAP / 2,
        top: style.top + GAP / 2,
        width: style.width - GAP,
        height: style.height - GAP,
      }}
    >
      <MaterialCard material={material} />
    </div>
  )
})

export const VirtualizedMaterialGrid = memo(function VirtualizedMaterialGrid({
  width = 1200,
  height = 600
}) {
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

  const columnCount = useMemo(() => {
    return Math.max(1, Math.floor(width / CARD_WIDTH))
  }, [width])

  const rowCount = useMemo(() => {
    return Math.ceil(materials.length / columnCount)
  }, [materials.length, columnCount])

  const itemData = useMemo(() => ({
    materials,
    columnCount,
  }), [materials, columnCount])

  const handlePrevPage = useCallback(() => {
    setCurrentPage(prev => Math.max(prev - 1, 1))
  }, [setCurrentPage])

  const handleNextPage = useCallback(() => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages))
  }, [setCurrentPage, totalPages])

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
      <Grid
        columnCount={columnCount}
        columnWidth={CARD_WIDTH}
        height={height}
        rowCount={rowCount}
        rowHeight={CARD_HEIGHT}
        width={width}
        itemData={itemData}
        overscanRowCount={2}
      >
        {Cell}
      </Grid>

      {totalPages > 1 && (
        <div className="flex justify-center items-center space-x-2 mt-8">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>

          <span className="px-4 py-2 text-gray-700">
            Page {currentPage} of {totalPages}
          </span>

          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}
    </>
  )
})
