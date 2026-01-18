# Google Flights for Construction Materials - Implementation Plan

## Executive Summary

Transform the current MVP construction materials search engine into an enterprise-grade platform with intelligent search, price comparison, supplier intelligence, and project management capabilities.

| Attribute | Current State | Target State |
|-----------|---------------|--------------|
| Backend | Flask + SQLite, no auth | Flask + PostgreSQL + Redis, JWT auth |
| Frontend | Monolithic React, basic filters | Component-based, advanced UX |
| Search | ILIKE pattern matching | Full-text search with relevance |
| Data | 13 seed materials | Scalable to 100k+ materials |
| Users | None | Authenticated with roles |

**Timeline:** 20 weeks (5 phases)

---

## Phase 1: Foundation & Security (Weeks 1-3)

### Week 1: Quick Wins & Critical Security ✅ COMPLETED

#### Backend Security (CRITICAL) ✅

| Task | Library | Priority | Status |
|------|---------|----------|--------|
| Input validation | `pydantic>=2.0` | P0 | ✅ Done |
| Rate limiting | `flask-limiter>=3.0` | P0 | ✅ Done |
| API versioning | Native Flask blueprints | P0 | ✅ Done |
| Structured error handling | Native | P0 | ✅ Done |

**Implemented:**
- Created `src/schemas/` directory with Pydantic validation schemas:
  - `common.py` - PaginationParams, ErrorResponse, ValidationErrorDetail
  - `material.py` - MaterialSearchParams, MaterialCreate, MaterialSortBy, SortOrder enums
  - `supplier.py` - SupplierCreate, SupplierResponse
- Added Flask-Limiter with 60 req/min, 200 req/day limits
- API versioning at `/api/v1` prefix with legacy `/api` routes for backward compatibility
- Structured error handlers for validation, rate limiting, 404, and 500 errors
- Fixed N+1 queries with `joinedload(Material.supplier)`
- Added sorting support (`sort_by`, `sort_order` params)

#### Frontend Quick Wins ✅

| Task | Approach | Impact | Status |
|------|----------|--------|--------|
| Debounced search | `useDebounce` hook (300ms) | High UX improvement | ✅ Done |
| URL state sync | `react-router-dom` useSearchParams | Shareable links | ✅ Done |
| Active filter chips | Existing `Badge` component | Visual clarity | Pending |
| Sort dropdown | Existing `Select` component | Core functionality | ✅ Done |

**Implemented:**
- Created `src/hooks/useDebounce.js` - 300ms debounce for search input
- Added `BrowserRouter` wrapper in `main.jsx`
- URL state sync via `useSearchParams` - all filters persist in URL
- Sort dropdown with ascending/descending toggle
- Updated API calls to use `/api/v1` endpoint

### Week 2: State Management & Routing ✅ COMPLETED

**Component decomposition:** ✅
```
frontend/materials_search_ui/src/
├── pages/
│   ├── SearchPage.jsx         ✅ Created
│   ├── MaterialDetailPage.jsx ✅ Created
│   └── index.js               ✅ Created
├── components/
│   ├── search/
│   │   ├── SearchBar.jsx      ✅ Created
│   │   ├── FilterPanel.jsx    ✅ Created
│   │   ├── SortSelect.jsx     ✅ Created
│   │   └── index.js           ✅ Created
│   └── materials/
│       ├── MaterialCard.jsx   ✅ Created
│       ├── MaterialGrid.jsx   ✅ Created
│       └── index.js           ✅ Created
├── contexts/
│   └── SearchContext.jsx      ✅ Created
└── hooks/
    └── useDebounce.js         ✅ Created (Week 1)
```

**Routes:** ✅
```javascript
/              -> Redirect to /search     ✅
/search        -> SearchPage (filters in URL) ✅
/materials/:id -> MaterialDetailPage      ✅
```

**Implemented:**
- SearchContext with all search state and API logic
- SearchPage using decomposed components
- MaterialDetailPage with full material details view
- SearchBar, FilterPanel, SortSelect components
- MaterialCard, MaterialGrid components
- React Router routes with SearchProvider wrapping search route

### Week 3: Backend API Improvements ✅ COMPLETED

| Enhancement | Details | Status |
|-------------|---------|--------|
| Sorting | `sort_by` (name/price/lead_time), `sort_order` (asc/desc) | ✅ Done (Week 1) |
| N+1 fix | `joinedload(Material.supplier)` | ✅ Done (Week 1) |
| Filter metadata | `GET /api/v1/filters` returns options with counts | ✅ Done |
| Param fix | Standardize search param to `q` | ✅ Done (Week 1) |

**Implemented:**
- `GET /api/v1/filters` endpoint returning:
  - Categories with material counts
  - Subcategories grouped by category with counts
  - Suppliers with material counts
  - Availability options with counts
  - Sustainability ratings with counts
  - Price range (min/max)
- Subcategory and sustainability_rating filters already in search endpoint
- All error responses now include `code` field for consistency

---

## Phase 2: Core Features (Weeks 4-7)

### Week 4: Database Migration ✅ COMPLETED

**docker-compose.yml additions:** ✅
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: materials_db
      POSTGRES_USER: materials_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-materials_secret}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U materials_user -d materials_db"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Implemented:**
- PostgreSQL service added to docker-compose.yml with healthcheck
- Backend depends_on postgres with service_healthy condition
- DATABASE_URL environment variable for backend service
- Named volume `postgres_data` for data persistence
- Config module (`src/config.py`) with DevelopmentConfig, ProductionConfig, TestingConfig
- Flask-Migrate integrated in main.py
- TSVECTOR search_vector column added to Material model
- GIN index `ix_materials_search_vector` for full-text search
- Search service (`src/services/search.py`) with:
  - `update_search_vector()` - updates tsvector for a material
  - `search_materials_fulltext()` - performs ranked FTS with `ts_rank`
  - `rebuild_all_search_vectors()` - batch rebuild all vectors
  - Graceful fallback to ILIKE for SQLite

**Libraries:** `psycopg2-binary>=2.9`, `flask-migrate>=4.0` ✅

### Week 5: User Authentication ✅ COMPLETED

**Libraries:** `flask-jwt-extended>=4.6`, `argon2-cffi>=23.0` ✅

**Implemented:**
- Auth module created (`src/auth/`):
  - `__init__.py` - exports auth_bp, hash_password, verify_password
  - `routes.py` - /auth/register, /auth/login, /auth/refresh, /auth/me, /auth/logout
  - `utils.py` - Argon2 password hashing with needs_rehash support
- Auth schemas (`src/schemas/auth.py`):
  - RegisterRequest with username/password validation
  - LoginRequest with email validation
  - TokenResponse, UserResponse
- Enhanced User model:
  - password_hash, company_name, role, created_at fields
  - Relationships to SavedSearch and Favorite models
- SavedSearch model for saved filter states with alert_enabled
- Favorite model for material bookmarks with notes
- JWT configuration in main.py:
  - 1-hour access token expiry
  - 30-day refresh token expiry
  - JWT_SECRET_KEY from environment or fallback to SECRET_KEY
- Auth blueprint registered at /api/v1/auth/*

**API Endpoints:**
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| /auth/register | POST | No | Create new user account |
| /auth/login | POST | No | Get access + refresh tokens |
| /auth/refresh | POST | Refresh token | Get new access token |
| /auth/me | GET | Access token | Get current user profile |
| /auth/logout | POST | Access token | Logout (client-side token deletion) |

### Week 6: Price Comparison Matrix ✅ COMPLETED

**The "Google Flights" core feature - compare same material across suppliers:**

**Implemented:**
- `src/models/comparison.py`:
  - `CanonicalMaterial` - normalized material definitions with name, category, specs
  - `MaterialVariant` - supplier-specific pricing linked to canonical materials
- `src/services/comparison.py`:
  - `get_material_comparison()` - returns comparison data with price_range and best_value
  - `find_similar_materials()` - fallback for materials without canonical mapping
  - `determine_best_value()` - scoring algorithm (price, lead time, availability)
  - `create_canonical_material()`, `add_variant_to_canonical()`, `get_price_statistics()`
- `src/routes/comparison.py`:
  - `GET /materials/:id/compare` - compare prices for a material
  - `GET /canonical-materials` - list all canonical materials
  - `GET /canonical-materials/:id` - get canonical with variants and stats
  - `POST /canonical-materials` - create canonical (auth required)
  - `POST /canonical-materials/:id/variants` - add variant (auth required)
  - `GET /canonical-materials/:id/variants` - list variants with price stats
- `src/schemas/comparison.py`:
  - `CanonicalMaterialCreate`, `MaterialVariantCreate` - input validation
  - `MaterialComparisonResponse`, `PriceStatisticsResponse` - response models

**API Response format:**
```json
{
  "material": {"id": 1, "name": "High-Strength Concrete Mix", ...},
  "comparisons": [
    {"supplier": {...}, "price": 125.00, "lead_time_days": 3, "availability": "In Stock"},
    {"supplier": {...}, "price": 135.00, "lead_time_days": 1, "availability": "In Stock"}
  ],
  "price_range": {"min": 125.00, "max": 135.00, "avg": 130.00},
  "best_value": {"supplier_id": 1, "material_id": 1, "reason": "Lowest price, Available now"}
}
```

### Week 7: Saved Searches & Favorites ✅ COMPLETED

**Implemented:**
- `src/schemas/user_features.py`:
  - `SavedSearchCreate`, `SavedSearchUpdate` - input validation for saved searches
  - `FavoriteCreate`, `FavoriteUpdate` - input validation for favorites
- `src/routes/user_features.py`:
  - Full CRUD for saved searches (GET/POST/PUT/DELETE)
  - Full CRUD for favorites (GET/POST/PUT/DELETE)
  - Toggle favorite endpoint (`POST /materials/:id/favorite`)
  - All endpoints JWT-protected
- Models already created in Week 5 (SavedSearch, Favorite in `src/models/user.py`)
- Blueprint registered at `/api/v1` and `/api` (legacy)

**API Endpoints:**
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| /saved-searches | GET | Yes | List user's saved searches |
| /saved-searches | POST | Yes | Create saved search |
| /saved-searches/:id | GET | Yes | Get saved search by ID |
| /saved-searches/:id | PUT | Yes | Update saved search |
| /saved-searches/:id | DELETE | Yes | Delete saved search |
| /favorites | GET | Yes | List user's favorites with material data |
| /favorites | POST | Yes | Add material to favorites |
| /favorites/:id | GET | Yes | Get favorite by ID |
| /favorites/:id | PUT | Yes | Update favorite notes |
| /favorites/:id | DELETE | Yes | Remove from favorites |
| /materials/:id/favorite | POST | Yes | Toggle favorite status |

**Models (from Week 5):**
```python
class SavedSearch(db.Model):
    __tablename__ = 'saved_searches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    query_params = db.Column(db.JSON)  # Full filter state
    alert_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## Phase 3: Advanced Features (Weeks 8-12)

### Weeks 8-9: Bill of Materials (BOM) Generator ✅ COMPLETED

**Implemented:**
- `src/models/bom.py`:
  - `BillOfMaterials` - BOM with user/project association, status tracking, auto-calculated totals
  - `BOMItem` - Line items with material reference, quantity, price snapshot, sort order
- `src/services/bom.py`:
  - Full CRUD operations for BOMs and items
  - `duplicate_bom()` - Copy BOM with all items
  - `refresh_all_prices()` - Update all item prices from current material prices
  - `export_bom_to_csv()` - CSV export with totals
  - `get_bom_summary()` - Summary by category and supplier
  - `reorder_items()` - Drag-and-drop support
- `src/routes/bom.py`:
  - Full REST API for BOM and item management
  - Export endpoint with CSV download
  - Price refresh and summary endpoints
- `src/schemas/bom.py`:
  - `BOMCreate`, `BOMUpdate` - BOM validation
  - `BOMItemCreate`, `BOMItemUpdate` - Item validation
  - `BOMItemReorder`, `BOMDuplicate` - Special operations
- Blueprint registered at `/api/v1` and `/api` (legacy)

**API Endpoints:**
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| /boms | GET | Yes | List user's BOMs |
| /boms | POST | Yes | Create new BOM |
| /boms/:id | GET | Yes | Get BOM with items |
| /boms/:id | PUT | Yes | Update BOM |
| /boms/:id | DELETE | Yes | Delete BOM and items |
| /boms/:id/items | GET | Yes | List BOM items |
| /boms/:id/items | POST | Yes | Add item to BOM |
| /boms/:id/items/:itemId | GET | Yes | Get item details |
| /boms/:id/items/:itemId | PUT | Yes | Update item |
| /boms/:id/items/:itemId | DELETE | Yes | Remove item |
| /boms/:id/items/reorder | POST | Yes | Reorder items |
| /boms/:id/duplicate | POST | Yes | Duplicate BOM |
| /boms/:id/refresh-prices | POST | Yes | Refresh all prices |
| /boms/:id/summary | GET | Yes | Get cost summary |
| /boms/:id/export | GET | Yes | Export to CSV |

**Models:**
```python
class BillOfMaterials(db.Model):
    __tablename__ = 'bills_of_materials'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')  # draft, finalized, ordered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    items = db.relationship('BOMItem', backref='bom', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_cost(self):
        return sum(item.line_total for item in self.items)

class BOMItem(db.Model):
    __tablename__ = 'bom_items'

    id = db.Column(db.Integer, primary_key=True)
    bom_id = db.Column(db.Integer, db.ForeignKey('bills_of_materials.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price_snapshot = db.Column(db.Float)  # Price at time of adding
    notes = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)

    @property
    def line_total(self):
        return self.quantity * (self.unit_price_snapshot or 0)
```

**Frontend features (planned):**
- Drag-and-drop interface using `react-resizable-panels`
- Running total calculation
- Export to CSV/Excel (`xlsx` library)
- Print-friendly view

### Weeks 9-10: Price History & Tracking

```python
class PriceHistory(db.Model):
    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_price_history_lookup', 'material_id', 'supplier_id', 'recorded_at'),
    )
```

**API:** `GET /api/v1/materials/:id/price-history?period=30d`

**Response:**
```json
{
  "material_id": 1,
  "current_price": 125.00,
  "history": [
    {"date": "2024-01-01", "price": 120.00},
    {"date": "2024-01-15", "price": 122.50},
    {"date": "2024-02-01", "price": 125.00}
  ],
  "trend": "rising",
  "change_percent": 4.17,
  "volatility": "low"
}
```

**Frontend:** Line charts using `recharts` (already installed)

### Weeks 10-11: Supplier Reviews & Ratings

```python
class SupplierReview(db.Model):
    __tablename__ = 'supplier_reviews'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Overall rating
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    title = db.Column(db.String(200))
    content = db.Column(db.Text)

    # Dimension ratings
    quality_rating = db.Column(db.Integer)      # 1-5
    delivery_rating = db.Column(db.Integer)     # 1-5
    communication_rating = db.Column(db.Integer) # 1-5
    value_rating = db.Column(db.Integer)        # 1-5

    # Verification
    verified_purchase = db.Column(db.Boolean, default=False)
    order_id = db.Column(db.Integer)  # Link to order if verified

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('supplier_id', 'user_id', name='unique_user_supplier_review'),
    )
```

### Weeks 11-12: Caching Layer

**docker-compose.yml:**
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

**Flask caching setup:**
```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://redis:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Usage
@cache.cached(timeout=3600, key_prefix='categories')
def get_categories():
    return db.session.query(Material.category).distinct().all()

@cache.cached(timeout=300, query_string=True)
def search_materials():
    # Cached by full query string
    pass
```

**Cache targets:**
| Data | TTL | Invalidation |
|------|-----|--------------|
| Categories/filters | 1 hour | On material create/update |
| Search results | 5 min | Time-based |
| Material details | 15 min | On material update |
| Price history | 1 hour | On price update |
| Supplier ratings | 30 min | On new review |

---

## Phase 4: Data Integration (Weeks 13-16)

### Overview: Three-Tier Data Strategy

Transform the app from static seed data to a living platform with real-time pricing from multiple sources.

| Tier | Source Type | Implementation | Timeline |
|------|-------------|----------------|----------|
| **Tier 1** | Official APIs | 1build, RSMeans, Home Depot | Weeks 13-14 |
| **Tier 2** | B2B Partnerships | Grainger, Ferguson, ABC Supply | Ongoing |
| **Tier 3** | Ethical Web Scraping | Playwright + LLM extraction | Week 15-16 |

### Week 13: Data Provider Infrastructure

**New data models:**

```python
class DataProvider(db.Model):
    """External data source configuration"""
    __tablename__ = 'data_providers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # '1build', 'rsmeans', 'grainger'
    provider_type = db.Column(db.String(20))  # 'api', 'scrape', 'manual'
    api_base_url = db.Column(db.String(500))
    api_key_encrypted = db.Column(db.Text)  # Encrypted API key
    rate_limit_per_minute = db.Column(db.Integer, default=60)
    is_active = db.Column(db.Boolean, default=True)
    last_sync_at = db.Column(db.DateTime)
    sync_frequency_hours = db.Column(db.Integer, default=24)

class PriceSource(db.Model):
    """Price data from external sources"""
    __tablename__ = 'price_sources'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('data_providers.id'))
    external_id = db.Column(db.String(100))  # Provider's SKU/ID
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))
    region = db.Column(db.String(50))  # 'OH-045' (county FIPS)
    retrieved_at = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float, default=1.0)  # 1.0 for API, 0.8 for scrape
    raw_data = db.Column(db.JSON)  # Original response for audit

    __table_args__ = (
        db.Index('idx_price_source_lookup', 'material_id', 'provider_id', 'region'),
        db.Index('idx_price_source_freshness', 'retrieved_at'),
    )
```

**Provider adapter interface:**

```python
# backend/materials_search_api/src/providers/base.py
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class MaterialPrice:
    external_id: str
    name: str
    price: float
    unit: str
    category: str
    region: Optional[str] = None
    specifications: Optional[dict] = None

class DataProviderAdapter(ABC):
    """Base class for all data provider integrations"""

    @abstractmethod
    def search(self, query: str, category: Optional[str] = None) -> List[MaterialPrice]:
        """Search for materials by keyword"""
        pass

    @abstractmethod
    def get_price(self, external_id: str, region: Optional[str] = None) -> Optional[MaterialPrice]:
        """Get current price for specific item"""
        pass

    @abstractmethod
    def get_bulk_prices(self, external_ids: List[str]) -> List[MaterialPrice]:
        """Batch price lookup for efficiency"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify API connectivity"""
        pass
```

**New directory structure:**
```
backend/materials_search_api/src/
├── providers/
│   ├── __init__.py
│   ├── base.py              # DataProviderAdapter ABC
│   ├── onebuild.py          # 1build API integration
│   ├── rsmeans.py           # RSMeans API integration
│   ├── homedepot.py         # Home Depot via SerpApi
│   └── scraper.py           # Playwright + LLM scraper
├── services/
│   ├── data_sync.py         # Background sync orchestration
│   └── price_aggregator.py  # Multi-source price merging
```

### Week 14: Tier 1 API Integrations

**1build API (Primary - best coverage):**

```python
# backend/materials_search_api/src/providers/onebuild.py
import httpx
from .base import DataProviderAdapter, MaterialPrice

class OneBuildProvider(DataProviderAdapter):
    BASE_URL = "https://api.1build.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )

    def search(self, query: str, category: str = None) -> List[MaterialPrice]:
        params = {"q": query, "limit": 50}
        if category:
            params["category"] = category

        response = self.client.get("/materials/search", params=params)
        response.raise_for_status()

        return [
            MaterialPrice(
                external_id=item["sku"],
                name=item["name"],
                price=item["unit_price"],
                unit=item["unit"],
                category=item["category"],
                region=item.get("region_code"),
                specifications=item.get("specs")
            )
            for item in response.json()["items"]
        ]

    def get_price(self, external_id: str, region: str = None) -> MaterialPrice:
        params = {"region": region} if region else {}
        response = self.client.get(f"/materials/{external_id}/price", params=params)
        response.raise_for_status()
        data = response.json()

        return MaterialPrice(
            external_id=external_id,
            name=data["name"],
            price=data["current_price"],
            unit=data["unit"],
            category=data["category"],
            region=region
        )
```

**RSMeans API (Benchmark data):**

```python
# backend/materials_search_api/src/providers/rsmeans.py
class RSMeansProvider(DataProviderAdapter):
    BASE_URL = "https://api.rsmeans.com/v2"

    def search(self, query: str, category: str = None) -> List[MaterialPrice]:
        # RSMeans uses CSI MasterFormat codes
        response = self.client.get("/costs/search", params={
            "keyword": query,
            "location": "OH",  # Ohio region
            "year": 2024
        })
        # ... transform to MaterialPrice
```

**Home Depot via SerpApi (Retail pricing):**

```python
# backend/materials_search_api/src/providers/homedepot.py
class HomeDepotProvider(DataProviderAdapter):
    """Home Depot prices via SerpApi wrapper"""

    def __init__(self, serpapi_key: str):
        self.client = httpx.Client(
            base_url="https://serpapi.com",
            params={"api_key": serpapi_key, "engine": "home_depot"}
        )

    def search(self, query: str, category: str = None) -> List[MaterialPrice]:
        response = self.client.get("/search", params={"q": query})
        products = response.json().get("products", [])

        return [
            MaterialPrice(
                external_id=p["product_id"],
                name=p["title"],
                price=p["price"],
                unit="each",
                category=category or "General"
            )
            for p in products
        ]
```

### Week 15: Background Sync Service

**Celery task for scheduled syncing:**

```python
# backend/materials_search_api/src/services/data_sync.py
from celery import Celery
from datetime import datetime, timedelta

celery = Celery('materials_sync')

@celery.task
def sync_provider_prices(provider_id: int):
    """Sync all materials from a single provider"""
    provider = DataProvider.query.get(provider_id)
    if not provider or not provider.is_active:
        return

    adapter = get_adapter_for_provider(provider)

    # Get materials that need price updates
    stale_materials = Material.query.filter(
        Material.last_price_check < datetime.utcnow() - timedelta(hours=provider.sync_frequency_hours)
    ).all()

    for material in stale_materials:
        try:
            price_data = adapter.get_price(material.external_id, region="OH")
            if price_data:
                record_price_update(material, provider, price_data)
        except Exception as e:
            log_sync_error(provider, material, e)

    provider.last_sync_at = datetime.utcnow()
    db.session.commit()

@celery.task
def sync_volatile_materials():
    """Hourly sync for volatile commodities (lumber, steel, concrete)"""
    volatile_categories = ['Lumber', 'Steel', 'Concrete']

    materials = Material.query.filter(
        Material.category.in_(volatile_categories)
    ).all()

    for material in materials:
        sync_material_from_all_providers.delay(material.id)

# Celery beat schedule
celery.conf.beat_schedule = {
    'sync-volatile-hourly': {
        'task': 'services.data_sync.sync_volatile_materials',
        'schedule': 3600.0,  # Every hour
    },
    'sync-all-daily': {
        'task': 'services.data_sync.sync_all_providers',
        'schedule': 86400.0,  # Daily
    },
}
```

**docker-compose.yml additions:**
```yaml
services:
  celery-worker:
    build: ./backend/materials_search_api
    command: celery -A src.services.data_sync worker --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - redis
      - postgres

  celery-beat:
    build: ./backend/materials_search_api
    command: celery -A src.services.data_sync beat --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - redis
```

### Week 16: Tier 3 - Ethical Web Scraping (Fallback)

**Important: Scraping is a LAST RESORT. Always prefer in this order:**
1. Official API (always preferred)
2. Request API access / B2B partnership
3. Public RSS/XML feeds
4. Ethical scraping (only if above unavailable)

#### Legal & Compliance Guardrails

| Risk | Mitigation |
|------|------------|
| **Terms of Service** | Only scrape public pricing pages; avoid login-required content |
| **Copyright** | Transform data (don't mirror); store only facts (prices), not creative content |
| **CFAA concerns** | Never bypass authentication, CAPTCHAs, or rate limits |
| **GDPR/CCPA** | Don't collect personal data; only product/pricing info |

#### What to Scrape vs. Not Scrape

**DO scrape:**
- Public product catalog pages
- Published price lists
- Inventory availability indicators
- Product specifications

**DON'T scrape:**
- Login-protected dealer portals
- Sites with explicit "no scraping" in robots.txt
- Dynamic pricing that requires account context
- Any PII or business-sensitive data

#### Scraper Implementation

```python
# backend/materials_search_api/src/providers/scraper.py
from playwright.async_api import async_playwright
import anthropic
import json
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

# Identify as a bot (transparent)
USER_AGENT = "MaterialsSearchBot/1.0 (+https://yoursite.com/bot-info; contact@yoursite.com)"

class LLMAssistedScraper(DataProviderAdapter):
    """Scrape supplier websites using Playwright + Claude for extraction.

    IMPORTANT: This is a fallback for suppliers without APIs.
    Always attempt API integration first.
    """

    def __init__(self, anthropic_key: str):
        self.claude = anthropic.Anthropic(api_key=anthropic_key)
        self.rate_limiter = AdaptiveRateLimiter()
        self.robots_cache = {}  # Cache robots.txt results

    async def scrape_product_page(self, url: str) -> MaterialPrice:
        # Step 1: Check robots.txt compliance
        if not await self.is_allowed(url):
            raise PermissionError(f"Scraping not allowed by robots.txt: {url}")

        # Step 2: Check if we have cached data (24-72 hour cache)
        cached = await self.get_cached(url)
        if cached:
            return cached

        # Step 3: Scrape with ethical guardrails
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(user_agent=USER_AGENT)
            page = await context.new_page()

            try:
                await self.rate_limiter.wait()
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state('networkidle')
                html = await page.content()
                self.rate_limiter.record_success()
            except Exception as e:
                self.rate_limiter.record_error()
                raise
            finally:
                await browser.close()

        # Step 4: Extract with LLM and cache result
        result = self.extract_with_llm(html, url)
        await self.cache_result(url, result, ttl_hours=48)
        return result

    def extract_with_llm(self, html: str, source_url: str) -> MaterialPrice:
        prompt = f"""Extract product information from this HTML. Return JSON only.

HTML (truncated to 10000 chars):
{html[:10000]}

Extract these fields:
- name: Product name
- price: Numeric price (no currency symbol)
- unit: Unit of measure (each, per sqft, per lf, etc.)
- category: Material category
- specifications: Key specs as dict

Return ONLY valid JSON, no explanation."""

        response = self.claude.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        data = json.loads(response.content[0].text)
        return MaterialPrice(
            external_id=source_url,
            name=data["name"],
            price=float(data["price"]),
            unit=data["unit"],
            category=data["category"],
            specifications=data.get("specifications")
        )

    async def is_allowed(self, url: str) -> bool:
        """Check robots.txt compliance with caching"""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in self.robots_cache:
            robots_url = f"{domain}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
            except:
                # If can't read robots.txt, assume disallowed (conservative)
                return False
            self.robots_cache[domain] = rp

        return self.robots_cache[domain].can_fetch("MaterialsSearchBot", url)
```

#### Adaptive Rate Limiter with Exponential Backoff

```python
# backend/materials_search_api/src/providers/rate_limiter.py
import asyncio
from datetime import datetime, timedelta
from collections import deque

class AdaptiveRateLimiter:
    """Enforce ethical scraping with adaptive delays and exponential backoff"""

    def __init__(self):
        self.base_delay = 3.0  # Start conservative (3 seconds)
        self.max_delay = 60.0  # Cap at 1 minute
        self.consecutive_errors = 0
        self.requests = deque()
        self.requests_per_minute = 10

    async def wait(self):
        now = datetime.utcnow()

        # Remove requests older than 1 minute
        while self.requests and self.requests[0] < now - timedelta(minutes=1):
            self.requests.popleft()

        # Calculate delay with exponential backoff on errors
        delay = min(
            self.base_delay * (2 ** self.consecutive_errors),
            self.max_delay
        )

        # If at rate limit, wait for oldest request to expire
        if len(self.requests) >= self.requests_per_minute:
            wait_time = (self.requests[0] + timedelta(minutes=1) - now).total_seconds()
            delay = max(delay, wait_time)

        await asyncio.sleep(delay)
        self.requests.append(datetime.utcnow())

    def record_success(self):
        """Reset backoff on successful request"""
        self.consecutive_errors = 0

    def record_error(self):
        """Increase backoff on error (rate limit hit, timeout, etc.)"""
        self.consecutive_errors = min(self.consecutive_errors + 1, 5)  # Cap at 5
```

#### Scraping Configuration Model

```python
# backend/materials_search_api/src/models/scrape_config.py
class ScrapeConfig(db.Model):
    """Per-domain scraping configuration and compliance tracking"""
    __tablename__ = 'scrape_configs'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)

    # Compliance
    robots_txt_allows = db.Column(db.Boolean, default=None)  # None = not checked
    tos_reviewed = db.Column(db.Boolean, default=False)
    tos_allows_scraping = db.Column(db.Boolean, default=None)
    last_robots_check = db.Column(db.DateTime)

    # Rate limiting (per-domain)
    min_delay_seconds = db.Column(db.Float, default=3.0)
    max_requests_per_hour = db.Column(db.Integer, default=60)

    # Caching
    cache_ttl_hours = db.Column(db.Integer, default=48)

    # Status
    is_enabled = db.Column(db.Boolean, default=False)  # Must explicitly enable
    disabled_reason = db.Column(db.String(500))  # Why disabled (e.g., "ToS prohibits")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

#### Alternative Fallbacks (When Scraping Isn't Appropriate)

When a supplier blocks scraping or has restrictive ToS, provide graceful alternatives:

```python
class QuoteRequestFallback:
    """For suppliers where scraping isn't allowed"""

    async def get_price(self, material_id: str, supplier_domain: str) -> dict:
        return {
            "price": None,
            "availability": "unknown",
            "fallback_type": "quote_request",
            "message": "Contact supplier for current pricing",
            "quote_url": f"https://{supplier_domain}/quote-request",
            "phone": await self.get_supplier_phone(supplier_domain),
            "last_known_price": await self.get_historical_price(material_id),
            "last_known_date": await self.get_last_price_date(material_id)
        }
```

#### Crowdsourced Price Layer

```python
class UserSubmittedPrice(db.Model):
    """Allow users to submit/verify prices they receive from suppliers"""
    __tablename__ = 'user_submitted_prices'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))

    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))
    quote_date = db.Column(db.Date, nullable=False)
    region = db.Column(db.String(50))

    # Verification
    has_receipt = db.Column(db.Boolean, default=False)
    verified_by_others = db.Column(db.Integer, default=0)  # Other users confirming
    confidence_score = db.Column(db.Float, default=0.5)  # Starts at 0.5, increases with verification

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## Phase 5: Polish & Scale (Weeks 17-20)

### Week 17: Performance Optimization

**Database indexes:**
```python
# Add to models
__table_args__ = (
    db.Index('idx_material_category', 'category'),
    db.Index('idx_material_price', 'price'),
    db.Index('idx_material_availability', 'availability'),
    db.Index('idx_supplier_rating', 'rating'),
    db.Index('idx_supplier_location', 'city', 'state'),
)
```

**Frontend optimizations:**
- `React.memo` for MaterialCard
- Virtualized lists with `react-window` for large result sets
- Image lazy loading
- Route-based code splitting

### Week 18: Advanced Search

**PostgreSQL trigram extension for fuzzy matching:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_material_name_trgm ON materials USING gin (name gin_trgm_ops);
```

**Synonym support:**
```python
SYNONYMS = {
    'concrete': ['cement', 'concrete mix'],
    'drywall': ['gypsum board', 'sheetrock', 'plasterboard'],
    'lumber': ['wood', 'timber'],
}

def expand_search_terms(query):
    terms = query.lower().split()
    expanded = set(terms)
    for term in terms:
        if term in SYNONYMS:
            expanded.update(SYNONYMS[term])
    return ' | '.join(expanded)  # PostgreSQL OR syntax
```

### Week 19: Notifications & Alerts

```python
class PriceAlert(db.Model):
    __tablename__ = 'price_alerts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(10), nullable=False)  # 'below', 'above'
    is_active = db.Column(db.Boolean, default=True)
    triggered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # price_alert, stock_alert, review_response
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    data = db.Column(db.JSON)  # Additional context
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Week 20: Testing & Documentation

**Backend testing:**
```
pytest + pytest-flask
Factory Boy for test data
Coverage target: 80%
```

**Frontend testing:**
```
Vitest for unit tests
React Testing Library for component tests
Playwright for E2E (critical paths)
```

**API documentation:**
- Flask-RESTX or Flasgger for OpenAPI/Swagger
- Hosted at `/api/docs`

---

## Dependencies Summary

### Backend (requirements.txt additions)
```
# Validation & Security
pydantic>=2.0
flask-limiter>=3.0
flask-jwt-extended>=4.6
argon2-cffi>=23.0

# Database
psycopg2-binary>=2.9
flask-migrate>=4.0

# Caching
flask-caching>=2.1
redis>=5.0

# Data Integration (Phase 4)
httpx>=0.25.0              # Async HTTP client for APIs
celery>=5.3.0              # Background task queue
playwright>=1.40.0         # Browser automation for scraping
anthropic>=0.18.0          # Claude API for LLM extraction
cryptography>=41.0.0       # API key encryption

# Testing
pytest>=7.0
pytest-flask>=1.2
factory-boy>=3.3

# Documentation
flask-restx>=1.3
```

### Frontend (package.json additions)
```json
{
  "@tanstack/react-query": "^5.0.0",
  "react-window": "^1.8.10",
  "xlsx": "^0.18.5"
}
```

---

## Final Directory Structure

```
pricing_project/
├── backend/
│   └── materials_search_api/
│       └── src/
│           ├── auth/
│           │   ├── __init__.py
│           │   ├── routes.py
│           │   └── utils.py
│           ├── schemas/
│           │   ├── __init__.py
│           │   ├── material.py
│           │   ├── supplier.py
│           │   └── common.py
│           ├── providers/                    # NEW: Data integration (Phase 4)
│           │   ├── __init__.py
│           │   ├── base.py                   # DataProviderAdapter ABC
│           │   ├── onebuild.py               # 1build API
│           │   ├── rsmeans.py                # RSMeans API
│           │   ├── homedepot.py              # Home Depot via SerpApi
│           │   ├── scraper.py                # Playwright + LLM scraper
│           │   └── rate_limiter.py           # Ethical scraping controls
│           ├── services/
│           │   ├── __init__.py
│           │   ├── search.py
│           │   ├── comparison.py
│           │   ├── notifications.py
│           │   ├── data_sync.py              # NEW: Celery background sync
│           │   └── price_aggregator.py       # NEW: Multi-source merging
│           ├── models/
│           │   ├── __init__.py
│           │   ├── user.py
│           │   ├── material.py
│           │   ├── supplier.py
│           │   ├── price_history.py
│           │   ├── saved_search.py
│           │   ├── bom.py
│           │   ├── review.py
│           │   ├── data_provider.py          # NEW: Provider config
│           │   ├── price_source.py           # NEW: External price tracking
│           │   ├── scrape_config.py          # NEW: Per-domain scraping rules
│           │   └── user_submitted_price.py   # NEW: Crowdsourced prices
│           └── routes/
│               ├── __init__.py
│               ├── materials.py
│               ├── suppliers.py
│               ├── comparison.py
│               ├── bom.py
│               └── users.py
│
├── frontend/
│   └── materials_search_ui/
│       └── src/
│           ├── pages/
│           │   ├── SearchPage.jsx
│           │   ├── MaterialDetailPage.jsx
│           │   ├── ComparePage.jsx
│           │   ├── BOMPage.jsx
│           │   ├── SupplierPage.jsx
│           │   └── auth/
│           │       ├── LoginPage.jsx
│           │       └── RegisterPage.jsx
│           ├── components/
│           │   ├── search/
│           │   ├── materials/
│           │   ├── comparison/
│           │   ├── bom/
│           │   └── layout/
│           ├── contexts/
│           │   ├── AuthContext.jsx
│           │   ├── SearchContext.jsx
│           │   └── BOMContext.jsx
│           ├── hooks/
│           │   ├── useDebounce.js
│           │   ├── useSearch.js
│           │   └── useAuth.js
│           └── lib/
│               ├── api.js
│               └── utils.js
│
├── docs/
│   ├── IMPLEMENTATION_PLAN.md
│   ├── API.md
│   └── ARCHITECTURE.md
│
└── docker-compose.yml
```

---

## Verification Checklist

- [x] **Security:** Rate limiting blocks >60 req/min, input validation rejects malformed data ✅ (Phase 1 Week 1)
- [ ] **Search:** Full-text search returns relevant results ranked by relevance
- [ ] **Performance:** Search responds <200ms with 10k materials
- [ ] **Auth:** JWT flow works end-to-end (register → login → protected routes → refresh)
- [ ] **Comparison:** Same material shows all supplier variants with price analysis
- [ ] **BOM:** Create, edit, calculate totals, export to Excel
- [ ] **Docker:** `docker-compose up --build` starts postgres, redis, celery, backend, frontend
- [x] **Frontend:** Routes work, filters persist in URL, sort works, responsive on mobile ✅ (Phase 1 Week 1)
- [ ] **Data Integration:** API providers connect and sync, scraper respects robots.txt
- [ ] **Background Jobs:** Celery worker processes tasks, beat scheduler runs on schedule
- [ ] **Price Sources:** Multi-provider prices aggregate correctly with confidence scores
- [ ] **Scraping Compliance:** ScrapeConfig enforced, blocked domains return fallback responses
- [ ] **Crowdsourced Prices:** User submissions recorded, verification flow works

---

## Implementation Progress

| Phase | Week | Status | Completed Date |
|-------|------|--------|----------------|
| Phase 1 | Week 1 - Quick Wins & Security | ✅ Complete | 2026-01-17 |
| Phase 1 | Week 2 - State Management & Routing | ✅ Complete | 2026-01-17 |
| Phase 1 | Week 3 - Backend API Improvements | ✅ Complete | 2026-01-17 |
| Phase 2 | Week 4 - Database Migration | ✅ Complete | 2026-01-17 |
| Phase 2 | Week 5 - User Authentication | ✅ Complete | 2026-01-17 |
| Phase 2 | Week 6 - Price Comparison Matrix | ✅ Complete | 2026-01-17 |
| Phase 2 | Week 7 - Saved Searches & Favorites | ✅ Complete | 2026-01-17 |
| Phase 3 | Weeks 8-9 - BOM Generator | ✅ Complete | 2026-01-17 |
| Phase 3 | Weeks 9-10 - Price History & Tracking | ⏳ Not Started | - |
| Phase 3 | Weeks 10-11 - Supplier Reviews | ⏳ Not Started | - |
| Phase 3 | Weeks 11-12 - Caching Layer | ⏳ Not Started | - |
| Phase 4 | Weeks 13-16 - Data Integration | ⏳ Not Started | - |
| Phase 5 | Weeks 17-20 - Polish & Scale | ⏳ Not Started | - |
