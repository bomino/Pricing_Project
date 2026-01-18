from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any


class CanonicalMaterialCreate(BaseModel):
    name: str
    category: str
    subcategory: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @field_validator('category')
    @classmethod
    def category_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip()


class MaterialVariantCreate(BaseModel):
    supplier_id: int
    price: float
    unit: str
    material_id: Optional[int] = None
    lead_time_days: Optional[int] = None
    availability: Optional[str] = None
    minimum_order: Optional[float] = None

    @field_validator('price')
    @classmethod
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @field_validator('supplier_id')
    @classmethod
    def supplier_id_positive(cls, v):
        if v <= 0:
            raise ValueError('Supplier ID must be positive')
        return v


class PriceRangeResponse(BaseModel):
    min: float
    max: float
    avg: float


class BestValueResponse(BaseModel):
    supplier_id: Optional[int]
    material_id: Optional[int]
    reason: str


class ComparisonItemResponse(BaseModel):
    supplier: Optional[Dict[str, Any]]
    price: float
    unit: Optional[str]
    lead_time_days: Optional[int]
    availability: Optional[str]
    minimum_order: Optional[float]
    material_id: Optional[int]
    last_updated: Optional[str]


class MaterialComparisonResponse(BaseModel):
    material: Dict[str, Any]
    comparisons: List[ComparisonItemResponse]
    price_range: PriceRangeResponse
    best_value: Optional[BestValueResponse]


class PriceStatisticsResponse(BaseModel):
    min_price: float
    max_price: float
    avg_price: float
    variant_count: int
