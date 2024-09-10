from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import crud
import schemas
import database
from typing import List, Optional

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
    return crud.create_tender(db=db, tender=tender)


