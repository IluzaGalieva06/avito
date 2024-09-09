from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Схема для создания тендера
class TenderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    organization_id: int
    status: str = "CREATED"

    class Config:
        orm_mode = True

# Схема для отображения тендера (например, в ответе)
class Tender(BaseModel):
    id: int
    name: str
    description: Optional[str]
    organization_id: int
    status: str
    version: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

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
