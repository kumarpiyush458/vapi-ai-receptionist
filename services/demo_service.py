from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import DemoRequest
from schemas import DemoRequestCreate


# -----------------------------
# Create Demo Request
# -----------------------------
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
            detail="A demo request has already been submitted using this email address.",
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


# -----------------------------
# Get All Demo Requests
# -----------------------------
def get_demo_requests_service(db: Session):
    return (
        db.query(DemoRequest)
        .order_by(DemoRequest.created_at.desc())
        .all()
    )


# -----------------------------
# Get Demo Request By ID
# -----------------------------
def get_demo_request_by_id_service(
    db: Session,
    demo_request_id: int,
):
    return (
        db.query(DemoRequest)
        .filter(DemoRequest.id == demo_request_id)
        .first()
    )


# -----------------------------
# Update Lead Status
# -----------------------------
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


# -----------------------------
# Dashboard Statistics
# -----------------------------
def get_dashboard_stats_service(db: Session):
    demo_requests = db.query(DemoRequest).all()

    return {
        "total_leads": len(demo_requests),
        "new": sum(
            1 for lead in demo_requests
            if lead.status == "New"
        ),
        "contacted": sum(
            1 for lead in demo_requests
            if lead.status == "Contacted"
        ),
        "demo_scheduled": sum(
            1 for lead in demo_requests
            if lead.status == "Demo Scheduled"
        ),
        "proposal_sent": sum(
            1 for lead in demo_requests
            if lead.status == "Proposal Sent"
        ),
        "won": sum(
            1 for lead in demo_requests
            if lead.status == "Won"
        ),
        "lost": sum(
            1 for lead in demo_requests
            if lead.status == "Lost"
        ),
    }


# -----------------------------
# Delete Lead
# -----------------------------
def delete_demo_request_service(
    db: Session,
    demo_request_id: int,
):
    demo_request = (
        db.query(DemoRequest)
        .filter(DemoRequest.id == demo_request_id)
        .first()
    )

    if not demo_request:
        return False

    db.delete(demo_request)
    db.commit()

    return True