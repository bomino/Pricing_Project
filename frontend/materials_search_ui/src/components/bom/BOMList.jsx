import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Folder, MoreVertical, Trash2, Copy, Download, Edit2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

export function BOMList({ boms, onCreateNew, onDelete, onDuplicate, onExport, loading }) {
  const navigate = useNavigate()
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [bomToDelete, setBomToDelete] = useState(null)

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatCurrency = (amount) => {
    if (amount == null) return '$0.00'
    return `$${Number(amount).toFixed(2)}`
  }

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800',
      active: 'bg-green-100 text-green-800',
      archived: 'bg-yellow-100 text-yellow-800',
    }
    return styles[status] || 'bg-gray-100 text-gray-800'
  }

  const handleDeleteClick = (bom) => {
    setBomToDelete(bom)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (bomToDelete) {
      try {
        await onDelete(bomToDelete.id)
        toast.success('BOM deleted successfully')
      } catch {
        toast.error('Failed to delete BOM')
      }
    }
    setDeleteDialogOpen(false)
    setBomToDelete(null)
  }

  const handleDuplicate = async (bom) => {
    try {
      const newBom = await onDuplicate(bom.id, `${bom.name} (Copy)`)
      toast.success('BOM duplicated successfully')
      navigate(`/bom/${newBom.id}`)
    } catch {
      toast.error('Failed to duplicate BOM')
    }
  }

  const handleExport = async (bom) => {
    try {
      await onExport(bom.id, 'csv')
      toast.success('BOM exported successfully')
    } catch {
      toast.error('Failed to export BOM')
    }
  }

  if (loading && boms.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (boms.length === 0) {
    return (
      <div className="text-center py-12">
        <Folder className="h-16 w-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No BOMs yet</h3>
        <p className="text-gray-500 mb-6">Create your first Bill of Materials to get started</p>
        <button
          onClick={onCreateNew}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Create BOM
        </button>
      </div>
    )
  }

  return (
    <>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {boms.map((bom) => (
          <div
            key={bom.id}
            className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow cursor-pointer group"
            onClick={() => navigate(`/bom/${bom.id}`)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">{bom.name}</h3>
                {bom.description && (
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">{bom.description}</p>
                )}
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger
                  onClick={(e) => e.stopPropagation()}
                  className="p-1 rounded hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <MoreVertical className="h-4 w-4 text-gray-500" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={(e) => { e.stopPropagation(); navigate(`/bom/${bom.id}`); }}>
                    <Edit2 className="h-4 w-4 mr-2" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleDuplicate(bom); }}>
                    <Copy className="h-4 w-4 mr-2" />
                    Duplicate
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleExport(bom); }}>
                    <Download className="h-4 w-4 mr-2" />
                    Export CSV
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={(e) => { e.stopPropagation(); handleDeleteClick(bom); }}
                    className="text-red-600 focus:text-red-600"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusBadge(bom.status)}`}>
                {bom.status || 'draft'}
              </span>
              <span className="text-gray-500">
                {bom.item_count || 0} item{(bom.item_count || 0) !== 1 ? 's' : ''}
              </span>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
              <span className="text-lg font-semibold text-green-600">
                {formatCurrency(bom.total_cost)}
              </span>
              <span className="text-xs text-gray-400">
                Updated {formatDate(bom.updated_at)}
              </span>
            </div>
          </div>
        ))}
      </div>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete BOM?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{bomToDelete?.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
