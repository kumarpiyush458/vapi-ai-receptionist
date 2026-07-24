from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import DemoRequest
from schemas import DemoRequestCreate


def create_demo_request_service(
    request: DemoRequestCreate,
    db: Session,
):
    existing_request = (
        db.query(DemoRequest)
        .filter(
            func.lower(DemoRequest.email) == request.email.lower()
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=409,
            detail="A demo request has already been submitted using this email address."
        )

    demo_request = DemoRequest(
        full_name=request.full_name,
        email=request.email,
        organization_name=request.organization_name,
        phone=request.phone,
        message=request.message,
    )

    db.add(demo_request)
    db.commit()
    db.refresh(demo_request)

    return demo_request

def get_demo_requests_service(db: Session):
    return db.query(DemoRequest).all()

def get_demo_request_by_id_service(
    db: Session,
    demo_request_id: int,
):
    return (
        db.query(DemoRequest)
        .filter(DemoRequest.id == demo_request_id)
        .first()
    )

def update_demo_request_status_service(
    db: Session,
    demo_request_id: int,
    status: str,
):
    demo_request = (
        db.query(DemoRequest)
        .filter(DemoRequest.id == demo_request_id)
        .first()
    )

    if not demo_request:
        return None

    demo_request.status = status

    db.commit()
    db.refresh(demo_request)

    return demo_request