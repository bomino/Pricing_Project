from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from src.services.bom import (
    create_bom, get_user_boms, get_bom_by_id, update_bom, delete_bom,
    add_item_to_bom, update_bom_item, remove_item_from_bom, get_bom_item,
    duplicate_bom, refresh_all_prices, export_bom_to_csv, get_bom_summary,
    reorder_items
)
from src.schemas.bom import (
    BOMCreate, BOMUpdate, BOMItemCreate, BOMItemUpdate, BOMItemReorder, BOMDuplicate
)

bom_bp = Blueprint('bom', __name__)


@bom_bp.route('/boms', methods=['GET'])
@jwt_required()
def list_boms():
    user_id = int(get_jwt_identity())
    status = request.args.get('status')

    try:
        boms = get_user_boms(user_id, status)
        return jsonify({
            'boms': [bom.to_dict() for bom in boms],
            'total': len(boms)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms', methods=['POST'])
@jwt_required()
def create_new_bom():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = BOMCreate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    try:
        bom = create_bom(
            user_id=user_id,
            name=params.name,
            description=params.description,
            project_id=params.project_id
        )
        return jsonify(bom.to_dict(include_items=True)), 201
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>', methods=['GET'])
@jwt_required()
def get_bom(bom_id):
    user_id = int(get_jwt_identity())

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    return jsonify(bom.to_dict(include_items=True))


@bom_bp.route('/boms/<int:bom_id>', methods=['PUT'])
@jwt_required()
def update_existing_bom(bom_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = BOMUpdate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    try:
        bom = update_bom(
            bom=bom,
            name=params.name,
            description=params.description,
            status=params.status,
            project_id=params.project_id
        )
        return jsonify(bom.to_dict(include_items=True))
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>', methods=['DELETE'])
@jwt_required()
def delete_existing_bom(bom_id):
    user_id = int(get_jwt_identity())

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    try:
        delete_bom(bom)
        return jsonify({'message': 'BOM deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>/items', methods=['GET'])
@jwt_required()
def list_bom_items(bom_id):
    user_id = int(get_jwt_identity())

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    items = bom.items.order_by('sort_order').all()
    return jsonify({
        'items': [item.to_dict() for item in items],
        'total': len(items),
        'total_cost': bom.total_cost
    })


@bom_bp.route('/boms/<int:bom_id>/items', methods=['POST'])
@jwt_required()
def add_bom_item(bom_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = BOMItemCreate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    try:
        item = add_item_to_bom(
            bom_id=bom_id,
            material_id=params.material_id,
            quantity=params.quantity,
            notes=params.notes,
            sort_order=params.sort_order
        )
        if not item:
            return jsonify({
                'error': f'Material with ID {params.material_id} not found',
                'code': 'NOT_FOUND'
            }), 404

        return jsonify(item.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>/items/<int:item_id>', methods=['GET'])
@jwt_required()
def get_bom_item_detail(bom_id, item_id):
    user_id = int(get_jwt_identity())

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    item = get_bom_item(item_id, bom_id)
    if not item:
        return jsonify({'error': 'Item not found', 'code': 'NOT_FOUND'}), 404

    return jsonify(item.to_dict())


@bom_bp.route('/boms/<int:bom_id>/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_bom_item_route(bom_id, item_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = BOMItemUpdate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    item = get_bom_item(item_id, bom_id)
    if not item:
        return jsonify({'error': 'Item not found', 'code': 'NOT_FOUND'}), 404

    try:
        item = update_bom_item(
            item=item,
            quantity=params.quantity,
            notes=params.notes,
            sort_order=params.sort_order,
            refresh_price=params.refresh_price or False
        )
        return jsonify(item.to_dict())
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_bom_item(bom_id, item_id):
    user_id = int(get_jwt_identity())

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    item = get_bom_item(item_id, bom_id)
    if not item:
        return jsonify({'error': 'Item not found', 'code': 'NOT_FOUND'}), 404

    try:
        remove_item_from_bom(item)
        return jsonify({'message': 'Item removed successfully'})
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>/items/reorder', methods=['POST'])
@jwt_required()
def reorder_bom_items(bom_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = BOMItemReorder(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    try:
        reorder_items(bom_id, params.item_order)
        return jsonify({'message': 'Items reordered successfully'})
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_existing_bom(bom_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    try:
        params = BOMDuplicate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    try:
        new_bom = duplicate_bom(bom, params.new_name)
        return jsonify(new_bom.to_dict(include_items=True)), 201
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>/refresh-prices', methods=['POST'])
@jwt_required()
def refresh_bom_prices(bom_id):
    user_id = int(get_jwt_identity())

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    try:
        result = refresh_all_prices(bom)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>/summary', methods=['GET'])
@jwt_required()
def get_bom_summary_route(bom_id):
    user_id = int(get_jwt_identity())

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    try:
        summary = get_bom_summary(bom)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@bom_bp.route('/boms/<int:bom_id>/export', methods=['GET'])
@jwt_required()
def export_bom(bom_id):
    user_id = int(get_jwt_identity())
    export_format = request.args.get('format', 'csv')

    bom = get_bom_by_id(bom_id, user_id)
    if not bom:
        return jsonify({'error': 'BOM not found', 'code': 'NOT_FOUND'}), 404

    try:
        if export_format == 'csv':
            csv_content = export_bom_to_csv(bom)
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename="{bom.name}.csv"'
                }
            )
        else:
            return jsonify({'error': 'Unsupported format', 'code': 'VALIDATION_ERROR'}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
