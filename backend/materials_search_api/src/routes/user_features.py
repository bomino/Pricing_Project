from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from src.models.user import db, SavedSearch, Favorite
from src.models.material import Material
from src.schemas.user_features import (
    SavedSearchCreate,
    SavedSearchUpdate,
    FavoriteCreate,
    FavoriteUpdate
)

user_features_bp = Blueprint('user_features', __name__)


@user_features_bp.route('/saved-searches', methods=['GET'])
@jwt_required()
def get_saved_searches():
    user_id = int(get_jwt_identity())

    try:
        searches = SavedSearch.query.filter_by(user_id=user_id).order_by(
            SavedSearch.created_at.desc()
        ).all()

        return jsonify({
            'saved_searches': [s.to_dict() for s in searches],
            'total': len(searches)
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/saved-searches', methods=['POST'])
@jwt_required()
def create_saved_search():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = SavedSearchCreate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    try:
        saved_search = SavedSearch(
            user_id=user_id,
            name=params.name,
            query_params=params.query_params,
            alert_enabled=params.alert_enabled
        )

        db.session.add(saved_search)
        db.session.commit()

        return jsonify(saved_search.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/saved-searches/<int:search_id>', methods=['GET'])
@jwt_required()
def get_saved_search(search_id):
    user_id = int(get_jwt_identity())

    try:
        saved_search = SavedSearch.query.filter_by(
            id=search_id,
            user_id=user_id
        ).first()

        if not saved_search:
            return jsonify({
                'error': 'Saved search not found',
                'code': 'NOT_FOUND'
            }), 404

        return jsonify(saved_search.to_dict())

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/saved-searches/<int:search_id>', methods=['PUT'])
@jwt_required()
def update_saved_search(search_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = SavedSearchUpdate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    try:
        saved_search = SavedSearch.query.filter_by(
            id=search_id,
            user_id=user_id
        ).first()

        if not saved_search:
            return jsonify({
                'error': 'Saved search not found',
                'code': 'NOT_FOUND'
            }), 404

        if params.name is not None:
            saved_search.name = params.name
        if params.query_params is not None:
            saved_search.query_params = params.query_params
        if params.alert_enabled is not None:
            saved_search.alert_enabled = params.alert_enabled

        db.session.commit()

        return jsonify(saved_search.to_dict())

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/saved-searches/<int:search_id>', methods=['DELETE'])
@jwt_required()
def delete_saved_search(search_id):
    user_id = int(get_jwt_identity())

    try:
        saved_search = SavedSearch.query.filter_by(
            id=search_id,
            user_id=user_id
        ).first()

        if not saved_search:
            return jsonify({
                'error': 'Saved search not found',
                'code': 'NOT_FOUND'
            }), 404

        db.session.delete(saved_search)
        db.session.commit()

        return jsonify({'message': 'Saved search deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    user_id = int(get_jwt_identity())

    try:
        favorites = Favorite.query.filter_by(user_id=user_id).order_by(
            Favorite.created_at.desc()
        ).all()

        results = []
        for fav in favorites:
            fav_dict = fav.to_dict()
            material = Material.query.get(fav.material_id)
            if material:
                fav_dict['material'] = material.to_dict()
            results.append(fav_dict)

        return jsonify({
            'favorites': results,
            'total': len(results)
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/favorites', methods=['POST'])
@jwt_required()
def create_favorite():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = FavoriteCreate(**data)
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

    existing = Favorite.query.filter_by(
        user_id=user_id,
        material_id=params.material_id
    ).first()

    if existing:
        return jsonify({
            'error': 'Material already in favorites',
            'code': 'ALREADY_EXISTS'
        }), 409

    try:
        favorite = Favorite(
            user_id=user_id,
            material_id=params.material_id,
            notes=params.notes
        )

        db.session.add(favorite)
        db.session.commit()

        result = favorite.to_dict()
        result['material'] = material.to_dict()

        return jsonify(result), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/favorites/<int:favorite_id>', methods=['GET'])
@jwt_required()
def get_favorite(favorite_id):
    user_id = int(get_jwt_identity())

    try:
        favorite = Favorite.query.filter_by(
            id=favorite_id,
            user_id=user_id
        ).first()

        if not favorite:
            return jsonify({
                'error': 'Favorite not found',
                'code': 'NOT_FOUND'
            }), 404

        result = favorite.to_dict()
        material = Material.query.get(favorite.material_id)
        if material:
            result['material'] = material.to_dict()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/favorites/<int:favorite_id>', methods=['PUT'])
@jwt_required()
def update_favorite(favorite_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        params = FavoriteUpdate(**data)
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [{'loc': list(err['loc']), 'msg': err['msg'], 'type': err['type']} for err in e.errors()]
        }), 400

    try:
        favorite = Favorite.query.filter_by(
            id=favorite_id,
            user_id=user_id
        ).first()

        if not favorite:
            return jsonify({
                'error': 'Favorite not found',
                'code': 'NOT_FOUND'
            }), 404

        if params.notes is not None:
            favorite.notes = params.notes

        db.session.commit()

        result = favorite.to_dict()
        material = Material.query.get(favorite.material_id)
        if material:
            result['material'] = material.to_dict()

        return jsonify(result)

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/favorites/<int:favorite_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite(favorite_id):
    user_id = int(get_jwt_identity())

    try:
        favorite = Favorite.query.filter_by(
            id=favorite_id,
            user_id=user_id
        ).first()

        if not favorite:
            return jsonify({
                'error': 'Favorite not found',
                'code': 'NOT_FOUND'
            }), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'message': 'Favorite deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@user_features_bp.route('/materials/<int:material_id>/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite(material_id):
    user_id = int(get_jwt_identity())

    material = Material.query.get(material_id)
    if not material:
        return jsonify({
            'error': f'Material with ID {material_id} not found',
            'code': 'NOT_FOUND'
        }), 404

    try:
        existing = Favorite.query.filter_by(
            user_id=user_id,
            material_id=material_id
        ).first()

        if existing:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({'favorited': False, 'message': 'Removed from favorites'})
        else:
            favorite = Favorite(user_id=user_id, material_id=material_id)
            db.session.add(favorite)
            db.session.commit()
            return jsonify({'favorited': True, 'favorite_id': favorite.id, 'message': 'Added to favorites'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500
