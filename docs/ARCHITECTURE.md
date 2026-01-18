# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  FRONTEND                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         React 19 + Vite                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │  Search  │ │ Compare  │ │   BOM    │ │ Supplier │ │   Auth   │  │   │
│  │  │   Page   │ │   Page   │ │   Page   │ │   Page   │ │  Pages   │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Shared Components                          │   │   │
│  │  │  SearchBar │ FilterPanel │ MaterialCard │ ComparisonTable    │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                      State Management                         │   │   │
│  │  │  SearchContext │ AuthContext │ BOMContext │ React Query      │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ HTTP/REST                              │
│                                    ▼                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                  BACKEND                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Flask Application                            │   │
│  │                                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │   │
│  │  │    Auth    │  │  Materials │  │ Comparison │  │    BOM     │   │   │
│  │  │   Routes   │  │   Routes   │  │   Routes   │  │   Routes   │   │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                      Middleware Layer                         │   │   │
│  │  │  JWT Auth │ Rate Limiting │ Validation │ Error Handling      │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                      Service Layer                            │   │   │
│  │  │  SearchService │ ComparisonService │ NotificationService     │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                       Data Layer                              │   │   │
│  │  │  SQLAlchemy Models │ Pydantic Schemas │ Database Migrations  │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                          │                    │                             │
│                          ▼                    ▼                             │
│              ┌──────────────────┐  ┌──────────────────┐                    │
│              │    PostgreSQL    │  │      Redis       │                    │
│              │   (Primary DB)   │  │    (Cache)       │                    │
│              │                  │  │                  │                    │
│              │ • Materials      │  │ • Search cache   │                    │
│              │ • Suppliers      │  │ • Rate limits    │                    │
│              │ • Users          │  │ • Sessions       │                    │
│              │ • Reviews        │  │ • Filter cache   │                    │
│              │ • Price History  │  │                  │                    │
│              │ • BOMs           │  │                  │                    │
│              └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORE ENTITIES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐         ┌─────────────────┐                           │
│  │    Supplier     │ 1     n │    Material     │                           │
│  ├─────────────────┤─────────┤─────────────────┤                           │
│  │ id              │         │ id              │                           │
│  │ name            │         │ name            │                           │
│  │ description     │         │ description     │                           │
│  │ contact_email   │         │ category        │                           │
│  │ contact_phone   │         │ subcategory     │                           │
│  │ website         │         │ specifications  │                           │
│  │ address         │         │ price           │                           │
│  │ city            │         │ unit            │                           │
│  │ state           │         │ supplier_id     │────┐                      │
│  │ rating          │         │ availability    │    │                      │
│  │ total_reviews   │         │ lead_time_days  │    │                      │
│  │ is_verified     │         │ sustainability  │    │                      │
│  │ service_areas[] │         │ search_vector   │    │                      │
│  │ certifications[]│         └─────────────────┘    │                      │
│  └─────────────────┘                │               │                      │
│           │                         │               │                      │
│           │ 1                       │ 1             │                      │
│           │                         │               │                      │
│           │ n                       │ n             │                      │
│  ┌─────────────────┐      ┌─────────────────┐      │                      │
│  │SupplierReview   │      │  PriceHistory   │      │                      │
│  ├─────────────────┤      ├─────────────────┤      │                      │
│  │ id              │      │ id              │      │                      │
│  │ supplier_id     │      │ material_id     │──────┘                      │
│  │ user_id         │      │ supplier_id     │                              │
│  │ rating          │      │ price           │                              │
│  │ title           │      │ recorded_at     │                              │
│  │ content         │      └─────────────────┘                              │
│  │ quality_rating  │                                                       │
│  │ delivery_rating │                                                       │
│  │ verified_purchase│                                                      │
│  └─────────────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRICE COMPARISON                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────┐         ┌──────────────────────┐                 │
│  │  CanonicalMaterial   │ 1     n │   MaterialVariant    │                 │
│  ├──────────────────────┤─────────┤──────────────────────┤                 │
│  │ id                   │         │ id                   │                 │
│  │ name                 │         │ canonical_material_id│                 │
│  │ category             │         │ supplier_id          │                 │
│  │ specifications (JSON)│         │ price                │                 │
│  └──────────────────────┘         │ unit                 │                 │
│                                   │ lead_time_days       │                 │
│  "Concrete Mix 4000 PSI"         │ availability         │                 │
│         │                         │ last_updated         │                 │
│         │                         └──────────────────────┘                 │
│         │                                                                   │
│         ├─── Supplier A: $125/yd, 3 days                                   │
│         ├─── Supplier B: $128/yd, 1 day                                    │
│         └─── Supplier C: $135/yd, 5 days                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER DOMAIN                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐                                                       │
│  │      User       │                                                       │
│  ├─────────────────┤                                                       │
│  │ id              │                                                       │
│  │ email           │                                                       │
│  │ password_hash   │                                                       │
│  │ company_name    │                                                       │
│  │ role            │  (buyer, supplier, admin)                             │
│  │ created_at      │                                                       │
│  └─────────────────┘                                                       │
│           │                                                                 │
│           │ 1                                                               │
│           │                                                                 │
│     ┌─────┴─────┬─────────────┬─────────────┬─────────────┐               │
│     │ n         │ n           │ n           │ n           │               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │SavedSearch│ │ Favorite │ │   BOM    │ │PriceAlert│ │Notification│       │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤        │
│  │ user_id  │ │ user_id  │ │ user_id  │ │ user_id  │ │ user_id  │        │
│  │ name     │ │material_id│ │ name     │ │material_id│ │ type     │        │
│  │query_params│ │ notes    │ │ items[]  │ │target_price│ │ title    │       │
│  │alert_on  │ │created_at│ │total_cost│ │ condition│ │ message  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│                                  │                                         │
│                                  │ 1                                       │
│                                  │ n                                       │
│                            ┌──────────┐                                    │
│                            │ BOMItem  │                                    │
│                            ├──────────┤                                    │
│                            │ bom_id   │                                    │
│                            │material_id│                                   │
│                            │ quantity │                                    │
│                            │unit_price│                                    │
│                            │ notes    │                                    │
│                            └──────────┘                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## API Structure

### Authentication
```
POST   /api/v1/auth/register     Register new user
POST   /api/v1/auth/login        Login, returns JWT tokens
POST   /api/v1/auth/refresh      Refresh access token
POST   /api/v1/auth/logout       Invalidate refresh token
GET    /api/v1/auth/me           Get current user profile
```

### Materials
```
GET    /api/v1/materials/search  Search with filters, pagination, sorting
GET    /api/v1/materials/:id     Get material details
GET    /api/v1/materials/:id/compare      Get price comparison across suppliers
GET    /api/v1/materials/:id/price-history Get historical prices
POST   /api/v1/materials         Create material (admin/supplier)
PUT    /api/v1/materials/:id     Update material (admin/supplier)
DELETE /api/v1/materials/:id     Delete material (admin)
```

### Filters & Metadata
```
GET    /api/v1/filters           Get all filter options with counts
GET    /api/v1/categories        Get category list
GET    /api/v1/subcategories     Get subcategories for category
```

### Suppliers
```
GET    /api/v1/suppliers         List suppliers with filters
GET    /api/v1/suppliers/:id     Get supplier details
GET    /api/v1/suppliers/:id/materials    Get supplier's materials
GET    /api/v1/suppliers/:id/reviews      Get supplier reviews
POST   /api/v1/suppliers/:id/reviews      Add review (authenticated)
```

### User Features (Authenticated)
```
GET    /api/v1/users/favorites           Get user's favorites
POST   /api/v1/users/favorites           Add favorite
DELETE /api/v1/users/favorites/:id       Remove favorite

GET    /api/v1/users/saved-searches      Get saved searches
POST   /api/v1/users/saved-searches      Save search
DELETE /api/v1/users/saved-searches/:id  Delete saved search

GET    /api/v1/users/price-alerts        Get price alerts
POST   /api/v1/users/price-alerts        Create alert
DELETE /api/v1/users/price-alerts/:id    Delete alert

GET    /api/v1/users/notifications       Get notifications
PUT    /api/v1/users/notifications/:id/read   Mark as read
```

### Bill of Materials
```
GET    /api/v1/bom                List user's BOMs
POST   /api/v1/bom                Create new BOM
GET    /api/v1/bom/:id            Get BOM details
PUT    /api/v1/bom/:id            Update BOM
DELETE /api/v1/bom/:id            Delete BOM
POST   /api/v1/bom/:id/items      Add item to BOM
PUT    /api/v1/bom/:id/items/:item_id    Update BOM item
DELETE /api/v1/bom/:id/items/:item_id    Remove BOM item
GET    /api/v1/bom/:id/export     Export BOM (CSV/Excel)
```

---

## Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Flask 3.1.1 | Web framework |
| ORM | SQLAlchemy 2.0 | Database abstraction |
| Database | PostgreSQL 15 | Primary datastore |
| Cache | Redis 7 | Caching, rate limiting |
| Auth | Flask-JWT-Extended | JWT authentication |
| Validation | Pydantic 2.0 | Request/response validation |
| Migrations | Flask-Migrate (Alembic) | Schema migrations |
| Rate Limiting | Flask-Limiter | API protection |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 19 | UI framework |
| Build Tool | Vite 6 | Fast builds, HMR |
| Styling | Tailwind CSS 4 | Utility-first CSS |
| Components | Radix UI | Accessible primitives |
| Routing | React Router 7 | Client-side routing |
| Forms | React Hook Form + Zod | Form handling |
| Data Fetching | React Query | Server state management |
| Charts | Recharts | Data visualization |
| Icons | Lucide React | Icon library |

### Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| Containerization | Docker | Consistent environments |
| Orchestration | Docker Compose | Multi-container management |
| Frontend Server | Nginx | Static file serving, reverse proxy |
| Process Manager | Gunicorn (future) | Production WSGI server |

---

## Caching Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CACHING LAYERS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Application Cache                            │   │
│  │                            (Redis)                                   │   │
│  │                                                                      │   │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐          │   │
│  │  │  Search Cache  │ │  Filter Cache  │ │ Material Cache │          │   │
│  │  │    5 min TTL   │ │   1 hour TTL   │ │   15 min TTL   │          │   │
│  │  │                │ │                │ │                │          │   │
│  │  │ Key: query hash│ │ Key: 'filters' │ │Key: material:id│          │   │
│  │  └────────────────┘ └────────────────┘ └────────────────┘          │   │
│  │                                                                      │   │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐          │   │
│  │  │  Price History │ │Supplier Ratings│ │   Rate Limits  │          │   │
│  │  │   1 hour TTL   │ │   30 min TTL   │ │   Per-minute   │          │   │
│  │  └────────────────┘ └────────────────┘ └────────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Database Query Cache                           │   │
│  │                        (PostgreSQL)                                  │   │
│  │                                                                      │   │
│  │  • Connection pooling (SQLAlchemy pool)                             │   │
│  │  • Query plan caching (PostgreSQL)                                  │   │
│  │  • Full-text search index (GIN)                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Frontend Cache                                │   │
│  │                       (React Query)                                  │   │
│  │                                                                      │   │
│  │  • Stale-while-revalidate for search results                        │   │
│  │  • Background refetching                                            │   │
│  │  • Optimistic updates for favorites/BOM                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SECURITY LAYERS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Request Processing                              │   │
│  │                                                                      │   │
│  │  Request → Rate Limiter → Auth Check → Input Validation → Handler   │   │
│  │                                                                      │   │
│  │  • Rate Limiting: 60 req/min for search, 10 req/min for writes     │   │
│  │  • Auth: JWT access token (15 min) + refresh token (7 days)        │   │
│  │  • Validation: Pydantic schemas for all inputs                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Authentication Flow                             │   │
│  │                                                                      │   │
│  │  1. User submits credentials                                        │   │
│  │  2. Server validates, returns access + refresh tokens               │   │
│  │  3. Client stores tokens (httpOnly cookies or secure storage)       │   │
│  │  4. Access token sent with each request (Authorization header)      │   │
│  │  5. On 401, client uses refresh token to get new access token       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Data Protection                                 │   │
│  │                                                                      │   │
│  │  • Passwords: Argon2 hashing (memory-hard)                          │   │
│  │  • SQL Injection: Parameterized queries (SQLAlchemy)                │   │
│  │  • XSS: React auto-escaping, Content-Security-Policy headers        │   │
│  │  • CORS: Configured for specific origins only                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
