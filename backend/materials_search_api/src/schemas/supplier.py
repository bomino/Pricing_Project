from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200, description="Supplier name")
    description: Optional[str] = Field(default=None, max_length=2000)
    contact_email: Optional[EmailStr] = Field(default=None)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=50)
    zip_code: Optional[str] = Field(default=None, max_length=20)
    country: str = Field(default="USA", max_length=50)
    service_areas: Optional[List[str]] = Field(default=None)
    certifications: Optional[List[str]] = Field(default=None)
    is_verified: bool = Field(default=False)


class SupplierResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    website: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: str
    service_areas: Optional[List[str]]
    certifications: Optional[List[str]]
    rating: float
    total_reviews: int
    is_verified: bool

    class Config:
        from_attributes = True


class PaginatedSuppliersResponse(BaseModel):
    suppliers: List[SupplierResponse]
    total: int
    pages: int
    current_page: int
    per_page: int
