from flask import Blueprint, request, jsonify
from src.services.price_history import (
    get_price_history,
    get_price_statistics,
    get_price_trend,
    record_price,
    bulk_record_prices
)
from src.models.material import Material
from src.cache import cache, CACHE_TIMEOUTS, make_cache_key

price_history_bp = Blueprint('price_history', __name__)


@price_history_bp.route('/materials/<int:material_id>/price-history', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['price_history'], make_cache_key=make_cache_key)
def get_material_price_history(material_id):
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found', 'code': 'NOT_FOUND'}), 404

    period = request.args.get('period', '30d')
    period_days = parse_period(period)

    history = get_price_history(material_id, period_days)
    stats = get_price_statistics(material_id, period_days)
    trend = get_price_trend(material_id, period_days)

    return jsonify({
        'material_id': material_id,
        'material_name': material.name,
        'period': period,
        'period_days': period_days,
        'history': history,
        'statistics': stats,
        'trend': trend
    })


@price_history_bp.route('/materials/<int:material_id>/price-history', methods=['POST'])
def add_price_record(material_id):
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found', 'code': 'NOT_FOUND'}), 404

    data = request.get_json()
    if not data or 'price' not in data:
        return jsonify({'error': 'Price is required', 'code': 'VALIDATION_ERROR'}), 400

    price = data.get('price')
    source = data.get('source', 'manual')

    if not isinstance(price, (int, float)) or price < 0:
        return jsonify({'error': 'Price must be a non-negative number', 'code': 'VALIDATION_ERROR'}), 400

    record = record_price(material_id, price, source)
    return jsonify(record.to_dict()), 201


@price_history_bp.route('/materials/<int:material_id>/price-statistics', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['price_history'], make_cache_key=make_cache_key)
def get_material_price_stats(material_id):
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found', 'code': 'NOT_FOUND'}), 404

    period = request.args.get('period', '30d')
    period_days = parse_period(period)

    stats = get_price_statistics(material_id, period_days)
    stats['material_id'] = material_id
    stats['material_name'] = material.name

    return jsonify(stats)


@price_history_bp.route('/price-history/snapshot', methods=['POST'])
def trigger_price_snapshot():
    recorded = bulk_record_prices(source='api_triggered')
    return jsonify({
        'message': 'Price snapshot completed',
        'recorded_count': recorded
    })


def parse_period(period_str):
    period_str = period_str.lower().strip()

    if period_str.endswith('d'):
        return int(period_str[:-1])
    elif period_str.endswith('w'):
        return int(period_str[:-1]) * 7
    elif period_str.endswith('m'):
        return int(period_str[:-1]) * 30
    elif period_str.endswith('y'):
        return int(period_str[:-1]) * 365
    else:
        try:
            return int(period_str)
        except ValueError:
            return 30
