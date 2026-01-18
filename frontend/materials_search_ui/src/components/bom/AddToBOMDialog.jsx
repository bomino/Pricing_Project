import { useState, useEffect } from 'react'
import { Plus, Folder } from 'lucide-react'
import { toast } from 'sonner'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { useBOM } from '@/hooks/useBOM'
import { useAuth } from '@/contexts/AuthContext'

export function AddToBOMDialog({ material, open, onOpenChange }) {
  const { isAuthenticated } = useAuth()
  const { boms, fetchBoms, createBom, addItem, loading } = useBOM()
  const [selectedBomId, setSelectedBomId] = useState(null)
  const [quantity, setQuantity] = useState(1)
  const [notes, setNotes] = useState('')
  const [showNewBomForm, setShowNewBomForm] = useState(false)
  const [newBomName, setNewBomName] = useState('')
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    if (open && isAuthenticated) {
      fetchBoms()
    }
  }, [open, isAuthenticated, fetchBoms])

  useEffect(() => {
    if (open) {
      setQuantity(1)
      setNotes('')
      setShowNewBomForm(false)
      setNewBomName('')
      setSelectedBomId(boms.length > 0 ? boms[0].id : null)
    }
  }, [open, boms.length])

  const handleAddToBOM = async () => {
    if (!material?.id) return

    setAdding(true)
    try {
      let targetBomId = selectedBomId

      if (showNewBomForm && newBomName.trim()) {
        const newBom = await createBom({ name: newBomName.trim() })
        targetBomId = newBom.id
      }

      if (!targetBomId) {
        toast.error('Please select or create a BOM')
        return
      }

      await addItem(targetBomId, {
        material_id: material.id,
        quantity,
        notes: notes.trim()
      })

      toast.success(`Added ${material.name} to BOM`)
      onOpenChange(false)
    } catch (err) {
      toast.error(err.message || 'Failed to add to BOM')
    } finally {
      setAdding(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add to BOM</DialogTitle>
          </DialogHeader>
          <div className="py-6 text-center">
            <p className="text-gray-500">Please log in to add materials to a BOM.</p>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add to Bill of Materials</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="font-medium text-gray-900">{material?.name}</p>
            {material?.price && (
              <p className="text-sm text-gray-500 mt-1">
                ${Number(material.price).toFixed(2)} per {material.unit || 'unit'}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select BOM
            </label>
            {loading ? (
              <div className="h-20 flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              </div>
            ) : boms.length > 0 && !showNewBomForm ? (
              <div className="space-y-2">
                {boms.map((bom) => (
                  <label
                    key={bom.id}
                    className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedBomId === bom.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="bom"
                      value={bom.id}
                      checked={selectedBomId === bom.id}
                      onChange={() => setSelectedBomId(bom.id)}
                      className="text-blue-600"
                    />
                    <Folder className="h-4 w-4 text-gray-400" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{bom.name}</p>
                      <p className="text-xs text-gray-500">
                        {bom.item_count || 0} items
                      </p>
                    </div>
                  </label>
                ))}
                <button
                  onClick={() => setShowNewBomForm(true)}
                  className="w-full flex items-center justify-center gap-2 p-3 border border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-gray-400 hover:text-gray-600 transition-colors"
                >
                  <Plus className="h-4 w-4" />
                  Create new BOM
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <input
                  type="text"
                  value={newBomName}
                  onChange={(e) => setNewBomName(e.target.value)}
                  placeholder="Enter BOM name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                />
                {boms.length > 0 && (
                  <button
                    onClick={() => setShowNewBomForm(false)}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    ← Back to existing BOMs
                  </button>
                )}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes about this item..."
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
        </div>

        <DialogFooter>
          <button
            onClick={() => onOpenChange(false)}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleAddToBOM}
            disabled={adding || (showNewBomForm && !newBomName.trim()) || (!showNewBomForm && !selectedBomId)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {adding ? 'Adding...' : 'Add to BOM'}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
