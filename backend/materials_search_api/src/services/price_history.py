from datetime import datetime, timedelta
from sqlalchemy import func, and_
from src.models.user import db
from src.models.material import Material, PriceHistory


def record_price(material_id, price, source='system'):
    if price is None:
        return None

    record = PriceHistory(
        material_id=material_id,
        price=price,
        source=source
    )
    db.session.add(record)
    db.session.commit()
    return record


def get_price_history(material_id, period_days=30, limit=100):
    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    history = PriceHistory.query.filter(
        and_(
            PriceHistory.material_id == material_id,
            PriceHistory.recorded_at >= cutoff_date
        )
    ).order_by(PriceHistory.recorded_at.asc()).limit(limit).all()

    return [record.to_dict() for record in history]


def get_price_statistics(material_id, period_days=30):
    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    stats = db.session.query(
        func.min(PriceHistory.price).label('min_price'),
        func.max(PriceHistory.price).label('max_price'),
        func.avg(PriceHistory.price).label('avg_price'),
        func.count(PriceHistory.id).label('data_points')
    ).filter(
        and_(
            PriceHistory.material_id == material_id,
            PriceHistory.recorded_at >= cutoff_date
        )
    ).first()

    latest = PriceHistory.query.filter(
        PriceHistory.material_id == material_id
    ).order_by(PriceHistory.recorded_at.desc()).first()

    oldest_in_period = PriceHistory.query.filter(
        and_(
            PriceHistory.material_id == material_id,
            PriceHistory.recorded_at >= cutoff_date
        )
    ).order_by(PriceHistory.recorded_at.asc()).first()

    price_change = None
    price_change_percent = None
    if latest and oldest_in_period and oldest_in_period.price:
        price_change = latest.price - oldest_in_period.price
        price_change_percent = (price_change / oldest_in_period.price) * 100

    return {
        'min_price': float(stats.min_price) if stats.min_price else None,
        'max_price': float(stats.max_price) if stats.max_price else None,
        'avg_price': round(float(stats.avg_price), 2) if stats.avg_price else None,
        'data_points': stats.data_points,
        'current_price': latest.price if latest else None,
        'price_change': round(price_change, 2) if price_change is not None else None,
        'price_change_percent': round(price_change_percent, 2) if price_change_percent is not None else None,
        'period_days': period_days
    }


def get_price_trend(material_id, period_days=30):
    history = get_price_history(material_id, period_days)

    if len(history) < 2:
        return 'insufficient_data'

    prices = [h['price'] for h in history]
    first_half_avg = sum(prices[:len(prices)//2]) / (len(prices)//2)
    second_half_avg = sum(prices[len(prices)//2:]) / (len(prices) - len(prices)//2)

    threshold = 0.02
    change_ratio = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg else 0

    if change_ratio > threshold:
        return 'increasing'
    elif change_ratio < -threshold:
        return 'decreasing'
    else:
        return 'stable'


def record_price_if_changed(material_id, new_price, source='system'):
    if new_price is None:
        return None

    latest = PriceHistory.query.filter(
        PriceHistory.material_id == material_id
    ).order_by(PriceHistory.recorded_at.desc()).first()

    if latest is None or latest.price != new_price:
        return record_price(material_id, new_price, source)

    return None


def bulk_record_prices(source='scheduled_snapshot'):
    materials = Material.query.filter(Material.price.isnot(None)).all()
    recorded_count = 0

    for material in materials:
        result = record_price_if_changed(material.id, material.price, source)
        if result:
            recorded_count += 1

    db.session.commit()
    return recorded_count
