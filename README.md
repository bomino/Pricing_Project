# Construction Materials Search Engine

A "Google Flights for construction materials" platform providing intelligent search, price comparison, supplier intelligence, and project management capabilities for construction professionals.

## Features

- **Intelligent Search**: Full-text search with filters by category, price, supplier, availability, and sustainability
- **Price Comparison**: Compare prices across multiple suppliers for the same material
- **Price History**: Track historical pricing trends with interactive charts
- **Bill of Materials**: Create and manage project material lists with cost calculations
- **Supplier Reviews**: Rate and review suppliers based on quality, delivery, and communication
- **Data Integration**: Multi-tier data sourcing from APIs, B2B partnerships, and web scraping
- **Admin Panel**: Manage data providers, trigger syncs, monitor job status

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

## Getting Started

### Prerequisites
- Docker Desktop installed and running ([download](https://www.docker.com/products/docker-desktop))

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd pricing_project
   ```

2. **Build and start all services**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3002
   - Backend API: http://localhost:5001
   - Admin Panel: http://localhost:3002/admin (requires login)

4. **Stop the application**
   ```bash
   docker-compose down
   ```

### Development Mode

For hot-reload during frontend development:

```bash
cd frontend/materials_search_ui
npm install
npm run dev
# Access at http://localhost:5175
```

The Vite dev server proxies `/api` requests to the backend container.

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
│       │   ├── user.py          # User model, db instance
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
│       │   ├── base.py          # DataProviderAdapter ABC
│       │   ├── registry.py      # Provider registry
│       │   ├── demo_provider.py # Demo data implementation
│       │   ├── rsmeans_provider.py # RSMeans API adapter
│       │   ├── serpapi_provider.py # SerpApi (Home Depot, Lowe's) adapter
│       │   └── scraper_provider.py # Playwright web scraper adapter
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
├── docker-compose.yml
├── CLAUDE.md                    # AI assistant guidelines
└── README.md                    # This file
```

## API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | User registration |
| POST | `/login` | Login, returns JWT tokens |
| POST | `/logout` | Invalidate token |
| POST | `/refresh` | Refresh access token |
| GET | `/me` | Current user info |

### Materials (`/api/v1`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/materials` | Search with filters, pagination, sorting |
| GET | `/materials/<id>` | Material details |
| GET | `/materials/<id>/compare` | Price comparison across suppliers |
| GET | `/materials/<id>/price-history` | Historical prices |

### Data Integration (`/api/v1`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/providers` | List all data providers |
| POST | `/providers` | Create provider (auth required) |
| PUT | `/providers/<id>` | Update provider (auth required) |
| DELETE | `/providers/<id>` | Delete provider (auth required) |
| POST | `/providers/<id>/sync` | Trigger sync job (auth required) |
| GET | `/sync-jobs` | List sync jobs with pagination |
| GET | `/price-sources` | List price sources |

### User Features (`/api/v1`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/saved-searches` | Manage saved searches |
| GET/POST | `/favorites` | Manage favorites |
| GET/POST | `/bom` | Bill of materials management |

## Data Provider System

### Three-Tier Data Strategy

| Tier | Source Type | Providers | Notes |
|------|-------------|-----------|-------|
| **Tier 1** | Official APIs | RSMeans, SerpApi (Home Depot, Lowe's) | High confidence, requires API keys |
| **Tier 2** | B2B Partnerships | Grainger, Ferguson, ABC Supply | Direct integrations (future) |
| **Tier 3** | Ethical Web Scraping | Playwright-based scrapers | robots.txt compliant, rate limited |

### Registered Provider Adapters

| Provider | Type | Description |
|----------|------|-------------|
| `demo` | API | Demo data for testing |
| `rsmeans` | API | RSMeans construction cost database |
| `serpapi` | API | SerpApi general search |
| `home_depot` | API | Home Depot via SerpApi |
| `lowes` | API | Lowe's via SerpApi |
| `playwright_scraper` | Scraper | Generic Playwright scraper |
| `grainger` | Scraper | Grainger industrial supplies |
| `mcmaster` | Scraper | McMaster-Carr industrial supplies |

### Adding a New Provider

1. Create adapter in `backend/.../integrations/`:
   ```python
   from .base import APIProviderAdapter
   from .registry import provider_registry

   class MyProviderAdapter(APIProviderAdapter):
       async def fetch_prices(self, category=None, search_query=None, limit=100):
           # Implementation
           pass

   provider_registry.register('my_provider', MyProviderAdapter)
   ```

2. Import in `integrations/__init__.py`

3. Create provider via Admin Panel or API:
   ```bash
   curl -X POST http://localhost:5001/api/v1/providers \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "my_provider", "provider_type": "api", "config": {"api_key": "xxx"}}'
   ```

## Admin Panel

Access at `/admin` after logging in. Features:

- **Data Providers Tab**
  - View all configured providers with status
  - Add new provider with type, base URL, API key, sync interval
  - Edit existing provider configuration
  - Activate/deactivate providers
  - Trigger manual sync
  - Delete providers (with confirmation)

- **Sync Jobs Tab**
  - View job history with status (pending, running, completed, failed)
  - See items processed count
  - Refresh job status

## Docker Commands

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Check service status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Rebuild single service
docker-compose build backend && docker-compose up -d backend

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

## Port Configuration

| Service | Internal | External |
|---------|----------|----------|
| Backend | 5000 | 5001 |
| Frontend (Docker) | 80 | 3002 |
| Frontend (Vite dev) | 5175 | 5175 |
| PostgreSQL | 5432 | 5460 |
| Redis | 6379 | 6390 |

## Celery Background Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `sync_provider` | On-demand | Sync prices from a specific provider |
| `sync_volatile_materials` | Every hour | Sync volatile categories (Steel, Lumber) |
| `sync_full_catalog` | Daily at 2 AM | Full catalog sync from all providers |
| `cleanup_expired_prices` | Every 6 hours | Mark expired price sources as invalid |

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

## Implementation Status

### Completed
- [x] Phase 1: Foundation & Security (validation, rate limiting, API versioning)
- [x] Phase 2: Core Features (PostgreSQL, auth, price comparison)
- [x] Phase 3: Advanced Features (BOM, price history, reviews, caching)
- [x] Phase 4: Data Integration (models, Celery, provider adapters, admin panel)

### Pending
- [ ] Phase 5: Performance optimizations (DB indexes, pagination, connection pooling)
- [ ] Phase 5: Advanced search (synonyms, typo tolerance, autocomplete)
- [ ] Phase 5: Notifications (price alerts, email notifications)
- [ ] Phase 5: Testing (pytest 80% coverage, Vitest, OpenAPI docs)

## Contributing

1. Create a feature branch from `main`
2. Make changes following existing code patterns
3. Test locally with `docker-compose up`
4. Submit a pull request

## License

Proprietary - All rights reserved.
