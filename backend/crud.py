from sqlalchemy.orm import Session
import models
import schemas
from typing import List, Optional

def create_tender(db: Session, tender: schemas.TenderCreate):
    db_tender = models.Tender(**tender.dict())
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
