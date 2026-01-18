from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.material import Supplier, SupplierReview
from src.services.supplier_review import (
    create_review, update_review, delete_review,
    get_supplier_reviews, get_review_statistics, get_user_review_for_supplier
)
from src.cache import cache, CACHE_TIMEOUTS, make_cache_key

supplier_review_bp = Blueprint('supplier_review', __name__)


@supplier_review_bp.route('/suppliers/<int:supplier_id>/reviews', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['supplier_reviews'], make_cache_key=make_cache_key)
def list_reviews(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    if sort_by not in ['created_at', 'rating', 'quality_rating', 'delivery_rating']:
        sort_by = 'created_at'

    result = get_supplier_reviews(supplier_id, page, per_page, sort_by, sort_order)
    return jsonify(result)


@supplier_review_bp.route('/suppliers/<int:supplier_id>/reviews/statistics', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['review_statistics'])
def review_statistics(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404

    stats = get_review_statistics(supplier_id)
    return jsonify({
        'supplier_id': supplier_id,
        'supplier_name': supplier.name,
        **stats
    })


@supplier_review_bp.route('/suppliers/<int:supplier_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404

    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'rating' not in data:
        return jsonify({'error': 'Rating is required'}), 400

    existing = get_user_review_for_supplier(supplier_id, user_id)
    if existing:
        return jsonify({'error': 'You have already reviewed this supplier'}), 400

    try:
        review = create_review(
            supplier_id=supplier_id,
            user_id=user_id,
            rating=data['rating'],
            title=data.get('title'),
            content=data.get('content'),
            quality_rating=data.get('quality_rating'),
            delivery_rating=data.get('delivery_rating'),
            communication_rating=data.get('communication_rating'),
            verified_purchase=data.get('verified_purchase', False)
        )
        return jsonify(review.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@supplier_review_bp.route('/suppliers/<int:supplier_id>/reviews/me', methods=['GET'])
@jwt_required()
def get_my_review(supplier_id):
    user_id = get_jwt_identity()
    review = get_user_review_for_supplier(supplier_id, user_id)
    if review:
        return jsonify(review)
    return jsonify({'message': 'No review found'}), 404


@supplier_review_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def edit_review(review_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        review = update_review(
            review_id=review_id,
            user_id=user_id,
            rating=data.get('rating'),
            title=data.get('title'),
            content=data.get('content'),
            quality_rating=data.get('quality_rating'),
            delivery_rating=data.get('delivery_rating'),
            communication_rating=data.get('communication_rating')
        )
        if not review:
            return jsonify({'error': 'Review not found or unauthorized'}), 404
        return jsonify(review.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@supplier_review_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def remove_review(review_id):
    user_id = get_jwt_identity()
    success = delete_review(review_id, user_id)
    if success:
        return jsonify({'message': 'Review deleted successfully'})
    return jsonify({'error': 'Review not found or unauthorized'}), 404
