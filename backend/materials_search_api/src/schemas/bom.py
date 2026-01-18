from typing import Optional, List
from pydantic import BaseModel, Field


class BOMCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    project_id: Optional[int] = None


class BOMUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern='^(draft|finalized|ordered)$')
    project_id: Optional[int] = None


class BOMItemCreate(BaseModel):
    material_id: int
    quantity: float = Field(..., gt=0)
    notes: Optional[str] = None
    sort_order: Optional[int] = None


class BOMItemUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None
    sort_order: Optional[int] = None
    refresh_price: Optional[bool] = False


class BOMItemReorder(BaseModel):
    item_order: List[int]


class BOMDuplicate(BaseModel):
    new_name: Optional[str] = Field(None, min_length=1, max_length=200)
