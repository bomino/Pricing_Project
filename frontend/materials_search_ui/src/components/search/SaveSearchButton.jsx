import { useState } from 'react'
import { Bookmark, Bell, BellOff } from 'lucide-react'
import { toast } from 'sonner'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { useSavedSearches } from '@/hooks/useSavedSearches'
import { useAuth } from '@/contexts/AuthContext'

export function SaveSearchButton({ queryParams, disabled = false }) {
  const { isAuthenticated } = useAuth()
  const { createSavedSearch } = useSavedSearches()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [name, setName] = useState('')
  const [alertEnabled, setAlertEnabled] = useState(false)
  const [saving, setSaving] = useState(false)

  const hasActiveFilters = () => {
    if (!queryParams) return false
    const { q, category, min_price, max_price, availability, supplier, sort_by } = queryParams
    return !!(q || category || min_price || max_price || availability || supplier || sort_by)
  }

  const handleOpen = () => {
    if (!isAuthenticated) {
      toast.error('Please log in to save searches')
      return
    }
    setDialogOpen(true)
    setName('')
    setAlertEnabled(false)
  }

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error('Please enter a name')
      return
    }

    setSaving(true)
    try {
      await createSavedSearch({
        name: name.trim(),
        query_params: queryParams,
        alert_enabled: alertEnabled
      })
      toast.success('Search saved successfully')
      setDialogOpen(false)
    } catch (err) {
      toast.error(err.message || 'Failed to save search')
    } finally {
      setSaving(false)
    }
  }

  const buildDescription = () => {
    if (!queryParams) return 'No filters applied'

    const parts = []
    if (queryParams.q) parts.push(`"${queryParams.q}"`)
    if (queryParams.category) parts.push(`Category: ${queryParams.category}`)
    if (queryParams.min_price || queryParams.max_price) {
      const priceRange = `$${queryParams.min_price || 0} - $${queryParams.max_price || '∞'}`
      parts.push(`Price: ${priceRange}`)
    }
    if (queryParams.availability) parts.push(`Availability: ${queryParams.availability}`)
    if (queryParams.supplier) parts.push(`Supplier: ${queryParams.supplier}`)
    if (queryParams.sort_by) parts.push(`Sort: ${queryParams.sort_by}`)

    return parts.length > 0 ? parts.join(' • ') : 'All materials'
  }

  if (!hasActiveFilters()) {
    return null
  }

  return (
    <>
      <button
        onClick={handleOpen}
        disabled={disabled}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
        title="Save this search"
      >
        <Bookmark className="h-4 w-4" />
        Save Search
      </button>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Save Search</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm text-gray-600">{buildDescription()}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Steel suppliers under $100"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Price alerts
                </label>
                <p className="text-xs text-gray-500 mt-0.5">
                  Get notified when prices change
                </p>
              </div>
              <button
                onClick={() => setAlertEnabled(!alertEnabled)}
                className={`p-2 rounded-lg transition-colors ${
                  alertEnabled
                    ? 'bg-blue-100 text-blue-600'
                    : 'bg-gray-100 text-gray-400'
                }`}
              >
                {alertEnabled ? (
                  <Bell className="h-5 w-5" />
                ) : (
                  <BellOff className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          <DialogFooter>
            <button
              onClick={() => setDialogOpen(false)}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !name.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {saving ? 'Saving...' : 'Save Search'}
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
