from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.user import db
from src.models.material import DataProvider, PriceSource, SyncJob
from src.tasks.sync_tasks import sync_provider

data_integration_bp = Blueprint('data_integration', __name__)


@data_integration_bp.route('/providers', methods=['GET'])
def list_providers():
    providers = DataProvider.query.all()
    return jsonify({
        'providers': [p.to_dict() for p in providers]
    })


@data_integration_bp.route('/providers/<int:provider_id>', methods=['GET'])
def get_provider(provider_id):
    provider = DataProvider.query.get_or_404(provider_id)
    return jsonify(provider.to_dict())


@data_integration_bp.route('/providers', methods=['POST'])
@jwt_required()
def create_provider():
    data = request.get_json()

    required_fields = ['name', 'provider_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    provider = DataProvider(
        name=data['name'],
        provider_type=data['provider_type'],
        base_url=data.get('base_url'),
        api_key_encrypted=data.get('api_key'),
        config=data.get('config', {}),
        is_active=data.get('is_active', True),
        rate_limit_requests=data.get('rate_limit_requests', 100),
        rate_limit_period=data.get('rate_limit_period', 3600),
        sync_interval_hours=data.get('sync_interval_hours', 24)
    )

    db.session.add(provider)
    db.session.commit()

    return jsonify(provider.to_dict()), 201


@data_integration_bp.route('/providers/<int:provider_id>', methods=['PUT'])
@jwt_required()
def update_provider(provider_id):
    provider = DataProvider.query.get_or_404(provider_id)
    data = request.get_json()

    if 'name' in data:
        provider.name = data['name']
    if 'base_url' in data:
        provider.base_url = data['base_url']
    if 'api_key' in data:
        provider.api_key_encrypted = data['api_key']
    if 'config' in data:
        provider.config = data['config']
    if 'is_active' in data:
        provider.is_active = data['is_active']
    if 'rate_limit_requests' in data:
        provider.rate_limit_requests = data['rate_limit_requests']
    if 'sync_interval_hours' in data:
        provider.sync_interval_hours = data['sync_interval_hours']

    db.session.commit()
    return jsonify(provider.to_dict())


@data_integration_bp.route('/providers/<int:provider_id>', methods=['DELETE'])
@jwt_required()
def delete_provider(provider_id):
    provider = DataProvider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    return jsonify({'message': 'Provider deleted'})


@data_integration_bp.route('/providers/<int:provider_id>/sync', methods=['POST'])
@jwt_required()
def trigger_sync(provider_id):
    provider = DataProvider.query.get_or_404(provider_id)

    if not provider.is_active:
        return jsonify({'error': 'Provider is not active'}), 400

    data = request.get_json() or {}
    job_type = data.get('job_type', 'full')

    task = sync_provider.delay(provider_id, job_type)

    return jsonify({
        'message': 'Sync job queued',
        'task_id': task.id,
        'provider_id': provider_id,
        'job_type': job_type
    })


@data_integration_bp.route('/sync-jobs', methods=['GET'])
def list_sync_jobs():
    provider_id = request.args.get('provider_id', type=int)
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = SyncJob.query

    if provider_id:
        query = query.filter_by(provider_id=provider_id)
    if status:
        query = query.filter_by(status=status)

    query = query.order_by(SyncJob.created_at.desc())
    jobs = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'jobs': [j.to_dict() for j in jobs.items],
        'total': jobs.total,
        'page': page,
        'per_page': per_page,
        'has_next': jobs.has_next,
        'has_prev': jobs.has_prev
    })


@data_integration_bp.route('/sync-jobs/<int:job_id>', methods=['GET'])
def get_sync_job(job_id):
    job = SyncJob.query.get_or_404(job_id)
    return jsonify(job.to_dict())


@data_integration_bp.route('/price-sources', methods=['GET'])
def list_price_sources():
    material_id = request.args.get('material_id', type=int)
    provider_id = request.args.get('provider_id', type=int)
    valid_only = request.args.get('valid_only', 'true').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = PriceSource.query

    if material_id:
        query = query.filter_by(material_id=material_id)
    if provider_id:
        query = query.filter_by(provider_id=provider_id)
    if valid_only:
        query = query.filter_by(is_valid=True)

    query = query.order_by(PriceSource.fetched_at.desc())
    sources = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'price_sources': [s.to_dict() for s in sources.items],
        'total': sources.total,
        'page': page,
        'per_page': per_page
    })


@data_integration_bp.route('/materials/<int:material_id>/price-sources', methods=['GET'])
def get_material_price_sources(material_id):
    valid_only = request.args.get('valid_only', 'true').lower() == 'true'

    query = PriceSource.query.filter_by(material_id=material_id)
    if valid_only:
        query = query.filter_by(is_valid=True)

    sources = query.order_by(PriceSource.confidence_score.desc()).all()

    prices = [s.price for s in sources]
    avg_price = sum(prices) / len(prices) if prices else None
    min_price = min(prices) if prices else None
    max_price = max(prices) if prices else None

    return jsonify({
        'material_id': material_id,
        'price_sources': [s.to_dict() for s in sources],
        'statistics': {
            'count': len(sources),
            'average_price': round(avg_price, 2) if avg_price else None,
            'min_price': min_price,
            'max_price': max_price,
            'price_spread': round(max_price - min_price, 2) if min_price and max_price else None
        }
    })
