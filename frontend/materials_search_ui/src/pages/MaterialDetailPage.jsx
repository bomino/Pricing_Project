import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, ClipboardPlus } from 'lucide-react'
import { PriceHistoryChart } from '@/components/materials/PriceHistoryChart'
import { PriceComparisonTable } from '@/components/comparison'
import { SupplierReviews } from '@/components/suppliers/SupplierReviews'
import { AuthHeader } from '@/components/auth'
import { FavoriteButton } from '@/components/favorites'
import { AddToBOMDialog } from '@/components/bom'

export function MaterialDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [material, setMaterial] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [bomDialogOpen, setBomDialogOpen] = useState(false)

  useEffect(() => {
    const fetchMaterial = async () => {
      setLoading(true)
      try {
        const response = await fetch(`/api/v1/materials/${id}`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        setMaterial(data)
        setError(null)
      } catch (err) {
        console.error('Error fetching material:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchMaterial()
  }, [id])

  const handleBack = () => {
    navigate(-1)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading material details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <p className="text-lg">Error: {error}</p>
          </div>
          <button
            onClick={handleBack}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  if (!material) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 text-lg">Material not found</p>
          <button
            onClick={handleBack}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Go Back
          </button>
        </div>
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
              <button
                onClick={handleBack}
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Search
              </button>
            </div>
            <AuthHeader />
          </div>
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold text-gray-900">{material.name}</h1>
            <FavoriteButton materialId={material.id} size="large" />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Description</h2>
              <p className="text-gray-600">{material.description}</p>

              {material.specifications && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Specifications</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {typeof material.specifications === 'object' ? (
                      Object.entries(material.specifications).map(([key, value]) => (
                        <div key={key} className="flex justify-between border-b border-gray-100 pb-2">
                          <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="font-medium">{value}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-600">{material.specifications}</p>
                    )}
                  </div>
                </div>
              )}

              {material.certifications && material.certifications.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Certifications</h3>
                  <div className="flex flex-wrap gap-2">
                    {material.certifications.map((cert, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                      >
                        {cert}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-8">
              <PriceComparisonTable materialId={material.id} />
            </div>

            <div className="mt-8">
              <PriceHistoryChart materialId={material.id} />
            </div>

            {material.supplier_id && (
              <div className="mt-8">
                <SupplierReviews supplierId={material.supplier_id} />
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-6">
              <div className="text-center mb-6">
                <span className={`px-3 py-1 text-sm rounded-full ${
                  material.availability === 'In Stock' ? 'bg-green-100 text-green-800' :
                  material.availability === 'Limited Stock' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {material.availability}
                </span>
              </div>

              <div className="text-center mb-6">
                <p className="text-3xl font-bold text-green-600">${material.price}</p>
                <p className="text-gray-500">{material.unit}</p>
              </div>

              <div className="space-y-4 text-sm">
                <div className="flex justify-between border-b border-gray-100 pb-2">
                  <span className="text-gray-500">Category:</span>
                  <span className="font-medium">{material.category}</span>
                </div>
                {material.subcategory && (
                  <div className="flex justify-between border-b border-gray-100 pb-2">
                    <span className="text-gray-500">Subcategory:</span>
                    <span className="font-medium">{material.subcategory}</span>
                  </div>
                )}
                {material.lead_time_days && (
                  <div className="flex justify-between border-b border-gray-100 pb-2">
                    <span className="text-gray-500">Lead Time:</span>
                    <span className="font-medium">{material.lead_time_days} days</span>
                  </div>
                )}
                {material.minimum_order && (
                  <div className="flex justify-between border-b border-gray-100 pb-2">
                    <span className="text-gray-500">Minimum Order:</span>
                    <span className="font-medium">{material.minimum_order}</span>
                  </div>
                )}
                {material.sustainability_rating && (
                  <div className="flex justify-between border-b border-gray-100 pb-2">
                    <span className="text-gray-500">Sustainability:</span>
                    <span className="font-medium">{material.sustainability_rating}</span>
                  </div>
                )}
              </div>

              {material.supplier && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Supplier</h3>
                  <p className="font-medium">{material.supplier.name}</p>
                  {material.supplier.rating && (
                    <p className="text-sm text-gray-500 mt-1">
                      Rating: {material.supplier.rating}/5
                    </p>
                  )}
                </div>
              )}

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setBomDialogOpen(true)}
                  className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <ClipboardPlus className="h-5 w-5" />
                  Add to BOM
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <AddToBOMDialog
        material={material}
        open={bomDialogOpen}
        onOpenChange={setBomDialogOpen}
      />
    </div>
  )
}
