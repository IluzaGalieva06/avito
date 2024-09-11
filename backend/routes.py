from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
import crud
import schemas
import database
from typing import List, Optional
from models import Tender, Employee, Bid, OrganizationResponsibility, BidFeedback

router = APIRouter()


@router.get("/ping")
def ping():
    return "ok"


@router.get("/tenders", response_model=List[schemas.TenderSchema])
def list_tenders(
    db: Session = Depends(database.get_db),
    limit: int = Query(
        5, ge=0, le=50, description="Максимальное число возвращаемых объектов"
    ),
    offset: int = Query(0, ge=0, description="Количество пропущенных объектов"),
    service_type: Optional[List[str]] = Query(
        None, description="Фильтрация по типам услуг"
    ),
):
    tenders = crud.get_tenders(
        db=db, limit=limit, offset=offset, service_type=service_type
    )
    return tenders


@router.post("/tenders/new", response_model=schemas.TenderSchema)
def create_tender(tender: schemas.TenderCreate, db: Session = Depends(database.get_db)):
    return crud.create_tender(
        db=db, tender=tender, creator_username=tender.creatorUsername
    )


@router.get("/tenders/my", response_model=List[schemas.TenderSchema])
def get_user_tenders(
    username: str,
    limit: int = Query(
        5, ge=0, le=50, description="Максимальное число возвращаемых объектов"
    ),
    offset: int = Query(0, ge=0, description="Количество пропущенных объектов"),
    db: Session = Depends(database.get_db),
):
    tenders = crud.get_tenders_by_user(
        db=db, username=username, limit=limit, offset=offset
    )
    if not tenders:
        raise HTTPException(
            status_code=404, detail="No tenders found for the specified user"
        )
    return tenders


@router.get("/tenders/{tenderId}/status", response_model=str)
def get_tender_status(tenderId: str, db: Session = Depends(database.get_db)):
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
    db: Session = Depends(database.get_db),
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(
            status_code=401, detail="Пользователь не существует или некорректен"
        )

    tender = db.query(Tender).filter(Tender.id == tenderId).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Тендер не найден")

    if tender.creator_id != user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для выполнения действия"
        )

    tender.status = status
    db.commit()
    db.refresh(tender)

    return tender


@router.patch("/tenders/{tenderId}/edit", response_model=schemas.TenderSchema)
def edit_tender(
    tenderId: str,
    username: str = Query(..., description="Username of the person editing the tender"),
    tender_update: schemas.TenderUpdate = Depends(),
    db: Session = Depends(database.get_db),
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    tender = db.query(Tender).filter(Tender.id == tenderId).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.creator_id != user.id:
        raise HTTPException(
            status_code=403, detail="Insufficient rights to perform this action"
        )

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


@router.put(
    "/tenders/{tenderId}/rollback/{version}", response_model=schemas.TenderSchema
)
def rollback_tender(
    tenderId: str,
    version: int,
    username: str = Query(
        ..., description="Username of the person performing the rollback"
    ),
    db: Session = Depends(database.get_db),
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    tender = db.query(Tender).filter(Tender.id == tenderId).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.creator_id != user.id:
        raise HTTPException(
            status_code=403, detail="Insufficient rights to perform this action"
        )

    if version >= tender.version:
        raise HTTPException(
            status_code=400, detail="Invalid version number for rollback"
        )

    tender.version = version

    db.commit()
    db.refresh(tender)

    return tender


@router.post("/bids/new", response_model=schemas.Bid)
def create_bid(bid: schemas.BidCreate, db: Session = Depends(database.get_db)):
    return crud.create_bid(db=db, bid_data=bid)


@router.get("/bids/my", response_model=List[schemas.Bid])
def get_user_bids(
    username: str,
    limit: int = Query(
        5, ge=0, le=50, description="Максимальное число возвращаемых объектов"
    ),
    offset: int = Query(0, ge=0, description="Количество пропущенных объектов"),
    db: Session = Depends(database.get_db),
):
    bids = crud.get_bids_by_user(db=db, username=username, limit=limit, offset=offset)
    if not bids:
        raise HTTPException(
            status_code=404, detail="No bids found for the specified user"
        )
    return bids


@router.get("/bids/{tenderId}/list", response_model=List[schemas.Bid])
def list_bids_for_tender(
    tenderId: str,
    username: str,
    limit: int = Query(
        5, ge=0, le=50, description="Максимальное число возвращаемых объектов"
    ),
    offset: int = Query(0, ge=0, description="Количество пропущенных объектов"),
    db: Session = Depends(database.get_db),
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    tender = db.query(Tender).filter(Tender.id == tenderId).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    bids = crud.get_bids_for_tender(
        db=db, tender_id=tenderId, limit=limit, offset=offset
    )
    return bids


@router.get("/bids/{bidId}/status", response_model=str)
def get_bid_status(
    bidId: UUID,
    username: str = Query(
        ..., description="Username of the person requesting the status"
    ),
    db: Session = Depends(database.get_db),
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    bid = db.query(Bid).filter(Bid.id == bidId).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    return bid.status


VALID_BID_STATUSES = ["Created", "Published", "Canceled", "Approved", "Rejected"]


@router.put("/bids/{bidId}/status", response_model=schemas.BidStatusResponse)
def update_bid_status(
    bidId: UUID,
    status: str = Query(..., description="Статус предложения", enum=VALID_BID_STATUSES),
    username: str = Query(..., description="Пользователь, который обновляет статус"),
    db: Session = Depends(database.get_db),
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(
            status_code=401, detail="Пользователь не существует или некорректен"
        )

    bid = db.query(Bid).filter(Bid.id == bidId).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Предложение не найдено")

    if bid.author_id != user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для выполнения действия"
        )

    bid.status = status
    db.commit()
    db.refresh(bid)

    return schemas.BidStatusResponse(status=bid.status)


@router.patch("/bids/{bidId}/edit", response_model=schemas.Bid)
def edit_bid(
    bidId: UUID,
    bid_update: schemas.BidUpdate,
    username: str = Query(..., description="Username of the person editing the bid"),
    db: Session = Depends(database.get_db),
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    bid = db.query(Bid).filter(Bid.id == bidId).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    if bid.author_id != user.id:
        raise HTTPException(
            status_code=403, detail="Insufficient rights to perform this action"
        )

    if bid_update.name:
        bid.name = bid_update.name
    if bid_update.description:
        bid.description = bid_update.description

    db.commit()
    db.refresh(bid)

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


@router.put("/bids/{bidId}/submit_decision", response_model=schemas.Bid)
def submit_decision(
    bidId: UUID,
    decision: str = Query(
        ..., description="Decision on the bid", enum=["Approved", "Rejected"]
    ),
    username: str = Query(
        ..., description="Username of the person submitting the decision"
    ),
    db: Session = Depends(database.get_db),
):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user:
        raise HTTPException(
            status_code=401, detail="User does not exist or is incorrect"
        )

    bid = db.query(Bid).filter(Bid.id == bidId).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    tender = db.query(Tender).filter(Tender.id == bid.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    organization_responsibility = (
        db.query(OrganizationResponsibility)
        .filter(
            OrganizationResponsibility.user_id == user.id,
            OrganizationResponsibility.organization_id == bid.organization_id,
        )
        .first()
    )

    if not organization_responsibility:
        raise HTTPException(
            status_code=403, detail="Insufficient rights to perform this action"
        )

    if decision == "Approved":
        bid.status = "Approved"
        if all(
            b.status == "Approved"
            for b in db.query(Bid).filter(Bid.tender_id == bid.tender_id).all()
        ):
            tender.status = "Closed"
            db.commit()
    elif decision == "Rejected":
        bid.status = "Rejected"

    db.commit()
    db.refresh(bid)

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


@router.put("/bids/{bidId}/feedback", response_model=schemas.BidFeedbackCreate)
def submit_bid_feedback(
    bidId: UUID,
    username: str = Query(...),
    feedback: str = Body(..., embed=True),
    db: Session = Depends(database.get_db),
):
    feedback_data = schemas.BidFeedbackCreate(
        username=username, feedback=feedback, bidId=bidId
    )
    feedback = crud.create_feedback(
        db=db, bidId=bidId, feedback_data=feedback_data, username=username
    )
    return schemas.BidFeedbackCreate(
        bidId=feedback.bid_id, username=feedback.username, feedback=feedback.feedback
    )


@router.put("/bids/{bidId}/rollback/{version}", response_model=schemas.Bid)
def rollback_bid(
    bidId: UUID,
    version: int,
    username: str = Query(
        ..., description="Username of the person performing the rollback"
    ),
    db: Session = Depends(database.get_db),
):
    bid = crud.rollback_bid(db=db, bid_id=bidId, version=version, username=username)
    return bid


@router.get("/bids/{tenderId}/reviews", response_model=List[schemas.BidFeedbackCreate])
def get_bid_reviews(
    tenderId: UUID,
    authorUsername: str,
    requesterUsername: str,
    limit: int = Query(
        5, ge=0, le=50, description="Maximum number of objects to return"
    ),
    offset: int = Query(
        0, ge=0, description="Number of objects to skip from the beginning"
    ),
    db: Session = Depends(database.get_db),
):
    requester = (
        db.query(Employee).filter(Employee.username == requesterUsername).first()
    )
    if not requester:
        raise HTTPException(status_code=401, detail="Requester user not found")

    author = db.query(Employee).filter(Employee.username == authorUsername).first()
    if not author:
        raise HTTPException(status_code=401, detail="Author user not found")

    tender = db.query(Tender).filter(Tender.id == tenderId).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    org_responsibility = (
        db.query(OrganizationResponsibility)
        .filter(
            OrganizationResponsibility.user_id == requester.id,
            OrganizationResponsibility.organization_id == tender.organizationId,
        )
        .first()
    )

    if not org_responsibility:
        raise HTTPException(
            status_code=403, detail="Insufficient rights to view reviews"
        )

    bids = (
        db.query(Bid)
        .filter(Bid.tender_id == tenderId, Bid.author_id == author.id)
        .all()
    )
    bid_ids = [bid.id for bid in bids]

    if not bid_ids:
        raise HTTPException(
            status_code=404, detail="No bids found for the specified author and tender"
        )

    reviews = (
        db.query(BidFeedback)
        .filter(BidFeedback.bid_id.in_(bid_ids))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        schemas.BidFeedbackCreate(
            bidId=review.bid_id, username=review.username, feedback=review.feedback
        )
        for review in reviews
    ]
