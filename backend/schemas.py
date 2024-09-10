from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TenderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    organizationId: int = Field(..., alias='organizationId')
    serviceType: Optional[str] = Field(None, max_length=50, alias='serviceType')
    status: str = "CREATED"

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class TenderSchema(BaseModel):
    id: int
    name: str
    description: str
    status: str
    serviceType: str = Field(..., alias='serviceType')
    organizationId: int = Field(..., alias='organizationId')  # Добавьте это поле
    version: int
    createdAt: datetime = Field(..., alias='created_at')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# Схема для создания предложения (bid)
class BidCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tender_id: int
    organization_id: int
    status: str = "CREATED"

    class Config:
        orm_mode = True

# Схема для отображения предложения (bid)
class Bid(BaseModel):
    id: int
    name: str
    description: Optional[str]
    tender_id: int
    organization_id: int
    status: str
    version: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
