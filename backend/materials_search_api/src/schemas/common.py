from pydantic import BaseModel, Field
from typing import Optional, List, Any


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")


class ValidationErrorDetail(BaseModel):
    loc: List[str] = Field(description="Error location path")
    msg: str = Field(description="Error message")
    type: str = Field(description="Error type")


class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[List[ValidationErrorDetail]] = Field(
        default=None, description="Validation error details"
    )


class SuccessResponse(BaseModel):
    message: str = Field(description="Success message")
    data: Optional[Any] = Field(default=None, description="Response data")
