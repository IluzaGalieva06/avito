from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from typing import List, Optional


def create_tender(db: Session, tender: schemas.TenderCreate, creator_username: str):
    user = db.query(models.Employee).filter(models.Employee.username == creator_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_tender = models.Tender(
        name=tender.name,
        description=tender.description,
        organizationId=tender.organizationId,
        creator_id=user.id,
        serviceType=tender.serviceType,
        status=tender.status
    )
    db.add(db_tender)
    db.commit()
    db.refresh(db_tender)
    return db_tender


def get_tenders(db: Session, limit: int, offset: int, service_type: Optional[List[str]] = None):
    query = db.query(models.Tender)

    if service_type:
        query = query.filter(models.Tender.service_type.in_(service_type))

    query = query.order_by(models.Tender.name).offset(offset).limit(limit)

    return query.all()

def get_tenders_by_user(db: Session, username: str, limit: int, offset: int) -> List[schemas.TenderSchema]:
    user = db.query(models.Employee).filter(models.Employee.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(models.Tender).filter(models.Tender.creator_id == user.id)
    query = query.order_by(models.Tender.name).offset(offset).limit(limit)

    tenders = query.all()

    results = []
    for tender in tenders:
        results.append({
            **tender.__dict__,
            'creatorUsername': username
        })

    return results


