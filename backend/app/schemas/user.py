"""User schemas for API validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|analyst|observer)$")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|analyst|observer)$")
    is_active: Optional[bool] = None


class User(UserBase):
    """User response schema."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UserInDB(User):
    """User schema including sensitive fields."""
    hashed_password: str
