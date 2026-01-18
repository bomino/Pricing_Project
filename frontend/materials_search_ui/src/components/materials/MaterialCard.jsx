import { useNavigate } from 'react-router-dom'

export function MaterialCard({ material }) {
  const navigate = useNavigate()

  const handleViewDetails = () => {
    navigate(`/materials/${material.id}`)
  }

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-lg text-gray-900 line-clamp-2">{material.name}</h3>
        <span className={`px-2 py-1 text-xs rounded-full ${
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

      <button
        onClick={handleViewDetails}
        className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
      >
        View Details
      </button>
    </div>
  )
}
