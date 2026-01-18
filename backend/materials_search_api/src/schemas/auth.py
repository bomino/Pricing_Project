from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    company_name: Optional[str] = None
    role: str = 'buyer'

    @field_validator('username')
    @classmethod
    def username_min_length(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @field_validator('role')
    @classmethod
    def valid_role(cls, v):
        allowed_roles = ['buyer', 'supplier', 'admin']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    company_name: Optional[str]
    role: str
    created_at: Optional[str]
