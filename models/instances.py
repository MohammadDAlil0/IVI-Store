from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class CreateUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: Optional[str] = Field(..., min_length=3)
    name: str = Field(..., min_length=1, max_length=50)
    address: Optional[str] = None
    auth_type: int = Field(...)

    @field_validator('username')
    def username_must_not_contain_spaces(cls, v):
        if ' ' in v:
            raise ValueError('Username must not contain spaces')
        return v

class UpdateUser(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = None


class CreateProduct(BaseModel):
    title: str = Field(..., min_length=1)
    photo: str = Field(...)
    price: float = Field(..., gt=0)  # Ensure price is greater than 0
    amount: int = Field(..., ge=0)  # Ensure amount is non-negative
    category: str = Field(...)
    tags: Optional[str] = None
    cls: str = Field(...)
    brand: str = Field(...)

class UpdateProduct(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    photo: Optional[str] = None
    # Ensure price is greater than 0 if provided
    price: Optional[float] = Field(None, gt=0)
    # Ensure amount is non-negative if provided
    amount: Optional[int] = Field(None, ge=0)
    brand: Optional[str] = None


class CreateOrder(BaseModel):
    user_id: int
    done: bool
    created_at: datetime
    products: str  # Consider using a more structured format like a list of product IDs
