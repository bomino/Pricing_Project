import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import timedelta
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from pydantic import ValidationError
from src.models.user import db
from src.models.material import Material, Supplier, Project, PriceHistory, SupplierReview, DataProvider, PriceSource, SyncJob
from src.models.comparison import CanonicalMaterial, MaterialVariant
from src.models.bom import BillOfMaterials, BOMItem
from src.routes.user import user_bp
from src.routes.materials import materials_bp
from src.routes.comparison import comparison_bp
from src.routes.user_features import user_features_bp
from src.routes.bom import bom_bp
from src.routes.price_history import price_history_bp
from src.routes.supplier_review import supplier_review_bp
from src.routes.data_integration import data_integration_bp
from src.auth.routes import auth_bp
from src.config import config
from src.cache import init_cache

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

jwt = JWTManager(app)
migrate = Migrate(app, db)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per minute"],
    storage_uri="memory://",
)

CORS(app)

init_cache(app)

app.register_blueprint(user_bp, url_prefix='/api/v1')
app.register_blueprint(materials_bp, url_prefix='/api/v1')
app.register_blueprint(auth_bp, url_prefix='/api/v1')
app.register_blueprint(comparison_bp, url_prefix='/api/v1')
app.register_blueprint(user_features_bp, url_prefix='/api/v1')
app.register_blueprint(bom_bp, url_prefix='/api/v1')
app.register_blueprint(price_history_bp, url_prefix='/api/v1')
app.register_blueprint(supplier_review_bp, url_prefix='/api/v1')
app.register_blueprint(data_integration_bp, url_prefix='/api/v1')

app.register_blueprint(user_bp, url_prefix='/api', name='user_legacy')
app.register_blueprint(materials_bp, url_prefix='/api', name='materials_legacy')
app.register_blueprint(auth_bp, url_prefix='/api', name='auth_legacy')
app.register_blueprint(comparison_bp, url_prefix='/api', name='comparison_legacy')
app.register_blueprint(user_features_bp, url_prefix='/api', name='user_features_legacy')
app.register_blueprint(bom_bp, url_prefix='/api', name='bom_legacy')
app.register_blueprint(price_history_bp, url_prefix='/api', name='price_history_legacy')
app.register_blueprint(supplier_review_bp, url_prefix='/api', name='supplier_review_legacy')
app.register_blueprint(data_integration_bp, url_prefix='/api', name='data_integration_legacy')

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


# Error handlers
@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({
        'error': 'Validation error',
        'code': 'VALIDATION_ERROR',
        'details': [
            {
                'loc': list(err['loc']),
                'msg': err['msg'],
                'type': err['type']
            }
            for err in error.errors()
        ]
    }), 400


@app.errorhandler(429)
def handle_rate_limit_error(error):
    return jsonify({
        'error': 'Rate limit exceeded',
        'code': 'RATE_LIMIT_EXCEEDED',
        'details': str(error.description)
    }), 429


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({
        'error': 'Resource not found',
        'code': 'NOT_FOUND'
    }), 404


@app.errorhandler(500)
def handle_internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
