import { useState, useEffect } from 'react'
import { Bookmark, Bell, BellOff, Trash2, Play } from 'lucide-react'
import { toast } from 'sonner'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
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
import { useSavedSearches } from '@/hooks/useSavedSearches'
import { useAuth } from '@/contexts/AuthContext'

export function SavedSearchList({ onApplySearch }) {
  const { isAuthenticated } = useAuth()
  const { savedSearches, loading, fetchSavedSearches, deleteSavedSearch, toggleAlert } = useSavedSearches()
  const [open, setOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [searchToDelete, setSearchToDelete] = useState(null)

  useEffect(() => {
    if (open && isAuthenticated) {
      fetchSavedSearches()
    }
  }, [open, isAuthenticated, fetchSavedSearches])

  const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  }

  const handleApply = (search) => {
    if (onApplySearch && search.query_params) {
      onApplySearch(search.query_params)
      setOpen(false)
      toast.success(`Applied: ${search.name}`)
    }
  }

  const handleToggleAlert = async (e, search) => {
    e.stopPropagation()
    try {
      await toggleAlert(search.id, !search.alert_enabled)
      toast.success(search.alert_enabled ? 'Alerts disabled' : 'Alerts enabled')
    } catch {
      toast.error('Failed to update alerts')
    }
  }

  const handleDeleteClick = (e, search) => {
    e.stopPropagation()
    setSearchToDelete(search)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (searchToDelete) {
      try {
        await deleteSavedSearch(searchToDelete.id)
        toast.success('Search deleted')
      } catch {
        toast.error('Failed to delete search')
      }
    }
    setDeleteDialogOpen(false)
    setSearchToDelete(null)
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <button
            className="relative inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="Saved searches"
          >
            <Bookmark className="h-4 w-4" />
            Saved
            {savedSearches.length > 0 && (
              <span className="absolute -top-1.5 -right-1.5 h-4 w-4 flex items-center justify-center text-[10px] bg-blue-500 text-white rounded-full">
                {savedSearches.length}
              </span>
            )}
          </button>
        </PopoverTrigger>
        <PopoverContent className="w-80 p-0" align="end">
          <div className="px-4 py-3 border-b border-gray-100">
            <h4 className="font-medium text-gray-900">Saved Searches</h4>
          </div>

          {loading ? (
            <div className="py-8 flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            </div>
          ) : savedSearches.length === 0 ? (
            <div className="py-8 text-center">
              <Bookmark className="h-8 w-8 mx-auto text-gray-300 mb-2" />
              <p className="text-sm text-gray-500">No saved searches yet</p>
              <p className="text-xs text-gray-400 mt-1">
                Apply filters and click "Save Search"
              </p>
            </div>
          ) : (
            <div className="max-h-80 overflow-y-auto">
              {savedSearches.map((search) => (
                <div
                  key={search.id}
                  className="px-4 py-3 hover:bg-gray-50 cursor-pointer group border-b border-gray-50 last:border-0"
                  onClick={() => handleApply(search)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate text-sm">
                        {search.name}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Saved {formatDate(search.created_at)}
                      </p>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleToggleAlert(e, search)}
                        className={`p-1 rounded ${
                          search.alert_enabled
                            ? 'text-blue-600 hover:bg-blue-50'
                            : 'text-gray-400 hover:bg-gray-100'
                        }`}
                        title={search.alert_enabled ? 'Disable alerts' : 'Enable alerts'}
                      >
                        {search.alert_enabled ? (
                          <Bell className="h-4 w-4" />
                        ) : (
                          <BellOff className="h-4 w-4" />
                        )}
                      </button>
                      <button
                        onClick={(e) => handleDeleteClick(e, search)}
                        className="p-1 rounded text-gray-400 hover:text-red-600 hover:bg-red-50"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <Play className="h-3 w-3 text-gray-400" />
                    <span className="text-xs text-gray-400">Click to apply</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </PopoverContent>
      </Popover>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete saved search?</AlertDialogTitle>
            <AlertDialogDescription>
              Delete "{searchToDelete?.name}"? This cannot be undone.
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
