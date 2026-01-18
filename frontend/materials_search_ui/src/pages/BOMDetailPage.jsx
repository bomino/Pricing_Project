import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Edit2, Check, X } from 'lucide-react'
import { toast } from 'sonner'
import { AuthHeader } from '@/components/auth'
import { BOMDetail } from '@/components/bom'
import { useBOM } from '@/hooks/useBOM'
import { useAuth } from '@/contexts/AuthContext'

export function BOMDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const {
    currentBom,
    loading,
    fetchBom,
    updateBom,
    updateItem,
    removeItem,
    refreshPrices,
    exportBom
  } = useBOM()

  const [isEditing, setIsEditing] = useState(false)
  const [editName, setEditName] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    if (isAuthenticated && id) {
      fetchBom(parseInt(id))
    }
  }, [isAuthenticated, id, fetchBom])

  useEffect(() => {
    if (currentBom) {
      setEditName(currentBom.name || '')
      setEditDescription(currentBom.description || '')
    }
  }, [currentBom])

  const handleSaveEdit = async () => {
    try {
      await updateBom(currentBom.id, {
        name: editName.trim(),
        description: editDescription.trim()
      })
      setIsEditing(false)
      toast.success('BOM updated')
    } catch {
      toast.error('Failed to update BOM')
    }
  }

  const handleCancelEdit = () => {
    setEditName(currentBom?.name || '')
    setEditDescription(currentBom?.description || '')
    setIsEditing(false)
  }

  const handleRefreshPrices = async (bomId) => {
    setRefreshing(true)
    try {
      await refreshPrices(bomId)
    } finally {
      setRefreshing(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Please log in to view this BOM.</p>
          <Link to="/search" className="text-blue-600 hover:text-blue-800 mt-2 inline-block">
            Go to Search
          </Link>
        </div>
      </div>
    )
  }

  if (loading && !currentBom) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!currentBom) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">BOM not found</p>
          <button
            onClick={() => navigate('/bom')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to BOM List
          </button>
        </div>
      </div>
    )
  }

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800',
      active: 'bg-green-100 text-green-800',
      archived: 'bg-yellow-100 text-yellow-800',
    }
    return styles[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-4">
              <img src="/logo.png" alt="Versatex" className="h-10 w-auto" />
              <button
                onClick={() => navigate('/bom')}
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to BOM List
              </button>
            </div>
            <AuthHeader />
          </div>

          {isEditing ? (
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="text-2xl font-bold text-gray-900 border-b-2 border-blue-500 focus:outline-none bg-transparent"
                  autoFocus
                />
                <button
                  onClick={handleSaveEdit}
                  className="p-1.5 rounded-full bg-green-100 text-green-600 hover:bg-green-200"
                >
                  <Check className="h-4 w-4" />
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="p-1.5 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <input
                type="text"
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                placeholder="Add description..."
                className="text-gray-500 border-b border-gray-300 focus:outline-none focus:border-blue-500 bg-transparent w-full max-w-lg"
              />
            </div>
          ) : (
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-3xl font-bold text-gray-900">{currentBom.name}</h1>
                  <span className={`px-2 py-0.5 text-xs rounded-full ${getStatusBadge(currentBom.status)}`}>
                    {currentBom.status || 'draft'}
                  </span>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="p-1.5 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                  >
                    <Edit2 className="h-4 w-4" />
                  </button>
                </div>
                {currentBom.description && (
                  <p className="text-gray-500 mt-1">{currentBom.description}</p>
                )}
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Total Cost</p>
                <p className="text-2xl font-bold text-green-600">
                  ${(currentBom.total_cost || 0).toFixed(2)}
                </p>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <BOMDetail
          bom={currentBom}
          onUpdateItem={updateItem}
          onRemoveItem={removeItem}
          onRefreshPrices={handleRefreshPrices}
          onExport={exportBom}
          refreshing={refreshing}
        />

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Add materials to this BOM</h4>
          <p className="text-sm text-blue-700">
            Search for materials and click "Add to BOM" to add them to this Bill of Materials.
          </p>
          <Link
            to="/search"
            className="inline-block mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Go to Search →
          </Link>
        </div>
      </main>
    </div>
  )
}
