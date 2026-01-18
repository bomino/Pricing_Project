from datetime import datetime
from sqlalchemy import func
from src.models.user import db
from src.models.material import Supplier, SupplierReview


def create_review(supplier_id, user_id, rating, title=None, content=None,
                  quality_rating=None, delivery_rating=None, communication_rating=None,
                  verified_purchase=False):
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5")

    for sub_rating in [quality_rating, delivery_rating, communication_rating]:
        if sub_rating is not None and (sub_rating < 1 or sub_rating > 5):
            raise ValueError("Sub-ratings must be between 1 and 5")

    review = SupplierReview(
        supplier_id=supplier_id,
        user_id=user_id,
        rating=rating,
        title=title,
        content=content,
        quality_rating=quality_rating,
        delivery_rating=delivery_rating,
        communication_rating=communication_rating,
        verified_purchase=verified_purchase
    )
    db.session.add(review)
    db.session.commit()

    update_supplier_aggregate_ratings(supplier_id)

    return review


def update_review(review_id, user_id, **kwargs):
    review = SupplierReview.query.filter_by(id=review_id, user_id=user_id).first()
    if not review:
        return None

    allowed_fields = ['rating', 'title', 'content', 'quality_rating',
                      'delivery_rating', 'communication_rating']

    for field in allowed_fields:
        if field in kwargs and kwargs[field] is not None:
            if field == 'rating' and (kwargs[field] < 1 or kwargs[field] > 5):
                raise ValueError("Rating must be between 1 and 5")
            if field in ['quality_rating', 'delivery_rating', 'communication_rating']:
                if kwargs[field] < 1 or kwargs[field] > 5:
                    raise ValueError("Sub-ratings must be between 1 and 5")
            setattr(review, field, kwargs[field])

    db.session.commit()
    update_supplier_aggregate_ratings(review.supplier_id)

    return review


def delete_review(review_id, user_id):
    review = SupplierReview.query.filter_by(id=review_id, user_id=user_id).first()
    if not review:
        return False

    supplier_id = review.supplier_id
    db.session.delete(review)
    db.session.commit()
    update_supplier_aggregate_ratings(supplier_id)

    return True


def get_supplier_reviews(supplier_id, page=1, per_page=10, sort_by='created_at', sort_order='desc'):
    query = SupplierReview.query.filter_by(supplier_id=supplier_id)

    if sort_order == 'desc':
        query = query.order_by(getattr(SupplierReview, sort_by).desc())
    else:
        query = query.order_by(getattr(SupplierReview, sort_by).asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'reviews': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


def get_review_statistics(supplier_id):
    stats = db.session.query(
        func.count(SupplierReview.id).label('total_reviews'),
        func.avg(SupplierReview.rating).label('avg_rating'),
        func.avg(SupplierReview.quality_rating).label('avg_quality'),
        func.avg(SupplierReview.delivery_rating).label('avg_delivery'),
        func.avg(SupplierReview.communication_rating).label('avg_communication')
    ).filter(SupplierReview.supplier_id == supplier_id).first()

    rating_distribution = db.session.query(
        SupplierReview.rating,
        func.count(SupplierReview.id).label('count')
    ).filter(
        SupplierReview.supplier_id == supplier_id
    ).group_by(SupplierReview.rating).all()

    distribution = {i: 0 for i in range(1, 6)}
    for rating, count in rating_distribution:
        distribution[rating] = count

    return {
        'total_reviews': stats.total_reviews or 0,
        'avg_rating': round(float(stats.avg_rating), 2) if stats.avg_rating else None,
        'avg_quality': round(float(stats.avg_quality), 2) if stats.avg_quality else None,
        'avg_delivery': round(float(stats.avg_delivery), 2) if stats.avg_delivery else None,
        'avg_communication': round(float(stats.avg_communication), 2) if stats.avg_communication else None,
        'rating_distribution': distribution
    }


def update_supplier_aggregate_ratings(supplier_id):
    stats = get_review_statistics(supplier_id)

    supplier = Supplier.query.get(supplier_id)
    if supplier:
        supplier.rating = stats['avg_rating'] or 0.0
        supplier.total_reviews = stats['total_reviews']
        db.session.commit()


def get_user_review_for_supplier(supplier_id, user_id):
    review = SupplierReview.query.filter_by(
        supplier_id=supplier_id,
        user_id=user_id
    ).first()
    return review.to_dict() if review else None
