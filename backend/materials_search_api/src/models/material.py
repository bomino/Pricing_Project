import os
from src.models.user import db
from sqlalchemy import Index
from datetime import datetime

is_postgres = 'postgresql' in os.environ.get('DATABASE_URL', '')

if is_postgres:
    from sqlalchemy.dialects.postgresql import TSVECTOR


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    specifications = db.Column(db.JSON)
    price = db.Column(db.Float)
    unit = db.Column(db.String(50))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    availability = db.Column(db.String(50), default='In Stock')
    lead_time_days = db.Column(db.Integer, default=0)
    minimum_order = db.Column(db.Float)
    certifications = db.Column(db.JSON)
    sustainability_rating = db.Column(db.String(10))
    image_url = db.Column(db.String(500))

    supplier = db.relationship('Supplier', backref=db.backref('materials', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'specifications': self.specifications,
            'price': self.price,
            'unit': self.unit,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'availability': self.availability,
            'lead_time_days': self.lead_time_days,
            'minimum_order': self.minimum_order,
            'certifications': self.certifications,
            'sustainability_rating': self.sustainability_rating,
            'image_url': self.image_url
        }


if is_postgres:
    Material.search_vector = db.Column(TSVECTOR)
    Material.__table_args__ = (
        Index('ix_materials_search_vector', 'search_vector', postgresql_using='gin'),
        Index('ix_materials_category', 'category'),
        Index('ix_materials_price', 'price'),
        Index('ix_materials_availability', 'availability'),
        Index('ix_materials_supplier', 'supplier_id'),
        Index('ix_materials_category_price', 'category', 'price'),
        Index('ix_materials_name', 'name'),
    )
else:
    Material.__table_args__ = (
        Index('ix_materials_category', 'category'),
        Index('ix_materials_price', 'price'),
        Index('ix_materials_availability', 'availability'),
        Index('ix_materials_supplier', 'supplier_id'),
    )


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(50), default='USA')
    service_areas = db.Column(db.JSON)
    certifications = db.Column(db.JSON)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)

    __table_args__ = (
        Index('ix_suppliers_rating', 'rating'),
        Index('ix_suppliers_location', 'city', 'state'),
        Index('ix_suppliers_name', 'name'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'website': self.website,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'service_areas': self.service_areas,
            'certifications': self.certifications,
            'rating': self.rating,
            'total_reviews': self.total_reviews,
            'is_verified': self.is_verified
        }

class PriceHistory(db.Model):
    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source = db.Column(db.String(50), default='system')

    material = db.relationship('Material', backref=db.backref('price_history', lazy='dynamic'))

    __table_args__ = (
        Index('ix_price_history_material_recorded', 'material_id', 'recorded_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'price': self.price,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'source': self.source
        }


class SupplierReview(db.Model):
    __tablename__ = 'supplier_reviews'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    quality_rating = db.Column(db.Integer)
    delivery_rating = db.Column(db.Integer)
    communication_rating = db.Column(db.Integer)
    verified_purchase = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', backref=db.backref('reviews', lazy='dynamic'))

    __table_args__ = (
        Index('ix_supplier_reviews_supplier', 'supplier_id'),
        Index('ix_supplier_reviews_user', 'user_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'quality_rating': self.quality_rating,
            'delivery_rating': self.delivery_rating,
            'communication_rating': self.communication_rating,
            'verified_purchase': self.verified_purchase,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(100))  # e.g., 'Residential', 'Commercial', 'Industrial'
    location = db.Column(db.String(200))
    budget = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='Planning')
    user_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type,
            'location': self.location,
            'budget': self.budget,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'user_id': self.user_id
        }


class DataProvider(db.Model):
    __tablename__ = 'data_providers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    provider_type = db.Column(db.String(50), nullable=False)  # 'api', 'scraper', 'b2b'
    base_url = db.Column(db.String(500))
    api_key_encrypted = db.Column(db.Text)
    config = db.Column(db.JSON, default={})
    is_active = db.Column(db.Boolean, default=True)
    rate_limit_requests = db.Column(db.Integer, default=100)
    rate_limit_period = db.Column(db.Integer, default=3600)
    last_sync_at = db.Column(db.DateTime)
    sync_interval_hours = db.Column(db.Integer, default=24)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    price_sources = db.relationship('PriceSource', backref='provider', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'provider_type': self.provider_type,
            'base_url': self.base_url,
            'is_active': self.is_active,
            'rate_limit_requests': self.rate_limit_requests,
            'rate_limit_period': self.rate_limit_period,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'sync_interval_hours': self.sync_interval_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PriceSource(db.Model):
    __tablename__ = 'price_sources'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('data_providers.id'), nullable=False)
    external_id = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))
    currency = db.Column(db.String(10), default='USD')
    confidence_score = db.Column(db.Float, default=1.0)
    source_url = db.Column(db.String(500))
    raw_data = db.Column(db.JSON)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime)
    is_valid = db.Column(db.Boolean, default=True)

    material = db.relationship('Material', backref=db.backref('price_sources', lazy='dynamic'))

    __table_args__ = (
        Index('ix_price_sources_material_provider', 'material_id', 'provider_id'),
        Index('ix_price_sources_fetched', 'fetched_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'provider_id': self.provider_id,
            'provider_name': self.provider.name if self.provider else None,
            'external_id': self.external_id,
            'price': self.price,
            'unit': self.unit,
            'currency': self.currency,
            'confidence_score': self.confidence_score,
            'source_url': self.source_url,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_valid': self.is_valid
        }


class SyncJob(db.Model):
    __tablename__ = 'sync_jobs'

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('data_providers.id'), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)  # 'full', 'incremental', 'single'
    status = db.Column(db.String(50), default='pending')  # 'pending', 'running', 'completed', 'failed'
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    items_processed = db.Column(db.Integer, default=0)
    items_failed = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    provider = db.relationship('DataProvider', backref=db.backref('sync_jobs', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'provider_name': self.provider.name if self.provider else None,
            'job_type': self.job_type,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'items_processed': self.items_processed,
            'items_failed': self.items_failed,
            'error_message': self.error_message
        }

