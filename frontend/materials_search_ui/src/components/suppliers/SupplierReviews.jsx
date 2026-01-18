import { useState, useEffect } from 'react'
import { Star, ThumbsUp, MessageSquare, Truck, PenSquare } from 'lucide-react'
import { ReviewForm } from './ReviewForm'
import { useAuth } from '@/contexts/AuthContext'

export function SupplierReviews({ supplierId }) {
  const { isAuthenticated } = useAuth()
  const [reviews, setReviews] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [showReviewForm, setShowReviewForm] = useState(false)

  useEffect(() => {
    const fetchReviews = async () => {
      if (!supplierId) return

      setLoading(true)
      try {
        const [reviewsRes, statsRes] = await Promise.all([
          fetch(`/api/v1/suppliers/${supplierId}/reviews?page=${page}&per_page=5`),
          fetch(`/api/v1/suppliers/${supplierId}/reviews/statistics`)
        ])

        if (!reviewsRes.ok || !statsRes.ok) {
          throw new Error('Failed to fetch reviews')
        }

        const reviewsData = await reviewsRes.json()
        const statsData = await statsRes.json()

        setReviews(reviewsData.reviews)
        setTotalPages(reviewsData.pages)
        setStatistics(statsData)
        setError(null)
      } catch (err) {
        console.error('Error fetching reviews:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchReviews()
  }, [supplierId, page])

  const renderStars = (rating, size = 'sm') => {
    const sizeClass = size === 'lg' ? 'h-5 w-5' : 'h-4 w-4'
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`${sizeClass} ${
              star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    )
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (loading && !statistics) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Reviews</h3>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Reviews</h3>
        <p className="text-gray-500 text-center">Unable to load reviews</p>
      </div>
    )
  }

  const handleReviewSubmit = (newReview) => {
    setShowReviewForm(false)
    setReviews([newReview, ...reviews])
    if (statistics) {
      setStatistics({
        ...statistics,
        total_reviews: statistics.total_reviews + 1
      })
    }
    setPage(1)
  }

  if (showReviewForm) {
    return (
      <ReviewForm
        supplierId={supplierId}
        onSubmit={handleReviewSubmit}
        onCancel={() => setShowReviewForm(false)}
      />
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Customer Reviews</h3>
        {isAuthenticated && (
          <button
            onClick={() => setShowReviewForm(true)}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <PenSquare className="h-4 w-4" />
            Write Review
          </button>
        )}
      </div>

      {statistics && (
        <div className="mb-6 pb-6 border-b border-gray-200">
          <div className="flex items-start gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-gray-900">
                {statistics.avg_rating?.toFixed(1) || '-'}
              </div>
              {renderStars(Math.round(statistics.avg_rating || 0), 'lg')}
              <p className="text-sm text-gray-500 mt-1">
                {statistics.total_reviews} reviews
              </p>
            </div>

            <div className="flex-1">
              <div className="space-y-2">
                {[5, 4, 3, 2, 1].map((rating) => {
                  const count = statistics.rating_distribution?.[rating] || 0
                  const percentage = statistics.total_reviews > 0
                    ? (count / statistics.total_reviews) * 100
                    : 0
                  return (
                    <div key={rating} className="flex items-center gap-2 text-sm">
                      <span className="w-3">{rating}</span>
                      <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-yellow-400 rounded-full"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="w-8 text-gray-500">{count}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {(statistics.avg_quality || statistics.avg_delivery || statistics.avg_communication) && (
            <div className="mt-4 grid grid-cols-3 gap-4">
              {statistics.avg_quality && (
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <ThumbsUp className="h-5 w-5 mx-auto text-blue-600 mb-1" />
                  <div className="text-lg font-semibold">{statistics.avg_quality.toFixed(1)}</div>
                  <div className="text-xs text-gray-500">Quality</div>
                </div>
              )}
              {statistics.avg_delivery && (
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <Truck className="h-5 w-5 mx-auto text-green-600 mb-1" />
                  <div className="text-lg font-semibold">{statistics.avg_delivery.toFixed(1)}</div>
                  <div className="text-xs text-gray-500">Delivery</div>
                </div>
              )}
              {statistics.avg_communication && (
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <MessageSquare className="h-5 w-5 mx-auto text-purple-600 mb-1" />
                  <div className="text-lg font-semibold">{statistics.avg_communication.toFixed(1)}</div>
                  <div className="text-xs text-gray-500">Communication</div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {reviews.length > 0 ? (
        <div className="space-y-4">
          {reviews.map((review) => (
            <div key={review.id} className="pb-4 border-b border-gray-100 last:border-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {renderStars(review.rating)}
                  {review.verified_purchase && (
                    <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                      Verified
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-500">
                  {formatDate(review.created_at)}
                </span>
              </div>

              {review.title && (
                <h4 className="font-medium text-gray-900 mb-1">{review.title}</h4>
              )}

              {review.content && (
                <p className="text-sm text-gray-600 mb-2">{review.content}</p>
              )}

              {(review.quality_rating || review.delivery_rating || review.communication_rating) && (
                <div className="flex gap-4 text-xs text-gray-500">
                  {review.quality_rating && (
                    <span>Quality: {review.quality_rating}/5</span>
                  )}
                  {review.delivery_rating && (
                    <span>Delivery: {review.delivery_rating}/5</span>
                  )}
                  {review.communication_rating && (
                    <span>Communication: {review.communication_rating}/5</span>
                  )}
                </div>
              )}
            </div>
          ))}

          {totalPages > 1 && (
            <div className="flex justify-center gap-2 pt-4">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <Star className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p>No reviews yet</p>
          <p className="text-sm">Be the first to review this supplier</p>
        </div>
      )}
    </div>
  )
}
