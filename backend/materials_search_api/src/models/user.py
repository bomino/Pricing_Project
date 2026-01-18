from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    company_name = db.Column(db.String(200))
    role = db.Column(db.String(50), default='buyer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    saved_searches = db.relationship('SavedSearch', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'company_name': self.company_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SavedSearch(db.Model):
    __tablename__ = 'saved_searches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    query_params = db.Column(db.JSON)
    alert_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'query_params': self.query_params,
            'alert_enabled': self.alert_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'material_id': self.material_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
