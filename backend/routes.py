from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
import database
from typing import List, Optional
from models import Tender

router = APIRouter()

@router.get("/ping")
def ping():
    return "ok"

@router.get("/tenders", response_model=List[schemas.TenderSchema])
def list_tenders(
    db: Session = Depends(database.get_db),
    limit: int = Query(5, ge=0, le=50, description="Максимальное число возвращаемых объектов"),
    offset: int = Query(0, ge=0, description="Количество пропущенных объектов"),
    service_type: Optional[List[str]] = Query(None, description="Фильтрация по типам услуг")
):
    tenders = crud.get_tenders(db=db, limit=limit, offset=offset, service_type=service_type)
    return tenders

@router.post("/tenders/new", response_model=schemas.TenderSchema)
def create_tender(tender: schemas.TenderCreate, db: Session = Depends(database.get_db)):
    return crud.create_tender(db=db, tender=tender, creator_username=tender.creatorUsername)

@router.get("/tenders/my", response_model=List[schemas.TenderSchema])
def get_user_tenders(
    username: str,
    limit: int = Query(5, ge=0, le=50, description="Максимальное число возвращаемых объектов"),
    offset: int = Query(0, ge=0, description="Количество пропущенных объектов"),
    db: Session = Depends(database.get_db)
):
    tenders = crud.get_tenders_by_user(db=db, username=username, limit=limit, offset=offset)
    if not tenders:
        raise HTTPException(status_code=404, detail="No tenders found for the specified user")
    return tenders

@router.get("/tenders/{tenderId}/status", response_model=str)
def get_tender_status(
    tenderId: str,
    db: Session = Depends(database.get_db)
):
    tender = db.query(Tender).filter(Tender.id == tenderId).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    return tender.status

