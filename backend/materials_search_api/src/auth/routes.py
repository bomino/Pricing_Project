from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from pydantic import ValidationError
from src.models.user import db, User
from src.auth.utils import hash_password, verify_password, needs_rehash
from src.schemas.auth import RegisterRequest, LoginRequest

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = RegisterRequest(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    if User.query.filter_by(email=params.email).first():
        return jsonify({'error': 'Email already registered', 'code': 'EMAIL_EXISTS'}), 409

    if User.query.filter_by(username=params.username).first():
        return jsonify({'error': 'Username already taken', 'code': 'USERNAME_EXISTS'}), 409

    user = User(
        username=params.username,
        email=params.email,
        password_hash=hash_password(params.password),
        company_name=params.company_name,
        role=params.role
    )

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = LoginRequest(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    user = User.query.filter_by(email=params.email).first()

    if not user or not verify_password(user.password_hash, params.password):
        return jsonify({'error': 'Invalid email or password', 'code': 'INVALID_CREDENTIALS'}), 401

    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(params.password)
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token})


@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found', 'code': 'NOT_FOUND'}), 404

    return jsonify({'user': user.to_dict()})


@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Successfully logged out'})
