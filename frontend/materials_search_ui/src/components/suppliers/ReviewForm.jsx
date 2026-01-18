import { useState } from 'react'
import { Star } from 'lucide-react'

export function ReviewForm({ supplierId, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    rating: 0,
    title: '',
    content: '',
    quality_rating: 0,
    delivery_rating: 0,
    communication_rating: 0
  })
  const [hoveredRating, setHoveredRating] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (formData.rating === 0) {
      setError('Please select an overall rating')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setError('Please log in to submit a review')
        return
      }

      const response = await fetch(`/api/v1/suppliers/${supplierId}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          rating: formData.rating,
          title: formData.title || null,
          content: formData.content || null,
          quality_rating: formData.quality_rating || null,
          delivery_rating: formData.delivery_rating || null,
          communication_rating: formData.communication_rating || null
        })
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.error || 'Failed to submit review')
      }

      const review = await response.json()
      if (onSubmit) onSubmit(review)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const StarRating = ({ value, onChange, label }) => (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600 w-28">{label}</span>
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange(star)}
            className="focus:outline-none"
          >
            <Star
              className={`h-5 w-5 transition-colors ${
                star <= value
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'text-gray-300 hover:text-yellow-300'
              }`}
            />
          </button>
        ))}
      </div>
      {value > 0 && <span className="text-sm text-gray-500">{value}/5</span>}
    </div>
  )

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Write a Review</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Overall Rating *
          </label>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onMouseEnter={() => setHoveredRating(star)}
                onMouseLeave={() => setHoveredRating(0)}
                onClick={() => setFormData({ ...formData, rating: star })}
                className="focus:outline-none"
              >
                <Star
                  className={`h-8 w-8 transition-colors ${
                    star <= (hoveredRating || formData.rating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Review Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Summarize your experience"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            maxLength={200}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Your Review
          </label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            placeholder="Share details about your experience with this supplier"
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="pt-4 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-3">
            Rate specific aspects (optional)
          </p>
          <div className="space-y-2">
            <StarRating
              label="Quality"
              value={formData.quality_rating}
              onChange={(v) => setFormData({ ...formData, quality_rating: v })}
            />
            <StarRating
              label="Delivery"
              value={formData.delivery_rating}
              onChange={(v) => setFormData({ ...formData, delivery_rating: v })}
            />
            <StarRating
              label="Communication"
              value={formData.communication_rating}
              onChange={(v) => setFormData({ ...formData, communication_rating: v })}
            />
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Submitting...' : 'Submit Review'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  )
}
