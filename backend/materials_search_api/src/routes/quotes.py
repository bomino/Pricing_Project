from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from typing import Optional
from src.models.user import db
from src.models.quote import QuoteRequest
from src.models.material import Material

quotes_bp = Blueprint('quotes', __name__)


class QuoteRequestCreate(BaseModel):
    material_id: int
    contact_name: str = Field(min_length=2, max_length=200)
    contact_email: str = Field(min_length=5, max_length=200)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    company_name: Optional[str] = Field(default=None, max_length=200)
    quantity: float = Field(gt=0)
    unit: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=2000)
    preferred_contact_method: Optional[str] = Field(default='email')

    @field_validator('preferred_contact_method')
    @classmethod
    def validate_contact_method(cls, v):
        allowed = ['email', 'phone', 'either']
        if v and v not in allowed:
            raise ValueError(f'preferred_contact_method must be one of: {allowed}')
        return v


class QuoteRequestUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None
    quoted_price: Optional[float] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed = ['pending', 'contacted', 'quoted', 'closed', 'cancelled']
        if v and v not in allowed:
            raise ValueError(f'status must be one of: {allowed}')
        return v


@quotes_bp.route('/quotes', methods=['POST'])
def create_quote_request():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = QuoteRequestCreate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    material = Material.query.get(params.material_id)
    if not material:
        return jsonify({
            'error': f'Material with ID {params.material_id} not found',
            'code': 'NOT_FOUND'
        }), 404

    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = int(identity)
    except Exception:
        pass

    try:
        quote_request = QuoteRequest(
            material_id=params.material_id,
            user_id=user_id,
            contact_name=params.contact_name,
            contact_email=params.contact_email,
            contact_phone=params.contact_phone,
            company_name=params.company_name,
            quantity=params.quantity,
            unit=params.unit or material.unit,
            notes=params.notes,
            preferred_contact_method=params.preferred_contact_method,
            status='pending'
        )

        db.session.add(quote_request)
        db.session.commit()

        return jsonify({
            'message': 'Quote request submitted successfully',
            'quote_request': quote_request.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@quotes_bp.route('/quotes', methods=['GET'])
@jwt_required()
def get_quote_requests():
    user_id = int(get_jwt_identity())

    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')

        query = QuoteRequest.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(QuoteRequest.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'quote_requests': [qr.to_dict() for qr in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@quotes_bp.route('/quotes/<int:quote_id>', methods=['GET'])
@jwt_required()
def get_quote_request(quote_id):
    user_id = int(get_jwt_identity())

    try:
        quote_request = QuoteRequest.query.filter_by(
            id=quote_id,
            user_id=user_id
        ).first()

        if not quote_request:
            return jsonify({
                'error': 'Quote request not found',
                'code': 'NOT_FOUND'
            }), 404

        return jsonify(quote_request.to_dict())

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@quotes_bp.route('/quotes/<int:quote_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_quote_request(quote_id):
    user_id = int(get_jwt_identity())

    try:
        quote_request = QuoteRequest.query.filter_by(
            id=quote_id,
            user_id=user_id
        ).first()

        if not quote_request:
            return jsonify({
                'error': 'Quote request not found',
                'code': 'NOT_FOUND'
            }), 404

        if quote_request.status in ['quoted', 'closed']:
            return jsonify({
                'error': 'Cannot cancel a quote that has already been processed',
                'code': 'INVALID_STATE'
            }), 400

        quote_request.status = 'cancelled'
        db.session.commit()

        return jsonify({
            'message': 'Quote request cancelled',
            'quote_request': quote_request.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@quotes_bp.route('/admin/quotes', methods=['GET'])
@jwt_required()
def admin_get_quotes():
    from src.models.user import User
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or user.role != 'admin':
        return jsonify({
            'error': 'Admin access required',
            'code': 'FORBIDDEN'
        }), 403

    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        status = request.args.get('status')

        query = QuoteRequest.query

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(QuoteRequest.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'quote_requests': [qr.to_dict() for qr in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@quotes_bp.route('/admin/quotes/<int:quote_id>', methods=['PUT'])
@jwt_required()
def admin_update_quote(quote_id):
    from src.models.user import User
    from datetime import datetime

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or user.role != 'admin':
        return jsonify({
            'error': 'Admin access required',
            'code': 'FORBIDDEN'
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = QuoteRequestUpdate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    try:
        quote_request = QuoteRequest.query.get(quote_id)

        if not quote_request:
            return jsonify({
                'error': 'Quote request not found',
                'code': 'NOT_FOUND'
            }), 404

        if params.status is not None:
            quote_request.status = params.status
        if params.admin_notes is not None:
            quote_request.admin_notes = params.admin_notes
        if params.quoted_price is not None:
            quote_request.quoted_price = params.quoted_price
            quote_request.quoted_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Quote request updated',
            'quote_request': quote_request.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
