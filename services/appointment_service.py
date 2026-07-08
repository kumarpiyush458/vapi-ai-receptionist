from logger import logger
import datetime as dt

from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import Appointment
from google_calendar import (
    create_calendar_event,
    update_calendar_event,
    delete_calendar_event,
)
from utils import (
    parse_natural_date,
    parse_natural_time,
    find_next_available_slot,
)
from schemas import (
    AppointmentRequest,
    AppointmentResponse,
    CancelAppointmentRequest,
    CancelAppointmentResponse,
)
from sqlalchemy import select

def schedule_appointment_service(
    request: AppointmentRequest,
    db: Session
):
    # Parse date
    actual_date = parse_natural_date(request.appointment_date)

    # Parse time
    appointment_time = parse_natural_time(
        request.appointment_time
    )

    # Combine date and time
    start_datetime = dt.datetime.combine(
        actual_date,
        appointment_time
    )

    existing_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.doctor == request.doctor,
            Appointment.start_time == start_datetime,
            Appointment.canceled == False
        )
        .first()
    )

    if existing_appointment:

        suggested_slot = find_next_available_slot(
            request.doctor,
            start_datetime,
            db
        )

        raise HTTPException(
            status_code=409,
            detail={
                "message": "Requested slot is already booked.",
                "suggested_date": suggested_slot.strftime("%Y-%m-%d"),
                "suggested_time": suggested_slot.strftime("%I:%M %p")
            }
        )

    new_appointment = Appointment(
        patient_name=request.patient_name,
        doctor=request.doctor,
        reason=request.reason,
        start_time=start_datetime,
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    logger.info(
        f"Appointment created successfully for {new_appointment.patient_name} with {new_appointment.doctor}"
    )

    try:
        google_event = create_calendar_event(
            patient_name=new_appointment.patient_name,
            doctor=new_appointment.doctor,
            reason=new_appointment.reason,
            start_datetime=new_appointment.start_time
        )

        new_appointment.google_event_id = google_event["id"]

        db.commit()
        db.refresh(new_appointment)

    except Exception:
        logger.exception(
            f"Failed to sync Google Calendar for appointment ID {new_appointment.id}"
        )

        raise HTTPException(
            status_code=500,
            detail="Appointment was created, but Google Calendar synchronization failed."
        )

    return AppointmentResponse(
        id=new_appointment.id,
        patient_name=new_appointment.patient_name,
        doctor=new_appointment.doctor,
        reason=new_appointment.reason,
        start_time=new_appointment.start_time,
        canceled=new_appointment.canceled,
        created_at=new_appointment.created_at,
    )

def cancel_appointment_service(
    request: CancelAppointmentRequest,
    db: Session
):
    
    actual_date = parse_natural_date(request.date)

    start_dt = dt.datetime.combine(
        actual_date,
        dt.time.min
    )
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Appointment)
        .where(Appointment.patient_name == request.patient_name)
        .where(Appointment.start_time >= start_dt)
        .where(Appointment.start_time < end_dt)
        .where(Appointment.canceled == False)
    )

    appointments = result.scalars().all()

    if not appointments:
        raise HTTPException(
            status_code=404,
            detail="No matching appointment for the details found in our system"
        )

    for appointment in appointments:

        if appointment.google_event_id:
            delete_calendar_event(appointment.google_event_id)

        appointment.canceled = True

    db.commit()

    return CancelAppointmentResponse(
        patient_name=request.patient_name,
        canceled_count=len(appointments)
    )
