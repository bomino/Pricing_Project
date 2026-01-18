import { useCallback, useMemo, useRef, useEffect, useState } from 'react'
import { FixedSizeGrid as Grid } from 'react-window'
import { MaterialCard } from './MaterialCard'
import { useSearch } from '../../contexts/SearchContext'

const CARD_HEIGHT = 340
const CARD_MIN_WIDTH = 320
const GAP = 24

function useGridDimensions(containerRef) {
  const [dimensions, setDimensions] = useState({ width: 0, height: 600 })

  useEffect(() => {
    if (!containerRef.current) return

    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: Math.min(window.innerHeight - 300, 800)
        })
      }
    }

    updateDimensions()
    const resizeObserver = new ResizeObserver(updateDimensions)
    resizeObserver.observe(containerRef.current)

    return () => resizeObserver.disconnect()
  }, [containerRef])

  return dimensions
}

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

  const containerRef = useRef(null)
  const { width, height } = useGridDimensions(containerRef)

  const columnCount = useMemo(() => {
    if (width === 0) return 1
    return Math.max(1, Math.floor((width + GAP) / (CARD_MIN_WIDTH + GAP)))
  }, [width])

  const rowCount = useMemo(() => {
    return Math.ceil(materials.length / columnCount)
  }, [materials.length, columnCount])

  const columnWidth = useMemo(() => {
    if (columnCount === 0) return CARD_MIN_WIDTH
    return (width - GAP * (columnCount - 1)) / columnCount
  }, [width, columnCount])

  const Cell = useCallback(({ columnIndex, rowIndex, style }) => {
    const index = rowIndex * columnCount + columnIndex
    if (index >= materials.length) return null

    const material = materials[index]
    return (
      <div style={{
        ...style,
        left: style.left + (columnIndex > 0 ? GAP * columnIndex : 0),
        top: style.top + (rowIndex > 0 ? GAP * rowIndex : 0),
        width: columnWidth,
        height: CARD_HEIGHT - GAP,
        paddingRight: columnIndex < columnCount - 1 ? 0 : 0,
      }}>
        <MaterialCard material={material} />
      </div>
    )
  }, [materials, columnCount, columnWidth])

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

  const useVirtualization = materials.length > 24

  return (
    <>
      <div ref={containerRef} className="w-full">
        {useVirtualization && width > 0 ? (
          <Grid
            columnCount={columnCount}
            columnWidth={columnWidth + GAP}
            height={height}
            rowCount={rowCount}
            rowHeight={CARD_HEIGHT}
            width={width}
            className="scrollbar-thin scrollbar-thumb-gray-300"
          >
            {Cell}
          </Grid>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {materials.map((material) => (
              <MaterialCard key={material.id} material={material} />
            ))}
          </div>
        )}
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
