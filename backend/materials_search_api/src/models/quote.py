from datetime import datetime
from src.models.user import db
from sqlalchemy import Index


class QuoteRequest(db.Model):
    __tablename__ = 'quote_requests'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    contact_name = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(200), nullable=False)
    contact_phone = db.Column(db.String(50))
    company_name = db.Column(db.String(200))

    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))
    notes = db.Column(db.Text)
    preferred_contact_method = db.Column(db.String(50), default='email')

    status = db.Column(db.String(50), default='pending')
    admin_notes = db.Column(db.Text)
    quoted_price = db.Column(db.Float)
    quoted_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    material = db.relationship('Material', backref=db.backref('quote_requests', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('quote_requests', lazy='dynamic'))

    __table_args__ = (
        Index('ix_quote_requests_material', 'material_id'),
        Index('ix_quote_requests_user', 'user_id'),
        Index('ix_quote_requests_status', 'status'),
        Index('ix_quote_requests_created', 'created_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'material_name': self.material.name if self.material else None,
            'user_id': self.user_id,
            'contact_name': self.contact_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'company_name': self.company_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes,
            'preferred_contact_method': self.preferred_contact_method,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'quoted_price': self.quoted_price,
            'quoted_at': self.quoted_at.isoformat() if self.quoted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
