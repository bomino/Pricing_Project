import { memo, useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ClipboardPlus } from 'lucide-react'
import { FavoriteButton } from '@/components/favorites'
import { AddToBOMDialog } from '@/components/bom'

export const MaterialCard = memo(function MaterialCard({ material, showFavorite = true, showAddToBOM = true }) {
  const navigate = useNavigate()
  const [bomDialogOpen, setBomDialogOpen] = useState(false)

  const handleViewDetails = useCallback(() => {
    navigate(`/materials/${material.id}`)
  }, [navigate, material.id])

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 relative">
      {showFavorite && (
        <div className="absolute top-3 right-3">
          <FavoriteButton materialId={material.id} size="small" />
        </div>
      )}
      <div className="flex justify-between items-start mb-3 pr-8">
        <h3 className="font-semibold text-lg text-gray-900 line-clamp-2">{material.name}</h3>
        <span className={`px-2 py-1 text-xs rounded-full flex-shrink-0 ${
          material.availability === 'In Stock' ? 'bg-green-100 text-green-800' :
          material.availability === 'Limited Stock' ? 'bg-yellow-100 text-yellow-800' :
          'bg-red-100 text-red-800'
        }`}>
          {material.availability}
        </span>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-3">{material.description}</p>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Category:</span>
          <span className="font-medium">{material.category}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Price:</span>
          <span className="font-medium text-green-600">${material.price} {material.unit}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Supplier:</span>
          <span className="font-medium">{material.supplier_name}</span>
        </div>
        {material.lead_time_days && (
          <div className="flex justify-between">
            <span className="text-gray-500">Lead Time:</span>
            <span className="font-medium">{material.lead_time_days} days</span>
          </div>
        )}
        {material.sustainability_score && (
          <div className="flex justify-between">
            <span className="text-gray-500">Sustainability:</span>
            <span className="font-medium">{material.sustainability_score}/10</span>
          </div>
        )}
      </div>

      <div className="flex gap-2 mt-4">
        <button
          onClick={handleViewDetails}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          View Details
        </button>
        {showAddToBOM && (
          <button
            onClick={() => setBomDialogOpen(true)}
            className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            title="Add to BOM"
          >
            <ClipboardPlus className="h-5 w-5 text-gray-600" />
          </button>
        )}
      </div>

      <AddToBOMDialog
        material={material}
        open={bomDialogOpen}
        onOpenChange={setBomDialogOpen}
      />
    </div>
  )
})
