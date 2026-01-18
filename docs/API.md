# API Documentation

## Base URL
```
Development: http://localhost:5001/api/v1
Production:  https://api.example.com/api/v1
```

## Authentication

All protected endpoints require a JWT access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "company_name": "Construction Corp"  // optional
}

Response 201:
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "company_name": "Construction Corp",
    "role": "buyer",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 900,  // 15 minutes
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "buyer"
  }
}
```

### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 900
}
```

---

## Materials

### Search Materials
```http
GET /materials/search

Query Parameters:
  q              string    Search query (searches name, description)
  category       string    Filter by category
  subcategory    string    Filter by subcategory
  min_price      number    Minimum price
  max_price      number    Maximum price
  supplier_id    integer   Filter by supplier
  availability   string    "In Stock" | "Limited Stock" | "Out of Stock"
  sustainability string    "A" | "B" | "C"
  sort_by        string    "name" | "price" | "lead_time" | "relevance" (default: relevance)
  sort_order     string    "asc" | "desc" (default: asc)
  page           integer   Page number (default: 1)
  per_page       integer   Items per page (default: 20, max: 100)

Example:
GET /materials/search?q=concrete&category=Concrete&min_price=100&max_price=200&sort_by=price&sort_order=asc&page=1

Response 200:
{
  "materials": [
    {
      "id": 1,
      "name": "High-Strength Concrete Mix",
      "description": "Premium concrete mix designed for high-load applications",
      "category": "Concrete",
      "subcategory": "Ready Mix",
      "specifications": {
        "strength": "4000 PSI",
        "slump": "4-6 inches"
      },
      "price": 125.00,
      "unit": "per cubic yard",
      "availability": "In Stock",
      "lead_time_days": 1,
      "minimum_order": 1.0,
      "sustainability_rating": "B",
      "supplier": {
        "id": 2,
        "name": "Steel & Concrete Solutions",
        "rating": 4.8,
        "is_verified": true
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 45,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "filters_applied": {
    "q": "concrete",
    "category": "Concrete",
    "min_price": 100,
    "max_price": 200
  }
}
```

### Get Material Details
```http
GET /materials/:id

Response 200:
{
  "id": 1,
  "name": "High-Strength Concrete Mix",
  "description": "Premium concrete mix designed for high-load applications with 4000 PSI strength",
  "category": "Concrete",
  "subcategory": "Ready Mix",
  "specifications": {
    "strength": "4000 PSI",
    "slump": "4-6 inches",
    "aggregate_size": "3/4 inch",
    "air_content": "6%"
  },
  "price": 125.00,
  "unit": "per cubic yard",
  "availability": "In Stock",
  "lead_time_days": 1,
  "minimum_order": 1.0,
  "certifications": ["ASTM C94", "ACI 318"],
  "sustainability_rating": "B",
  "image_url": "https://example.com/concrete-mix.jpg",
  "supplier": {
    "id": 2,
    "name": "Steel & Concrete Solutions",
    "rating": 4.8,
    "total_reviews": 89,
    "is_verified": true,
    "contact_email": "info@steelconcrete.com",
    "contact_phone": "(555) 987-6543"
  },
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

### Compare Material Prices
```http
GET /materials/:id/compare

Response 200:
{
  "material": {
    "id": 1,
    "name": "High-Strength Concrete Mix",
    "category": "Concrete",
    "specifications": {...}
  },
  "comparisons": [
    {
      "supplier": {
        "id": 2,
        "name": "Steel & Concrete Solutions",
        "rating": 4.8,
        "is_verified": true
      },
      "price": 125.00,
      "unit": "per cubic yard",
      "lead_time_days": 3,
      "availability": "In Stock",
      "minimum_order": 1.0,
      "last_updated": "2024-01-15T10:00:00Z"
    },
    {
      "supplier": {
        "id": 1,
        "name": "BuildMart Supply Co.",
        "rating": 4.5,
        "is_verified": true
      },
      "price": 128.50,
      "unit": "per cubic yard",
      "lead_time_days": 1,
      "availability": "In Stock",
      "minimum_order": 2.0,
      "last_updated": "2024-01-15T09:00:00Z"
    }
  ],
  "price_analysis": {
    "min_price": 125.00,
    "max_price": 135.00,
    "avg_price": 129.50,
    "price_spread_percent": 8.0
  },
  "best_options": {
    "lowest_price": {"supplier_id": 2, "price": 125.00},
    "fastest_delivery": {"supplier_id": 1, "lead_time_days": 1},
    "best_value": {"supplier_id": 2, "reason": "Lowest price with verified supplier"}
  }
}
```

### Get Price History
```http
GET /materials/:id/price-history

Query Parameters:
  period    string    "7d" | "30d" | "90d" | "1y" (default: 30d)

Response 200:
{
  "material_id": 1,
  "current_price": 125.00,
  "period": "30d",
  "history": [
    {"date": "2024-01-01", "price": 120.00, "supplier_id": 2},
    {"date": "2024-01-08", "price": 122.50, "supplier_id": 2},
    {"date": "2024-01-15", "price": 125.00, "supplier_id": 2}
  ],
  "trend": {
    "direction": "rising",
    "change_amount": 5.00,
    "change_percent": 4.17
  },
  "statistics": {
    "min": 120.00,
    "max": 125.00,
    "avg": 122.50,
    "volatility": "low"
  }
}
```

---

## Filters & Metadata

### Get Filter Options
```http
GET /filters

Response 200:
{
  "categories": [
    {"name": "Concrete", "count": 5},
    {"name": "Steel", "count": 8},
    {"name": "Lumber", "count": 12}
  ],
  "subcategories": {
    "Concrete": [
      {"name": "Ready Mix", "count": 3},
      {"name": "Green Mix", "count": 2}
    ],
    "Steel": [
      {"name": "Structural", "count": 5},
      {"name": "Reinforcement", "count": 3}
    ]
  },
  "suppliers": [
    {"id": 1, "name": "BuildMart Supply Co.", "count": 15},
    {"id": 2, "name": "Steel & Concrete Solutions", "count": 8}
  ],
  "availability_options": ["In Stock", "Limited Stock", "Out of Stock"],
  "sustainability_ratings": ["A", "B", "C"],
  "price_range": {
    "min": 0.85,
    "max": 450.00
  }
}
```

---

## Suppliers

### List Suppliers
```http
GET /suppliers

Query Parameters:
  city           string    Filter by city
  state          string    Filter by state
  min_rating     number    Minimum rating (1-5)
  is_verified    boolean   Filter verified suppliers
  certification  string    Filter by certification
  page           integer   Page number (default: 1)
  per_page       integer   Items per page (default: 20)

Response 200:
{
  "suppliers": [
    {
      "id": 1,
      "name": "BuildMart Supply Co.",
      "description": "Leading supplier of construction materials",
      "city": "Chicago",
      "state": "IL",
      "rating": 4.5,
      "total_reviews": 150,
      "is_verified": true,
      "certifications": ["ISO 9001", "LEED Certified"],
      "materials_count": 15
    }
  ],
  "pagination": {...}
}
```

### Get Supplier Reviews
```http
GET /suppliers/:id/reviews

Query Parameters:
  sort_by    string    "newest" | "highest" | "lowest" (default: newest)
  page       integer   Page number
  per_page   integer   Items per page

Response 200:
{
  "supplier_id": 1,
  "summary": {
    "average_rating": 4.5,
    "total_reviews": 150,
    "rating_distribution": {
      "5": 80,
      "4": 45,
      "3": 15,
      "2": 7,
      "1": 3
    },
    "dimension_averages": {
      "quality": 4.6,
      "delivery": 4.3,
      "communication": 4.5,
      "value": 4.4
    }
  },
  "reviews": [
    {
      "id": 1,
      "user": {"id": 5, "company_name": "ABC Construction"},
      "rating": 5,
      "title": "Excellent quality and fast delivery",
      "content": "We've been ordering from BuildMart for 2 years...",
      "quality_rating": 5,
      "delivery_rating": 5,
      "communication_rating": 5,
      "value_rating": 4,
      "verified_purchase": true,
      "created_at": "2024-01-10T14:30:00Z"
    }
  ],
  "pagination": {...}
}
```

### Add Supplier Review (Authenticated)
```http
POST /suppliers/:id/reviews
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "rating": 5,
  "title": "Great supplier",
  "content": "Fast delivery and excellent quality materials...",
  "quality_rating": 5,
  "delivery_rating": 4,
  "communication_rating": 5,
  "value_rating": 4
}

Response 201:
{
  "message": "Review submitted successfully",
  "review": {...}
}
```

---

## User Features (Authenticated)

### Favorites

```http
GET /users/favorites
Authorization: Bearer <access_token>

Response 200:
{
  "favorites": [
    {
      "id": 1,
      "material": {...},
      "notes": "Good for Project X",
      "created_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

```http
POST /users/favorites
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "material_id": 1,
  "notes": "Consider for upcoming project"
}

Response 201:
{
  "message": "Added to favorites",
  "favorite": {...}
}
```

### Saved Searches

```http
GET /users/saved-searches
Authorization: Bearer <access_token>

Response 200:
{
  "saved_searches": [
    {
      "id": 1,
      "name": "Concrete under $130",
      "query_params": {
        "q": "concrete",
        "category": "Concrete",
        "max_price": 130
      },
      "alert_enabled": true,
      "created_at": "2024-01-05T08:00:00Z"
    }
  ]
}
```

```http
POST /users/saved-searches
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Concrete under $130",
  "query_params": {
    "q": "concrete",
    "category": "Concrete",
    "max_price": 130
  },
  "alert_enabled": true
}

Response 201:
{
  "message": "Search saved",
  "saved_search": {...}
}
```

### Price Alerts

```http
POST /users/price-alerts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "material_id": 1,
  "target_price": 120.00,
  "condition": "below"  // "below" or "above"
}

Response 201:
{
  "message": "Price alert created",
  "alert": {
    "id": 1,
    "material": {...},
    "target_price": 120.00,
    "condition": "below",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

---

## Bill of Materials (BOM)

### List BOMs
```http
GET /bom
Authorization: Bearer <access_token>

Response 200:
{
  "boms": [
    {
      "id": 1,
      "name": "Office Building Foundation",
      "description": "Materials for 50k sqft foundation",
      "status": "draft",
      "items_count": 12,
      "total_cost": 45670.00,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

### Create BOM
```http
POST /bom
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Office Building Foundation",
  "description": "Materials for 50k sqft foundation",
  "project_id": 1  // optional
}

Response 201:
{
  "message": "BOM created",
  "bom": {...}
}
```

### Get BOM Details
```http
GET /bom/:id
Authorization: Bearer <access_token>

Response 200:
{
  "id": 1,
  "name": "Office Building Foundation",
  "description": "Materials for 50k sqft foundation",
  "status": "draft",
  "items": [
    {
      "id": 1,
      "material": {
        "id": 1,
        "name": "High-Strength Concrete Mix",
        "current_price": 125.00,
        "unit": "per cubic yard"
      },
      "quantity": 100,
      "unit_price_snapshot": 122.00,
      "line_total": 12200.00,
      "notes": "For foundation slab"
    }
  ],
  "summary": {
    "items_count": 12,
    "total_cost": 45670.00,
    "estimated_savings": 1230.00  // vs current prices
  },
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

### Add Item to BOM
```http
POST /bom/:id/items
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "material_id": 1,
  "quantity": 100,
  "notes": "For foundation slab"
}

Response 201:
{
  "message": "Item added to BOM",
  "item": {...},
  "bom_total": 45670.00
}
```

### Export BOM
```http
GET /bom/:id/export?format=xlsx
Authorization: Bearer <access_token>

Response 200:
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="bom-office-building-foundation.xlsx"
```

---

## Error Responses

All errors follow this format:
```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {}  // Optional additional context
}
```

### Common Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | VALIDATION_ERROR | Invalid request data |
| 401 | UNAUTHORIZED | Missing or invalid token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource already exists |
| 422 | UNPROCESSABLE_ENTITY | Business rule violation |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

### Example Error Response
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  }
}
```

---

## Rate Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Search endpoints | 60 requests | 1 minute |
| Read endpoints | 120 requests | 1 minute |
| Write endpoints | 10 requests | 1 minute |
| Auth endpoints | 5 requests | 1 minute |

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705320000
```
