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