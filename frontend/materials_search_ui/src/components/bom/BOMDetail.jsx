import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Trash2, Plus, Minus, RefreshCw, Download, ExternalLink } from 'lucide-react'
import { toast } from 'sonner'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableFooter,
} from '@/components/ui/table'
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

export function BOMDetail({
  bom,
  onUpdateItem,
  onRemoveItem,
  onRefreshPrices,
  onExport,
  refreshing = false
}) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [itemToDelete, setItemToDelete] = useState(null)
  const [updatingItems, setUpdatingItems] = useState({})

  const items = bom?.items || []

  const formatCurrency = (amount) => {
    if (amount == null) return '$0.00'
    return `$${Number(amount).toFixed(2)}`
  }

  const handleQuantityChange = async (item, delta) => {
    const newQuantity = Math.max(1, (item.quantity || 1) + delta)
    if (newQuantity === item.quantity) return

    setUpdatingItems(prev => ({ ...prev, [item.id]: true }))
    try {
      await onUpdateItem(bom.id, item.id, { quantity: newQuantity })
    } catch {
      toast.error('Failed to update quantity')
    } finally {
      setUpdatingItems(prev => ({ ...prev, [item.id]: false }))
    }
  }

  const handleDeleteClick = (item) => {
    setItemToDelete(item)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (itemToDelete) {
      try {
        await onRemoveItem(bom.id, itemToDelete.id)
        toast.success('Item removed')
      } catch {
        toast.error('Failed to remove item')
      }
    }
    setDeleteDialogOpen(false)
    setItemToDelete(null)
  }

  const handleRefreshPrices = async () => {
    try {
      await onRefreshPrices(bom.id)
      toast.success('Prices refreshed')
    } catch {
      toast.error('Failed to refresh prices')
    }
  }

  const handleExport = async () => {
    try {
      await onExport(bom.id, 'csv')
      toast.success('BOM exported')
    } catch {
      toast.error('Failed to export BOM')
    }
  }

  const totalCost = items.reduce((sum, item) => {
    const price = item.unit_price_snapshot || item.material?.price || 0
    return sum + (price * (item.quantity || 1))
  }, 0)

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-500 mb-4">No items in this BOM yet.</p>
        <p className="text-sm text-gray-400">
          Search for materials and add them to this BOM using the "Add to BOM" button.
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">
            Items ({items.length})
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefreshPrices}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh Prices
            </button>
            <button
              onClick={handleExport}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40%]">Material</TableHead>
              <TableHead className="text-right">Unit Price</TableHead>
              <TableHead className="text-center">Quantity</TableHead>
              <TableHead className="text-right">Subtotal</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => {
              const material = item.material || {}
              const unitPrice = item.unit_price_snapshot || material.price || 0
              const subtotal = unitPrice * (item.quantity || 1)
              const isUpdating = updatingItems[item.id]

              return (
                <TableRow key={item.id}>
                  <TableCell>
                    <div>
                      <Link
                        to={`/materials/${material.id}`}
                        className="font-medium text-blue-600 hover:text-blue-800 inline-flex items-center gap-1"
                      >
                        {material.name || 'Unknown Material'}
                        <ExternalLink className="h-3 w-3" />
                      </Link>
                      {material.category && (
                        <p className="text-xs text-gray-500 mt-0.5">{material.category}</p>
                      )}
                      {item.notes && (
                        <p className="text-xs text-gray-400 mt-1 italic">Note: {item.notes}</p>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div>
                      <span className="font-medium">{formatCurrency(unitPrice)}</span>
                      {material.unit && (
                        <span className="text-xs text-gray-500 ml-1">/{material.unit}</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => handleQuantityChange(item, -1)}
                        disabled={isUpdating || item.quantity <= 1}
                        className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 transition-colors"
                      >
                        <Minus className="h-4 w-4" />
                      </button>
                      <span className={`w-10 text-center font-medium ${isUpdating ? 'opacity-50' : ''}`}>
                        {item.quantity || 1}
                      </span>
                      <button
                        onClick={() => handleQuantityChange(item, 1)}
                        disabled={isUpdating}
                        className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 transition-colors"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    {formatCurrency(subtotal)}
                  </TableCell>
                  <TableCell>
                    <button
                      onClick={() => handleDeleteClick(item)}
                      className="p-1 rounded text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
          <TableFooter>
            <TableRow>
              <TableCell colSpan={3} className="text-right font-semibold">
                Total
              </TableCell>
              <TableCell className="text-right font-bold text-lg text-green-600">
                {formatCurrency(totalCost)}
              </TableCell>
              <TableCell></TableCell>
            </TableRow>
          </TableFooter>
        </Table>
      </div>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove item?</AlertDialogTitle>
            <AlertDialogDescription>
              Remove "{itemToDelete?.material?.name || 'this item'}" from the BOM?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-red-600 hover:bg-red-700"
            >
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
