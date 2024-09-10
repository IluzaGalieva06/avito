from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
import database
from typing import List, Optional
from models import Tender, Employee

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

VALID_STATUSES = ["Created", "Published", "Closed"]

@router.put("/tenders/{tenderId}/status", response_model=schemas.TenderSchema)
def update_tender_status(
    tenderId: str,
    status: str = Query(..., description="Статус тендера", enum=VALID_STATUSES),
    username: str = Query(..., description="Пользователь, который обновляет статус"),
    db: Session = Depends(database.get_db)
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не существует или некорректен")

    tender = db.query(Tender).filter(Tender.id == tenderId).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Тендер не найден")

    if tender.creator_id != user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения действия")

    tender.status = status
    db.commit()
    db.refresh(tender)

    return tender

@router.patch("/tenders/{tenderId}/edit", response_model=schemas.TenderSchema)
def edit_tender(
    tenderId: str,
    username: str = Query(..., description="Username of the person editing the tender"),
    tender_update: schemas.TenderUpdate = Depends(),
    db: Session = Depends(database.get_db)
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    tender = db.query(Tender).filter(Tender.id == tenderId).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.creator_id != user.id:
        raise HTTPException(status_code=403, detail="Insufficient rights to perform this action")

    if tender_update.name:
        tender.name = tender_update.name
    if tender_update.description:
        tender.description = tender_update.description
    if tender_update.serviceType:
        tender.serviceType = tender_update.serviceType
    if tender_update.version:
        tender.version = tender_update.version

    db.commit()
    db.refresh(tender)

    return tender