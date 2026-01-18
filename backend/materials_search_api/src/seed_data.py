import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create a new Flask app instance for seeding
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy()
db.init_app(app)

# Define models directly here to avoid import issues
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

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create sample suppliers
        suppliers_data = [
            {
                'name': 'BuildMart Supply Co.',
                'description': 'Leading supplier of construction materials for commercial and residential projects',
                'contact_email': 'sales@buildmart.com',
                'contact_phone': '(555) 123-4567',
                'website': 'https://buildmart.com',
                'address': '123 Industrial Blvd',
                'city': 'Chicago',
                'state': 'IL',
                'zip_code': '60601',
                'service_areas': ['Illinois', 'Indiana', 'Wisconsin'],
                'certifications': ['ISO 9001', 'LEED Certified'],
                'rating': 4.5,
                'total_reviews': 150,
                'is_verified': True
            },
            {
                'name': 'Steel & Concrete Solutions',
                'description': 'Specialized in structural steel and concrete products',
                'contact_email': 'info@steelconcrete.com',
                'contact_phone': '(555) 987-6543',
                'website': 'https://steelconcrete.com',
                'address': '456 Steel Way',
                'city': 'Pittsburgh',
                'state': 'PA',
                'zip_code': '15201',
                'service_areas': ['Pennsylvania', 'Ohio', 'West Virginia'],
                'certifications': ['AISC Certified', 'ACI Certified'],
                'rating': 4.8,
                'total_reviews': 89,
                'is_verified': True
            },
            {
                'name': 'Green Building Materials',
                'description': 'Eco-friendly and sustainable construction materials',
                'contact_email': 'contact@greenbuild.com',
                'contact_phone': '(555) 456-7890',
                'website': 'https://greenbuild.com',
                'address': '789 Eco Drive',
                'city': 'Portland',
                'state': 'OR',
                'zip_code': '97201',
                'service_areas': ['Oregon', 'Washington', 'California'],
                'certifications': ['LEED Certified', 'FSC Certified', 'Energy Star'],
                'rating': 4.7,
                'total_reviews': 203,
                'is_verified': True
            },
            {
                'name': 'Roofing & Siding Specialists',
                'description': 'Complete roofing and exterior siding solutions',
                'contact_email': 'sales@roofingsiding.com',
                'contact_phone': '(555) 321-0987',
                'website': 'https://roofingsiding.com',
                'address': '321 Roof Lane',
                'city': 'Atlanta',
                'state': 'GA',
                'zip_code': '30301',
                'service_areas': ['Georgia', 'South Carolina', 'North Carolina'],
                'certifications': ['GAF Certified', 'CertainTeed Certified'],
                'rating': 4.3,
                'total_reviews': 76,
                'is_verified': True
            }
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            supplier = Supplier(**supplier_data)
            db.session.add(supplier)
            suppliers.append(supplier)
        
        db.session.commit()
        
        # Create sample materials
        materials_data = [
            # Concrete Materials
            {
                'name': 'High-Strength Concrete Mix',
                'description': 'Premium concrete mix designed for high-load applications with 4000 PSI strength',
                'category': 'Concrete',
                'subcategory': 'Ready Mix',
                'specifications': {
                    'strength': '4000 PSI',
                    'slump': '4-6 inches',
                    'aggregate_size': '3/4 inch',
                    'air_content': '6%'
                },
                'price': 125.00,
                'unit': 'per cubic yard',
                'supplier_id': 2,
                'availability': 'In Stock',
                'lead_time_days': 1,
                'minimum_order': 1.0,
                'certifications': ['ASTM C94', 'ACI 318'],
                'sustainability_rating': 'B',
                'image_url': 'https://example.com/concrete-mix.jpg'
            },
            {
                'name': 'Eco-Friendly Concrete',
                'description': 'Sustainable concrete mix with recycled aggregates and reduced carbon footprint',
                'category': 'Concrete',
                'subcategory': 'Green Mix',
                'specifications': {
                    'strength': '3500 PSI',
                    'recycled_content': '30%',
                    'carbon_reduction': '25%',
                    'slump': '3-5 inches'
                },
                'price': 140.00,
                'unit': 'per cubic yard',
                'supplier_id': 3,
                'availability': 'In Stock',
                'lead_time_days': 2,
                'minimum_order': 2.0,
                'certifications': ['LEED Certified', 'ASTM C94'],
                'sustainability_rating': 'A',
                'image_url': 'https://example.com/eco-concrete.jpg'
            },
            # Steel Materials
            {
                'name': 'Structural Steel I-Beam',
                'description': 'Wide flange steel beam for structural applications',
                'category': 'Steel',
                'subcategory': 'Structural',
                'specifications': {
                    'size': 'W12x26',
                    'length': '20 feet',
                    'grade': 'A992',
                    'yield_strength': '50 ksi'
                },
                'price': 285.00,
                'unit': 'per piece',
                'supplier_id': 2,
                'availability': 'In Stock',
                'lead_time_days': 3,
                'minimum_order': 1.0,
                'certifications': ['AISC Certified', 'ASTM A992'],
                'sustainability_rating': 'B',
                'image_url': 'https://example.com/steel-beam.jpg'
            },
            {
                'name': 'Reinforcement Rebar #5',
                'description': 'Grade 60 deformed steel reinforcement bar',
                'category': 'Steel',
                'subcategory': 'Reinforcement',
                'specifications': {
                    'size': '#5 (5/8 inch)',
                    'length': '20 feet',
                    'grade': '60',
                    'yield_strength': '60 ksi'
                },
                'price': 12.50,
                'unit': 'per piece',
                'supplier_id': 2,
                'availability': 'In Stock',
                'lead_time_days': 1,
                'minimum_order': 10.0,
                'certifications': ['ASTM A615'],
                'sustainability_rating': 'C',
                'image_url': 'https://example.com/rebar.jpg'
            },
            # Lumber Materials
            {
                'name': 'Pressure Treated Lumber 2x10',
                'description': 'Pressure treated dimensional lumber for outdoor construction',
                'category': 'Lumber',
                'subcategory': 'Treated',
                'specifications': {
                    'size': '2x10 inches',
                    'length': '12 feet',
                    'grade': 'Construction',
                    'treatment': 'ACQ'
                },
                'price': 28.75,
                'unit': 'per piece',
                'supplier_id': 3,
                'availability': 'In Stock',
                'lead_time_days': 0,
                'minimum_order': 1.0,
                'certifications': ['ALSC Certified'],
                'sustainability_rating': 'B',
                'image_url': 'https://example.com/treated-lumber.jpg'
            },
            {
                'name': 'FSC Certified Pine Lumber',
                'description': 'Sustainably sourced pine lumber with FSC certification',
                'category': 'Lumber',
                'subcategory': 'Sustainable',
                'specifications': {
                    'size': '2x8 inches',
                    'length': '16 feet',
                    'grade': 'Select Structural',
                    'species': 'Southern Pine'
                },
                'price': 32.50,
                'unit': 'per piece',
                'supplier_id': 3,
                'availability': 'In Stock',
                'lead_time_days': 1,
                'minimum_order': 1.0,
                'certifications': ['FSC Certified'],
                'sustainability_rating': 'A',
                'image_url': 'https://example.com/fsc-lumber.jpg'
            },
            # Roofing Materials
            {
                'name': 'Asphalt Shingles - Architectural',
                'description': 'High-quality architectural asphalt shingles with 30-year warranty',
                'category': 'Roofing',
                'subcategory': 'Shingles',
                'specifications': {
                    'style': 'Architectural',
                    'warranty': '30 years',
                    'wind_rating': '130 mph',
                    'fire_rating': 'Class A'
                },
                'price': 95.00,
                'unit': 'per square',
                'supplier_id': 4,
                'availability': 'In Stock',
                'lead_time_days': 2,
                'minimum_order': 1.0,
                'certifications': ['UL Listed'],
                'sustainability_rating': 'C',
                'image_url': 'https://example.com/asphalt-shingles.jpg'
            },
            {
                'name': 'Metal Roofing - Standing Seam',
                'description': 'Durable standing seam metal roofing with 50-year warranty',
                'category': 'Roofing',
                'subcategory': 'Metal',
                'specifications': {
                    'material': 'Galvalume Steel',
                    'gauge': '24 gauge',
                    'warranty': '50 years',
                    'wind_rating': '180 mph'
                },
                'price': 450.00,
                'unit': 'per square',
                'supplier_id': 4,
                'availability': 'In Stock',
                'lead_time_days': 5,
                'minimum_order': 1.0,
                'certifications': ['Energy Star', 'Cool Roof Rating'],
                'sustainability_rating': 'A',
                'image_url': 'https://example.com/metal-roofing.jpg'
            },
            # Insulation Materials
            {
                'name': 'Fiberglass Batt Insulation R-19',
                'description': 'Standard fiberglass batt insulation for wall applications',
                'category': 'Insulation',
                'subcategory': 'Fiberglass',
                'specifications': {
                    'r_value': 'R-19',
                    'thickness': '6.25 inches',
                    'width': '15 inches',
                    'length': '93 inches'
                },
                'price': 0.85,
                'unit': 'per square foot',
                'supplier_id': 1,
                'availability': 'In Stock',
                'lead_time_days': 0,
                'minimum_order': 100.0,
                'certifications': ['GREENGUARD Gold'],
                'sustainability_rating': 'B',
                'image_url': 'https://example.com/fiberglass-insulation.jpg'
            },
            {
                'name': 'Spray Foam Insulation',
                'description': 'High-performance closed-cell spray foam insulation',
                'category': 'Insulation',
                'subcategory': 'Spray Foam',
                'specifications': {
                    'r_value': 'R-6.5 per inch',
                    'type': 'Closed Cell',
                    'density': '2.0 lbs/ft³',
                    'coverage': '200 board feet'
                },
                'price': 1.75,
                'unit': 'per board foot',
                'supplier_id': 3,
                'availability': 'In Stock',
                'lead_time_days': 1,
                'minimum_order': 200.0,
                'certifications': ['Energy Star'],
                'sustainability_rating': 'A',
                'image_url': 'https://example.com/spray-foam.jpg'
            },
            # Drywall Materials
            {
                'name': 'Standard Drywall 1/2 inch',
                'description': 'Standard gypsum drywall for interior walls and ceilings',
                'category': 'Drywall',
                'subcategory': 'Standard',
                'specifications': {
                    'thickness': '1/2 inch',
                    'size': '4x8 feet',
                    'edge': 'Tapered',
                    'fire_rating': '1 hour'
                },
                'price': 12.50,
                'unit': 'per sheet',
                'supplier_id': 1,
                'availability': 'In Stock',
                'lead_time_days': 0,
                'minimum_order': 1.0,
                'certifications': ['ASTM C36'],
                'sustainability_rating': 'C',
                'image_url': 'https://example.com/drywall.jpg'
            }
        ]
        
        for material_data in materials_data:
            material = Material(**material_data)
            db.session.add(material)
        
        # Create a sample user
        user = User(
            username='demo_user',
            email='demo@example.com',
            password='password123'
        )
        db.session.add(user)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()

