from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class Employee(Base):
    __tablename__ = "employee"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Organization(Base):
    __tablename__ = "organization"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum("IE", "LLC", "JSC", name="organization_type"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Tender(Base):
    __tablename__ = "tender"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    organizationId = Column(UUID(as_uuid=True), ForeignKey("organization.id"))
    creator_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"))
    serviceType = Column(String(50))
    status = Column(String(50), default="CREATED")
    version = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Bid(Base):
    __tablename__ = "bid"
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tender.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"))
    status = Column(String(50), default="CREATED")
    version = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    feedbacks = relationship("BidFeedback", back_populates="bid")


class OrganizationResponsibility(Base):
    __tablename__ = "organization_responsibility"
    user_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), primary_key=True)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id"), primary_key=True
    )


class BidFeedback(Base):
    __tablename__ = "bid_feedback"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bid_id = Column(UUID(as_uuid=True), ForeignKey("bid.id"))
    username = Column(String(50), nullable=False)
    feedback = Column(Text, nullable=False)

    bid = relationship("Bid", back_populates="feedbacks")
