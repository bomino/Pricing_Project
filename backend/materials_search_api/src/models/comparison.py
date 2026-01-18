from src.models.user import db
from datetime import datetime


class CanonicalMaterial(db.Model):
    __tablename__ = 'canonical_materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    specifications = db.Column(db.JSON)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    variants = db.relationship('MaterialVariant', backref='canonical', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'specifications': self.specifications,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'variant_count': self.variants.count()
        }


class MaterialVariant(db.Model):
    __tablename__ = 'material_variants'

    id = db.Column(db.Integer, primary_key=True)
    canonical_material_id = db.Column(db.Integer, db.ForeignKey('canonical_materials.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))
    lead_time_days = db.Column(db.Integer)
    availability = db.Column(db.String(50))
    minimum_order = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', backref=db.backref('variants', lazy='dynamic'))
    material = db.relationship('Material', backref=db.backref('variant', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'canonical_material_id': self.canonical_material_id,
            'supplier_id': self.supplier_id,
            'supplier': self.supplier.to_dict() if self.supplier else None,
            'material_id': self.material_id,
            'price': self.price,
            'unit': self.unit,
            'lead_time_days': self.lead_time_days,
            'availability': self.availability,
            'minimum_order': self.minimum_order,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
