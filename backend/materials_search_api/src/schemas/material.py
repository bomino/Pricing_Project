from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class MaterialSortBy(str, Enum):
    name = "name"
    price = "price"
    lead_time = "lead_time_days"
    availability = "availability"


class SustainabilityRating(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class MaterialSearchParams(BaseModel):
    q: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Search query for name/description"
    )
    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Filter by category"
    )
    subcategory: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Filter by subcategory"
    )
    min_price: Optional[float] = Field(
        default=None,
        ge=0,
        description="Minimum price filter"
    )
    max_price: Optional[float] = Field(
        default=None,
        ge=0,
        description="Maximum price filter"
    )
    supplier_id: Optional[int] = Field(
        default=None,
        ge=1,
        description="Filter by supplier ID"
    )
    availability: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Filter by availability status"
    )
    sustainability_rating: Optional[SustainabilityRating] = Field(
        default=None,
        description="Filter by sustainability rating (A/B/C/D)"
    )
    sort_by: Optional[MaterialSortBy] = Field(
        default=MaterialSortBy.name,
        description="Sort field"
    )
    sort_order: Optional[SortOrder] = Field(
        default=SortOrder.asc,
        description="Sort order"
    )
    page: int = Field(default=1, ge=1, description="Page number (offset pagination)")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
    cursor: Optional[str] = Field(
        default=None,
        description="Cursor for cursor-based pagination (base64 encoded)"
    )
    use_cursor: bool = Field(
        default=False,
        description="Use cursor-based pagination instead of offset"
    )

    @field_validator("max_price")
    @classmethod
    def max_price_must_be_greater_than_min(cls, v, info):
        if v is not None and info.data.get("min_price") is not None:
            if v < info.data["min_price"]:
                raise ValueError("max_price must be greater than or equal to min_price")
        return v


class MaterialCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200, description="Material name")
    description: Optional[str] = Field(default=None, max_length=2000)
    category: str = Field(min_length=1, max_length=100, description="Material category")
    subcategory: Optional[str] = Field(default=None, max_length=100)
    specifications: Optional[Dict[str, Any]] = Field(default=None)
    price: Optional[float] = Field(default=None, ge=0)
    unit: Optional[str] = Field(default=None, max_length=50)
    supplier_id: int = Field(ge=1, description="Supplier ID")
    availability: str = Field(default="In Stock", max_length=50)
    lead_time_days: int = Field(default=0, ge=0)
    minimum_order: Optional[float] = Field(default=None, ge=0)
    certifications: Optional[List[str]] = Field(default=None)
    sustainability_rating: Optional[SustainabilityRating] = Field(default=None)
    image_url: Optional[str] = Field(default=None, max_length=500)


class MaterialResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    subcategory: Optional[str]
    specifications: Optional[Dict[str, Any]]
    price: Optional[float]
    unit: Optional[str]
    supplier_id: int
    supplier_name: Optional[str]
    availability: str
    lead_time_days: int
    minimum_order: Optional[float]
    certifications: Optional[List[str]]
    sustainability_rating: Optional[str]
    image_url: Optional[str]

    class Config:
        from_attributes = True


class PaginatedMaterialsResponse(BaseModel):
    materials: List[MaterialResponse]
    total: int
    pages: int
    current_page: int
    per_page: int
    has_next: bool
    has_prev: bool
