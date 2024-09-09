from sqlalchemy.orm import Session
from . import models, schemas

def create_tender(db: Session, tender: schemas.TenderCreate):
    db_tender = models.Tender(**tender.dict())
    db.add(db_tender)
    db.commit()
    db.refresh(db_tender)
    return db_tender

def get_tenders(db: Session):
    return db.query(models.Tender).all()
