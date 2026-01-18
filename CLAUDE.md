# Construction Materials Search Platform

## Project Overview

A "Google Flights for construction materials" platform providing intelligent search, price comparison, supplier intelligence, and project management capabilities for construction professionals.

## Tech Stack

### Backend
- **Framework**: Flask 2.x with Blueprints
- **Database**: PostgreSQL 15 (via SQLAlchemy ORM)
- **Cache**: Redis 7 (flask-caching)
- **Task Queue**: Celery with Redis broker
- **Auth**: JWT (flask-jwt-extended)
- **Validation**: Pydantic 2.x

### Frontend
- **Framework**: React 18 with Vite
- **Routing**: react-router-dom v6
- **UI Components**: Radix UI / shadcn/ui
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker Compose
- **Services**: postgres, redis, backend, celery_worker, celery_beat, frontend

## Project Structure

```
pricing_project/
├── backend/materials_search_api/
│   └── src/
│       ├── main.py              # Flask app entry point
│       ├── config.py            # Environment configs
│       ├── cache.py             # Redis cache setup
│       ├── celery_app.py        # Celery configuration
│       ├── models/
│       │   ├── user.py          # User, db instance
│       │   ├── material.py      # Material, Supplier, PriceHistory, DataProvider, PriceSource, SyncJob
│       │   ├── comparison.py    # CanonicalMaterial, MaterialVariant
│       │   └── bom.py           # BillOfMaterials, BOMItem
│       ├── routes/
│       │   ├── materials.py     # Material CRUD & search
│       │   ├── comparison.py    # Price comparison
│       │   ├── user_features.py # Saved searches, favorites
│       │   ├── bom.py           # Bill of materials
│       │   ├── price_history.py # Historical prices
│       │   ├── supplier_review.py # Supplier reviews
│       │   └── data_integration.py # Provider management, sync jobs
│       ├── auth/
│       │   └── routes.py        # JWT auth endpoints
│       ├── integrations/
│       │   ├── base.py          # DataProviderAdapter ABC, MaterialPrice, SyncResult
│       │   ├── registry.py      # Provider registry singleton
│       │   ├── demo_provider.py # Demo data implementation
│       │   ├── rsmeans_provider.py # RSMeans API adapter (Tier 1)
│       │   ├── serpapi_provider.py # SerpApi adapter - Home Depot, Lowe's, Google Shopping (Tier 1)
│       │   └── scraper_provider.py # Playwright web scraper - Grainger, McMaster-Carr (Tier 3)
│       └── tasks/
│           └── sync_tasks.py    # Celery background tasks
├── frontend/materials_search_ui/
│   └── src/
│       ├── App.jsx              # Routes configuration
│       ├── pages/
│       │   ├── SearchPage.jsx   # Main search UI
│       │   ├── MaterialDetailPage.jsx
│       │   └── AdminPage.jsx    # Data provider management
│       ├── components/
│       │   ├── ui/              # Radix/shadcn components
│       │   ├── search/          # SearchBar, FilterPanel, SortSelect
│       │   ├── materials/       # MaterialCard, MaterialGrid, PriceHistoryChart
│       │   ├── auth/            # LoginForm, RegisterForm, AuthModal, AuthHeader
│       │   └── suppliers/       # ReviewForm, SupplierReviews
│       └── contexts/
│           ├── AuthContext.jsx  # JWT auth state
│           └── SearchContext.jsx # Search state management
└── docker-compose.yml
```

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - Login, returns JWT tokens
- `POST /logout` - Invalidate token
- `POST /refresh` - Refresh access token
- `GET /me` - Current user info

### Materials (`/api/v1`)
- `GET /materials` - Search with filters, pagination, sorting
- `GET /materials/<id>` - Material details
- `GET /materials/<id>/compare` - Price comparison across suppliers
- `GET /materials/<id>/price-history` - Historical prices

### Data Integration (`/api/v1`)
- `GET /providers` - List data providers
- `POST /providers` - Create provider (auth required)
- `PUT /providers/<id>` - Update provider (auth required)
- `DELETE /providers/<id>` - Delete provider (auth required)
- `POST /providers/<id>/sync` - Trigger sync job (auth required)
- `POST /providers/<id>/activate` - Activate provider (auth required)
- `POST /providers/<id>/deactivate` - Deactivate provider (auth required)
- `GET /sync-jobs` - List sync jobs with pagination
- `GET /price-sources` - List price sources

### User Features (`/api/v1`)
- `GET/POST /saved-searches` - Manage saved searches
- `GET/POST /favorites` - Manage favorites
- `GET/POST /bom` - Bill of materials management

## Data Provider System

### Three-Tier Data Strategy

| Tier | Source Type | Providers | Confidence |
|------|-------------|-----------|------------|
| **Tier 1** | Official APIs | RSMeans, SerpApi (Home Depot, Lowe's) | 0.85-0.95 |
| **Tier 2** | B2B Partnerships | Grainger, Ferguson (future) | 0.80-0.90 |
| **Tier 3** | Ethical Web Scraping | Playwright-based scrapers | 0.70-0.75 |

### Registered Provider Adapters

| Provider Key | Adapter Class | Type | Description |
|--------------|---------------|------|-------------|
| `demo` | `DemoProviderAdapter` | API | Demo data for testing |
| `rsmeans` | `RSMeansProviderAdapter` | API | RSMeans construction cost database |
| `serpapi` | `SerpApiProviderAdapter` | API | SerpApi general search |
| `home_depot` | `HomeDepotProviderAdapter` | API | Home Depot via SerpApi |
| `lowes` | `LowesProviderAdapter` | API | Lowe's via SerpApi |
| `playwright_scraper` | `PlaywrightScraperAdapter` | Scraper | Generic configurable scraper |
| `grainger` | `GraingerScraperAdapter` | Scraper | Grainger industrial supplies |
| `mcmaster` | `MCMasterScraperAdapter` | Scraper | McMaster-Carr industrial supplies |

### Provider Adapter Interface

All providers implement the `DataProviderAdapter` abstract base class:

```python
class DataProviderAdapter(ABC):
    @abstractmethod
    async def fetch_prices(self, category=None, search_query=None, limit=100) -> SyncResult

    @abstractmethod
    async def fetch_single_price(self, external_id: str) -> Optional[MaterialPrice]

    @abstractmethod
    async def search_materials(self, query: str, limit=20) -> List[MaterialPrice]

    @abstractmethod
    async def validate_connection(self) -> bool
```

### Adding a New Provider

1. Create adapter class in `backend/.../integrations/`:
   ```python
   from .base import APIProviderAdapter, MaterialPrice, SyncResult
   from .registry import provider_registry

   class MyProviderAdapter(APIProviderAdapter):
       def __init__(self, provider_config):
           if not provider_config.get('base_url'):
               provider_config['base_url'] = 'https://api.myprovider.com'
           super().__init__(provider_config)

       async def fetch_prices(self, category=None, search_query=None, limit=100) -> SyncResult:
           # Implementation
           pass

   provider_registry.register('my_provider', MyProviderAdapter)
   ```

2. Import in `integrations/__init__.py`:
   ```python
   from .my_provider import MyProviderAdapter
   ```

3. Add to `__all__` list

## Admin Panel

Access at `/admin` route after logging in. Accessible via user dropdown menu in header.

### Data Providers Tab
- View all configured providers in a table
- Columns: Name, Type, Status (Active/Inactive), Last Sync, Sync Interval, Actions
- Actions per provider:
  - **Activate/Deactivate**: Toggle provider status (inactive providers can't sync)
  - **Trigger Sync**: Start immediate sync job
  - **Edit**: Modify provider configuration
  - **Delete**: Remove provider (with confirmation dialog)
- **Add Provider** button opens dialog with fields:
  - Name (maps to provider_registry key)
  - Provider Type (api/scraper)
  - Base URL
  - API Key (optional, for API providers)
  - Sync Interval (e.g., "24h", "12h", "6h")
  - Active checkbox

### Sync Jobs Tab
- View job history table
- Columns: ID, Provider, Type (full/incremental), Status, Items Processed, Started, Completed
- Status indicators: pending, running, completed, failed
- **Refresh** button to update job list

## Docker Commands

```bash
# Build and start all services
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Check service status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Rebuild single service
docker-compose build backend && docker-compose up -d backend

# Rebuild multiple services
docker-compose build backend celery_worker celery_beat && docker-compose up -d
```

## Development

```bash
# Frontend dev server (hot reload)
cd frontend/materials_search_ui
npm run dev
# Access at http://localhost:5175

# Backend runs via Docker on port 5001
# Vite proxy configured to forward /api requests to backend
```

## Port Configuration

| Service | Internal | External |
|---------|----------|----------|
| Backend | 5000 | 5001 |
| Frontend (Docker) | 80 | 3002 |
| Frontend (Vite dev) | 5175 | 5175 |
| PostgreSQL | 5432 | 5460 |
| Redis | 6379 | 6390 |

## Celery Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `sync_provider` | On-demand | Sync prices from a data provider |
| `sync_volatile_materials` | Hourly | Sync volatile categories (Steel, Lumber) |
| `sync_full_catalog` | Daily at 2 AM | Full catalog sync from all providers |
| `cleanup_expired_prices` | Every 6 hours | Mark expired price sources as invalid |

## Implementation Status

### Completed
- [x] Phase 1: Foundation & Security (validation, rate limiting, API versioning)
- [x] Phase 2: Core Features (PostgreSQL, auth, price comparison)
- [x] Phase 3: Advanced Features (BOM, price history, reviews, caching)
- [x] Phase 4: Data Integration Infrastructure
  - [x] DataProvider, PriceSource, SyncJob models
  - [x] DataProviderAdapter abstract base class
  - [x] Provider registry for adapter lookup
  - [x] Celery tasks for background sync
  - [x] Admin panel UI (React)
  - [x] RSMeans API adapter (Tier 1)
  - [x] SerpApi adapter - Home Depot, Lowe's, Google Shopping (Tier 1)
  - [x] Playwright scraper adapter - Grainger, McMaster-Carr (Tier 3)

### Pending
- [ ] Phase 5: Performance (DB indexes, cursor pagination, connection pooling)
- [ ] Phase 5: Advanced search (synonyms, typo tolerance via pg_trgm, autocomplete)
- [ ] Phase 5: Notifications (price alerts, email notifications)
- [ ] Phase 5: Testing (pytest 80% coverage, Vitest, OpenAPI/Swagger docs)

## Key Files to Modify

| Task | Files |
|------|-------|
| Add new API endpoint | `backend/.../routes/`, `main.py` (register blueprint) |
| Add new model | `backend/.../models/`, `main.py` (import for table creation) |
| Add new page | `frontend/.../pages/`, `pages/index.js`, `App.jsx` |
| Add new component | `frontend/.../components/` |
| Add Celery task | `backend/.../tasks/sync_tasks.py`, `celery_app.py` (beat schedule) |
| Add data provider | Create adapter in `integrations/`, import in `__init__.py` |

## Environment Variables

```env
FLASK_ENV=development
DB_PASSWORD=materials_secret
JWT_SECRET_KEY=your-secret-key
POSTGRES_PORT=5460
REDIS_PORT=6390
BACKEND_PORT=5001
FRONTEND_PORT=3002
```

## Testing Provider Adapters

```bash
# Via API (after login)
curl -X POST http://localhost:5001/api/v1/providers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "demo", "provider_type": "api", "base_url": "http://demo", "sync_interval": "12h"}'

# Trigger sync
curl -X POST http://localhost:5001/api/v1/providers/1/sync \
  -H "Authorization: Bearer $TOKEN"

# Check sync jobs
curl http://localhost:5001/api/v1/sync-jobs

# Via Admin Panel
# 1. Login at http://localhost:5175
# 2. Click user dropdown -> Admin Panel
# 3. Use "Add Provider" button
# 4. Click sync icon on provider row
```

## Provider Configuration Examples

### RSMeans
```json
{
  "name": "rsmeans",
  "provider_type": "api",
  "base_url": "https://api.rsmeans.com/v1",
  "config": {
    "api_key": "your-api-key",
    "region_code": "US-OH",
    "data_year": "2024"
  }
}
```

### Home Depot (via SerpApi)
```json
{
  "name": "home_depot",
  "provider_type": "api",
  "base_url": "https://serpapi.com",
  "config": {
    "api_key": "your-serpapi-key",
    "zip_code": "45409"
  }
}
```

### Grainger (Web Scraper)
```json
{
  "name": "grainger",
  "provider_type": "scraper",
  "base_url": "https://www.grainger.com",
  "config": {
    "headless": true,
    "max_pages": 5,
    "delay_seconds": 2
  }
}
```
