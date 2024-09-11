from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from typing import List, Optional


def create_tender(db: Session, tender: schemas.TenderCreate, creator_username: str):
    user = (
        db.query(models.Employee)
        .filter(models.Employee.username == creator_username)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_tender = models.Tender(
        name=tender.name,
        description=tender.description,
        organizationId=tender.organizationId,
        creator_id=user.id,
        serviceType=tender.serviceType,
        status=tender.status,
    )
    db.add(db_tender)
    db.commit()
    db.refresh(db_tender)
    return db_tender


def get_tenders(
    db: Session, limit: int, offset: int, service_type: Optional[List[str]] = None
):
    query = db.query(models.Tender)

    if service_type:
        query = query.filter(models.Tender.service_type.in_(service_type))

    query = query.order_by(models.Tender.name).offset(offset).limit(limit)

    return query.all()


def get_tenders_by_user(
    db: Session, username: str, limit: int, offset: int
) -> List[schemas.TenderSchema]:
    user = (
        db.query(models.Employee).filter(models.Employee.username == username).first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(models.Tender).filter(models.Tender.creator_id == user.id)
    query = query.order_by(models.Tender.name).offset(offset).limit(limit)

    tenders = query.all()

    results = []
    for tender in tenders:
        results.append({**tender.__dict__, "creatorUsername": username})

    return results


def create_bid(db: Session, bid_data: schemas.BidCreate):
    user = (
        db.query(models.Employee)
        .filter(models.Employee.username == bid_data.creator_username)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    author_type = "User"

    db_bid = models.Bid(
        name=bid_data.name,
        description=bid_data.description,
        tender_id=bid_data.tender_id,
        organization_id=bid_data.organization_id,
        status=bid_data.status,
        version=1,
        author_id=user.id,
    )
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)

    return {
        "id": db_bid.id,
        "name": db_bid.name,
        "description": db_bid.description,
        "tenderId": db_bid.tender_id,
        "organizationId": db_bid.organization_id,
        "status": db_bid.status,
        "version": db_bid.version,
        "createdAt": db_bid.created_at,
        "authorId": db_bid.author_id,
        "authorType": author_type,
    }


def get_bids_by_user(
    db: Session, username: str, limit: int, offset: int
) -> List[schemas.Bid]:
    user = (
        db.query(models.Employee).filter(models.Employee.username == username).first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(models.Bid).filter(models.Bid.author_id == user.id)
    query = query.order_by(models.Bid.created_at).offset(offset).limit(limit)

    bids = query.all()

    return [
        schemas.Bid(
            id=bid.id,
            name=bid.name,
            description=bid.description,
            tenderId=bid.tender_id,
            status=bid.status,
            version=bid.version,
            createdAt=bid.created_at,
            authorId=bid.author_id,
            authorType="User",
        )
        for bid in bids
    ]


def get_bids_for_tender(
    db: Session, tender_id: str, limit: int, offset: int
) -> List[schemas.Bid]:
    query = db.query(models.Bid).filter(models.Bid.tender_id == tender_id)
    query = query.order_by(models.Bid.created_at).offset(offset).limit(limit)

    bids = query.all()

    results = []
    for bid in bids:
        author_type = "Organization" if bid.organization_id else "User"
        results.append(
            schemas.Bid(
                id=bid.id,
                name=bid.name,
                description=bid.description,
                tenderId=bid.tender_id,
                status=bid.status,
                version=bid.version,
                createdAt=bid.created_at,
                authorId=bid.author_id,
                authorType=author_type,
            )
        )

    return results


def create_feedback(
    db: Session, bidId: UUID, username: str, feedback_data: schemas.BidFeedbackCreate
):
    bid = db.query(models.Bid).filter(models.Bid.id == bidId).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    user = (
        db.query(models.Employee).filter(models.Employee.username == username).first()
    )

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    db_feedback = models.BidFeedback(
        bid_id=feedback_data.bidId,
        username=feedback_data.username,
        feedback=feedback_data.feedback,
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def rollback_bid(db: Session, bid_id: UUID, version: int, username: str):
    user = (
        db.query(models.Employee).filter(models.Employee.username == username).first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bid = db.query(models.Bid).filter(models.Bid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    if version >= bid.version:
        raise HTTPException(
            status_code=400, detail="Invalid version number for rollback"
        )
    print(bid.version)
    bid.version = version
    db.commit()
    db.refresh(bid)
    print(bid.version)

    return schemas.Bid(
        id=bid.id,
        name=bid.name,
        description=bid.description,
        tenderId=bid.tender_id,
        status=bid.status,
        version=bid.version,
        createdAt=bid.created_at,
        authorId=bid.author_id,
        authorType="User",
    )
