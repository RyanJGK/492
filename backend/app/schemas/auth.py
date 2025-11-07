"""Authentication schemas."""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: Optional[UUID] = None
    exp: Optional[int] = None
    type: Optional[str] = None
