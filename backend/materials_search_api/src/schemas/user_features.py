from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any


class SavedSearchCreate(BaseModel):
    name: str
    query_params: Dict[str, Any]
    alert_enabled: bool = False

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class SavedSearchUpdate(BaseModel):
    name: Optional[str] = None
    query_params: Optional[Dict[str, Any]] = None
    alert_enabled: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v


class FavoriteCreate(BaseModel):
    material_id: int
    notes: Optional[str] = None

    @field_validator('material_id')
    @classmethod
    def material_id_positive(cls, v):
        if v <= 0:
            raise ValueError('Material ID must be positive')
        return v


class FavoriteUpdate(BaseModel):
    notes: Optional[str] = None


class SavedSearchResponse(BaseModel):
    id: int
    user_id: int
    name: str
    query_params: Dict[str, Any]
    alert_enabled: bool
    created_at: Optional[str]


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    material_id: int
    notes: Optional[str]
    created_at: Optional[str]
