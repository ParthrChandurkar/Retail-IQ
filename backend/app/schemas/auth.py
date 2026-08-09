"""Authentication contracts."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class UserPublic(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool


class TokenPayload(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic
