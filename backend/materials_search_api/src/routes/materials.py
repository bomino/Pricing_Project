from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_, asc, desc, func
from sqlalchemy.orm import joinedload
from pydantic import ValidationError
from src.models.user import db
from src.models.material import Material, Supplier, Project
from src.schemas.material import MaterialSearchParams, MaterialCreate, MaterialSortBy, SortOrder
from src.schemas.supplier import SupplierCreate
from src.services.price_history import record_price
from src.cache import cache, CACHE_TIMEOUTS, make_cache_key
import json

materials_bp = Blueprint('materials', __name__)


def validate_request_params(schema_class, params_dict):
    """Validate request parameters using Pydantic schema"""
    try:
        return schema_class(**params_dict), None
    except ValidationError as e:
        return None, {
            'error': 'Validation error',
            'code': 'VALIDATION_ERROR',
            'details': [
                {
                    'loc': list(err['loc']),
                    'msg': err['msg'],
                    'type': err['type']
                }
                for err in e.errors()
            ]
        }


@materials_bp.route('/materials/search', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['search_results'], make_cache_key=make_cache_key)
def search_materials():
    """Search materials with various filters"""
    params, error = validate_request_params(MaterialSearchParams, request.args.to_dict())
    if error:
        return jsonify(error), 400

    try:
        materials_query = Material.query.options(joinedload(Material.supplier))

        if params.q:
            materials_query = materials_query.filter(
                or_(
                    Material.name.ilike(f'%{params.q}%'),
                    Material.description.ilike(f'%{params.q}%')
                )
            )

        if params.category:
            materials_query = materials_query.filter(Material.category.ilike(f'%{params.category}%'))

        if params.subcategory:
            materials_query = materials_query.filter(Material.subcategory.ilike(f'%{params.subcategory}%'))

        if params.min_price is not None:
            materials_query = materials_query.filter(Material.price >= params.min_price)
        if params.max_price is not None:
            materials_query = materials_query.filter(Material.price <= params.max_price)

        if params.supplier_id:
            materials_query = materials_query.filter(Material.supplier_id == params.supplier_id)

        if params.availability:
            materials_query = materials_query.filter(Material.availability.ilike(f'%{params.availability}%'))

        if params.sustainability_rating:
            materials_query = materials_query.filter(
                Material.sustainability_rating == params.sustainability_rating.value
            )

        sort_column = getattr(Material, params.sort_by.value, Material.name)
        if params.sort_order == SortOrder.desc:
            materials_query = materials_query.order_by(desc(sort_column))
        else:
            materials_query = materials_query.order_by(asc(sort_column))

        materials = materials_query.paginate(
            page=params.page,
            per_page=params.per_page,
            error_out=False
        )

        return jsonify({
            'materials': [material.to_dict() for material in materials.items],
            'total': materials.total,
            'pages': materials.pages,
            'current_page': params.page,
            'per_page': params.per_page,
            'has_next': materials.has_next,
            'has_prev': materials.has_prev
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500

@materials_bp.route('/materials/<int:material_id>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['material_detail'])
def get_material(material_id):
    """Get a specific material by ID"""
    try:
        material = Material.query.options(joinedload(Material.supplier)).get_or_404(material_id)
        return jsonify(material.to_dict())
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@materials_bp.route('/materials', methods=['POST'])
def create_material():
    """Create a new material"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    params, error = validate_request_params(MaterialCreate, data)
    if error:
        return jsonify(error), 400

    try:
        supplier = Supplier.query.get(params.supplier_id)
        if not supplier:
            return jsonify({
                'error': f'Supplier with ID {params.supplier_id} not found',
                'code': 'NOT_FOUND'
            }), 404

        material = Material(
            name=params.name,
            description=params.description,
            category=params.category,
            subcategory=params.subcategory,
            specifications=params.specifications,
            price=params.price,
            unit=params.unit,
            supplier_id=params.supplier_id,
            availability=params.availability,
            lead_time_days=params.lead_time_days,
            minimum_order=params.minimum_order,
            certifications=params.certifications,
            sustainability_rating=params.sustainability_rating.value if params.sustainability_rating else None,
            image_url=params.image_url
        )

        db.session.add(material)
        db.session.commit()

        if params.price is not None:
            record_price(material.id, params.price, source='material_created')

        return jsonify(material.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@materials_bp.route('/materials/<int:material_id>', methods=['PUT'])
def update_material(material_id):
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found', 'code': 'NOT_FOUND'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    try:
        old_price = material.price

        if 'name' in data:
            material.name = data['name']
        if 'description' in data:
            material.description = data['description']
        if 'category' in data:
            material.category = data['category']
        if 'subcategory' in data:
            material.subcategory = data['subcategory']
        if 'specifications' in data:
            material.specifications = data['specifications']
        if 'price' in data:
            material.price = data['price']
        if 'unit' in data:
            material.unit = data['unit']
        if 'availability' in data:
            material.availability = data['availability']
        if 'lead_time_days' in data:
            material.lead_time_days = data['lead_time_days']
        if 'minimum_order' in data:
            material.minimum_order = data['minimum_order']
        if 'certifications' in data:
            material.certifications = data['certifications']
        if 'sustainability_rating' in data:
            material.sustainability_rating = data['sustainability_rating']
        if 'image_url' in data:
            material.image_url = data['image_url']

        db.session.commit()

        if 'price' in data and data['price'] != old_price and data['price'] is not None:
            record_price(material.id, data['price'], source='material_updated')

        return jsonify(material.to_dict())

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@materials_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get all suppliers"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        suppliers = Supplier.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'suppliers': [supplier.to_dict() for supplier in suppliers.items],
            'total': suppliers.total,
            'pages': suppliers.pages,
            'current_page': page,
            'per_page': per_page
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@materials_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    """Create a new supplier"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required', 'code': 'VALIDATION_ERROR'}), 400

    params, error = validate_request_params(SupplierCreate, data)
    if error:
        return jsonify(error), 400

    try:
        supplier = Supplier(
            name=params.name,
            description=params.description,
            contact_email=params.contact_email,
            contact_phone=params.contact_phone,
            website=params.website,
            address=params.address,
            city=params.city,
            state=params.state,
            zip_code=params.zip_code,
            country=params.country,
            service_areas=params.service_areas,
            certifications=params.certifications,
            is_verified=params.is_verified
        )

        db.session.add(supplier)
        db.session.commit()

        return jsonify(supplier.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500

@materials_bp.route('/categories', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['categories'])
def get_categories():
    """Get all material categories"""
    try:
        categories = db.session.query(Material.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]

        return jsonify({'categories': category_list})

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500

@materials_bp.route('/subcategories', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['categories'], make_cache_key=make_cache_key)
def get_subcategories():
    """Get subcategories for a specific category"""
    try:
        category = request.args.get('category')

        query = db.session.query(Material.subcategory).distinct()
        if category:
            query = query.filter(Material.category == category)

        subcategories = query.all()
        subcategory_list = [subcat[0] for subcat in subcategories if subcat[0]]

        return jsonify({'subcategories': subcategory_list})

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500


@materials_bp.route('/filters', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUTS['filters'])
def get_filters():
    """Get all filter options with counts for the search UI"""
    try:
        categories_query = db.session.query(
            Material.category,
            func.count(Material.id).label('count')
        ).filter(Material.category.isnot(None)).group_by(Material.category).all()

        categories = [
            {'name': cat, 'count': count}
            for cat, count in categories_query if cat
        ]

        subcategories_by_category = {}
        subcategories_query = db.session.query(
            Material.category,
            Material.subcategory,
            func.count(Material.id).label('count')
        ).filter(
            Material.category.isnot(None),
            Material.subcategory.isnot(None)
        ).group_by(Material.category, Material.subcategory).all()

        for cat, subcat, count in subcategories_query:
            if cat and subcat:
                if cat not in subcategories_by_category:
                    subcategories_by_category[cat] = []
                subcategories_by_category[cat].append({'name': subcat, 'count': count})

        suppliers_query = db.session.query(
            Supplier.id,
            Supplier.name,
            func.count(Material.id).label('count')
        ).join(Material, Material.supplier_id == Supplier.id).group_by(
            Supplier.id, Supplier.name
        ).all()

        suppliers = [
            {'id': sid, 'name': name, 'count': count}
            for sid, name, count in suppliers_query if name
        ]

        availability_query = db.session.query(
            Material.availability,
            func.count(Material.id).label('count')
        ).filter(Material.availability.isnot(None)).group_by(Material.availability).all()

        availability_options = [
            {'name': avail, 'count': count}
            for avail, count in availability_query if avail
        ]

        sustainability_query = db.session.query(
            Material.sustainability_rating,
            func.count(Material.id).label('count')
        ).filter(Material.sustainability_rating.isnot(None)).group_by(
            Material.sustainability_rating
        ).all()

        sustainability_ratings = [
            {'rating': rating, 'count': count}
            for rating, count in sustainability_query if rating
        ]

        price_range = db.session.query(
            func.min(Material.price).label('min'),
            func.max(Material.price).label('max')
        ).first()

        return jsonify({
            'categories': categories,
            'subcategories': subcategories_by_category,
            'suppliers': suppliers,
            'availability_options': availability_options,
            'sustainability_ratings': sustainability_ratings,
            'price_range': {
                'min': float(price_range.min) if price_range.min else 0,
                'max': float(price_range.max) if price_range.max else 0
            }
        })

    except Exception as e:
        return jsonify({'error': str(e), 'code': 'INTERNAL_ERROR'}), 500

@materials_bp.route('/materials/recommendations', methods=['GET'])
def get_recommendations():
    """Get material recommendations based on project type or similar materials"""
    try:
        material_id = request.args.get('material_id', type=int)
        project_type = request.args.get('project_type')
        category = request.args.get('category')
        limit = request.args.get('limit', 10, type=int)
        
        if material_id:
            # Get recommendations based on similar materials
            base_material = Material.query.get_or_404(material_id)
            recommendations = Material.query.filter(
                and_(
                    Material.category == base_material.category,
                    Material.id != material_id
                )
            ).limit(limit).all()
        elif category:
            # Get popular materials in category
            recommendations = Material.query.filter(
                Material.category == category
            ).limit(limit).all()
        else:
            # Get general recommendations
            recommendations = Material.query.limit(limit).all()
        
        return jsonify({
            'recommendations': [material.to_dict() for material in recommendations]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@materials_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get user projects"""
    try:
        user_id = request.args.get('user_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Project.query
        if user_id:
            query = query.filter(Project.user_id == user_id)
        
        projects = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'projects': [project.to_dict() for project in projects.items],
            'total': projects.total,
            'pages': projects.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@materials_bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        project = Project(
            name=data.get('name'),
            description=data.get('description'),
            project_type=data.get('project_type'),
            location=data.get('location'),
            budget=data.get('budget'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            status=data.get('status', 'Planning'),
            user_id=data.get('user_id')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify(project.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

