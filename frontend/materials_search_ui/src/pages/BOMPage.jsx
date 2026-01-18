import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Plus, ClipboardList } from 'lucide-react'
import { AuthHeader } from '@/components/auth'
import { BOMList, CreateBOMDialog } from '@/components/bom'
import { useBOM } from '@/hooks/useBOM'
import { useAuth } from '@/contexts/AuthContext'

export function BOMPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const {
    boms,
    loading,
    fetchBoms,
    createBom,
    deleteBom,
    duplicateBom,
    exportBom
  } = useBOM()

  const [createDialogOpen, setCreateDialogOpen] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      fetchBoms()
    }
  }, [isAuthenticated, fetchBoms])

  const handleCreateBom = async (data) => {
    const newBom = await createBom(data)
    navigate(`/bom/${newBom.id}`)
    return newBom
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-4">
                <img src="/logo.png" alt="Versatex" className="h-10 w-auto" />
                <Link
                  to="/search"
                  className="flex items-center text-gray-600 hover:text-gray-900"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Search
                </Link>
              </div>
              <AuthHeader />
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-16">
          <div className="text-center">
            <ClipboardList className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Bill of Materials</h2>
            <p className="text-gray-500 mb-6">Please log in to manage your Bills of Materials.</p>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-4">
              <img src="/logo.png" alt="Versatex" className="h-10 w-auto" />
              <Link
                to="/search"
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Search
              </Link>
            </div>
            <AuthHeader />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Bill of Materials</h1>
              <p className="text-gray-500 mt-1">Manage your project material lists</p>
            </div>
            <button
              onClick={() => setCreateDialogOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Create BOM
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <BOMList
          boms={boms}
          loading={loading}
          onCreateNew={() => setCreateDialogOpen(true)}
          onDelete={deleteBom}
          onDuplicate={duplicateBom}
          onExport={exportBom}
        />
      </main>

      <CreateBOMDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onCreate={handleCreateBom}
      />
    </div>
  )
}
