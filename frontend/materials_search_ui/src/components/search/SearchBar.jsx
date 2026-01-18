import { Search } from 'lucide-react'
import { useSearch } from '../../contexts/SearchContext'

export function SearchBar() {
  const { searchQuery, setSearchQuery, setCurrentPage, fetchMaterials } = useSearch()

  const handleSubmit = (e) => {
    e.preventDefault()
    setCurrentPage(1)
    fetchMaterials()
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
      <input
        type="text"
        placeholder="Search materials (e.g., concrete, steel, lumber)..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </form>
  )
}
