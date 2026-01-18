import { SearchBar, FilterPanel, SortSelect, SaveSearchButton, SavedSearchList } from '../components/search'
import { MaterialGrid } from '../components/materials'
import { AuthHeader } from '../components/auth'
import { useSearch } from '../contexts/SearchContext'

export function SearchPage() {
  const { totalMaterials, loading, debouncedSearchQuery, getCurrentQueryParams, applySearchParams } = useSearch()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <img src="/logo.png" alt="Versatex" className="h-12 w-auto" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Construction Materials Search</h1>
                <p className="text-gray-500 text-sm">Find the best construction materials for your project</p>
              </div>
            </div>
            <AuthHeader />
          </div>
        </div>
      </header>

      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 space-y-4">
          <SearchBar />
          <FilterPanel />
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {loading ? 'Loading...' : `${totalMaterials} materials found`}
            </h2>
            {debouncedSearchQuery && (
              <p className="text-gray-600">Results for "{debouncedSearchQuery}"</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <SaveSearchButton queryParams={getCurrentQueryParams()} />
            <SavedSearchList onApplySearch={applySearchParams} />
            <SortSelect />
          </div>
        </div>

        <MaterialGrid />
      </main>
    </div>
  )
}
