from datetime import datetime
from src.models.user import db


class BillOfMaterials(db.Model):
    __tablename__ = 'bills_of_materials'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('BOMItem', backref='bom', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref=db.backref('boms', lazy='dynamic'))
    project = db.relationship('Project', backref=db.backref('boms', lazy='dynamic'))

    @property
    def total_cost(self):
        return sum(item.line_total for item in self.items)

    @property
    def item_count(self):
        return self.items.count()

    def to_dict(self, include_items=False):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'total_cost': self.total_cost,
            'item_count': self.item_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            result['items'] = [item.to_dict() for item in self.items]
        return result


class BOMItem(db.Model):
    __tablename__ = 'bom_items'

    id = db.Column(db.Integer, primary_key=True)
    bom_id = db.Column(db.Integer, db.ForeignKey('bills_of_materials.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price_snapshot = db.Column(db.Float)
    notes = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    material = db.relationship('Material', backref=db.backref('bom_items', lazy='dynamic'))

    @property
    def line_total(self):
        return self.quantity * (self.unit_price_snapshot or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'bom_id': self.bom_id,
            'material_id': self.material_id,
            'quantity': self.quantity,
            'unit_price_snapshot': self.unit_price_snapshot,
            'line_total': self.line_total,
            'notes': self.notes,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'material': self.material.to_dict() if self.material else None
        }
