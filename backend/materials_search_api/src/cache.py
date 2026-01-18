import os
from flask_caching import Cache

cache = Cache()

def init_cache(app):
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    cache_config = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': redis_url,
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_KEY_PREFIX': 'materials_'
    }

    app.config.from_mapping(cache_config)
    cache.init_app(app)

    return cache


CACHE_TIMEOUTS = {
    'categories': 3600,
    'filters': 3600,
    'search_results': 300,
    'material_detail': 900,
    'price_history': 900,
    'supplier_reviews': 600,
    'review_statistics': 600,
}


def make_cache_key(*args, **kwargs):
    from flask import request
    return f"{request.path}?{request.query_string.decode('utf-8')}"
