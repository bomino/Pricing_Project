from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from src.models.user import db
from src.models.material import Material
from src.models.comparison import CanonicalMaterial, MaterialVariant
from src.services.comparison import (
    get_material_comparison,
    create_canonical_material,
    add_variant_to_canonical,
    get_price_statistics
)
from src.schemas.comparison import CanonicalMaterialCreate, MaterialVariantCreate

comparison_bp = Blueprint('comparison', __name__)


@comparison_bp.route('/materials/<int:material_id>/compare', methods=['GET'])
def compare_material_prices(material_id):
    try:
        result = get_material_comparison(material_id)

        if not result:
            return jsonify({
                'error': f'Material with ID {material_id} not found',
                'code': 'NOT_FOUND'
            }), 404

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@comparison_bp.route('/canonical-materials', methods=['GET'])
def get_canonical_materials():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')

        query = CanonicalMaterial.query

        if category:
            query = query.filter(CanonicalMaterial.category == category)

        materials = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'canonical_materials': [m.to_dict() for m in materials.items],
            'total': materials.total,
            'pages': materials.pages,
            'current_page': page,
            'per_page': per_page
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@comparison_bp.route('/canonical-materials/<int:canonical_id>', methods=['GET'])
def get_canonical_material(canonical_id):
    try:
        canonical = CanonicalMaterial.query.get_or_404(canonical_id)
        stats = get_price_statistics(canonical_id)

        result = canonical.to_dict()
        result['price_statistics'] = stats
        result['variants'] = [v.to_dict() for v in canonical.variants.all()]

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@comparison_bp.route('/canonical-materials', methods=['POST'])
@jwt_required()
def create_canonical():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = CanonicalMaterialCreate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    try:
        canonical = create_canonical_material(
            name=params.name,
            category=params.category,
            subcategory=params.subcategory,
            specifications=params.specifications,
            description=params.description
        )

        return jsonify(canonical.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@comparison_bp.route('/canonical-materials/<int:canonical_id>/variants', methods=['POST'])
@jwt_required()
def add_variant(canonical_id):
    canonical = CanonicalMaterial.query.get(canonical_id)
    if not canonical:
        return jsonify({
            'error': f'Canonical material with ID {canonical_id} not found',
            'code': 'NOT_FOUND'
        }), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = MaterialVariantCreate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    try:
        variant = add_variant_to_canonical(
            canonical_id=canonical_id,
            supplier_id=params.supplier_id,
            price=params.price,
            unit=params.unit,
            material_id=params.material_id,
            lead_time_days=params.lead_time_days,
            availability=params.availability,
            minimum_order=params.minimum_order
        )

        return jsonify(variant.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@comparison_bp.route('/canonical-materials/<int:canonical_id>/variants', methods=['GET'])
def get_variants(canonical_id):
    try:
        canonical = CanonicalMaterial.query.get_or_404(canonical_id)
        variants = canonical.variants.all()

        return jsonify({
            'canonical_material': canonical.to_dict(),
            'variants': [v.to_dict() for v in variants],
            'price_statistics': get_price_statistics(canonical_id)
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
