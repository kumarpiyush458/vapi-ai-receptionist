# Step 1: Import Database Objects
from services.doctor_service import (
    recommend_doctor,
    find_patient_by_phone,
)

from schemas import (
    AppointmentRequest,
    AppointmentResponse,
    CancelAppointmentRequest,
    CancelAppointmentResponse,
    ListAppointmentRequest,
    RecommendDoctorRequest,
    RecommendDoctorResponse,
    RescheduleAppointmentRequest,
    RescheduleAppointmentResponse,
)

from utils import (
    parse_natural_date,
    parse_natural_time,
    get_next_slot,
    is_slot_available,
    find_next_available_slot,
)

from google_calendar import (
    create_calendar_event,
    delete_calendar_event,
    update_calendar_event
)
from database import init_db, Appointment, Doctor, Patient, get_db
from sqlalchemy.orm import Session
init_db()

from services.appointment_service import (
    schedule_appointment_service,
    cancel_appointment_service,
)


# step 3: Create Data Contracts using Pydantic models
import datetime as dt 


# Step 2: Create FastAPI application and endpoints pseudoo code

from fastapi import FastAPI, HTTPException, Depends


app = FastAPI()

# Schedule Appointments
@app.post("/schedule_appointment/")
def schedule_appointment(
    request: AppointmentRequest,
    db: Session = Depends(get_db)
):
    return schedule_appointment_service(
        request,
        db
    )

# Cancel Appointments
from sqlalchemy import select

@app.post("/cancel_appointment/")
def cancel_appointment(
    request: CancelAppointmentRequest,
    db: Session = Depends(get_db)
):
    return cancel_appointment_service(
        request,
        db
    )

# List Appointment
@app.post("/list_appointments/")
def list_appointments(
    request: ListAppointmentRequest,
    db: Session = Depends(get_db)
):

    start_dt = dt.datetime.combine(request.date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Appointment)
        .where(Appointment.canceled == False)
        .where(Appointment.start_time >= start_dt)
        .where(Appointment.start_time < end_dt)
        .order_by(Appointment.start_time.asc())
    )

    appointments = result.scalars().all()

    booked_appointments = []

    for appointment in appointments:
        appointment_obj = AppointmentResponse(
            id=appointment.id,
            patient_name=appointment.patient_name,
            doctor=appointment.doctor,
            reason=appointment.reason,
            start_time=appointment.start_time,
            canceled=appointment.canceled,
            created_at=appointment.created_at,
        )

        booked_appointments.append(appointment_obj)

    return booked_appointments

# Recommend doctors
@app.post("/recommend_doctor/")
def recommend_doctor_endpoint(
    request: RecommendDoctorRequest,
    db: Session = Depends(get_db)
):
    doctor = recommend_doctor(
        request.symptoms,
         db
    )

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="No suitable doctor found for these symptoms."
        )
    
    return RecommendDoctorResponse(
        department=doctor.department,
        doctor_name=doctor.doctor_name,
        experience=doctor.experience
    )

# Reschedule Appointment
@app.post("/reschedule_appointment/")
def reschedule_appointment(
    request: RescheduleAppointmentRequest,
    db: Session = Depends(get_db)
):
    old_date = parse_natural_date(request.old_date)

    start_dt = dt.datetime.combine(
        old_date,
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

    appointment = result.scalars().first()

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="No appointment found for the given details."
        )

    actual_date = parse_natural_date(request.new_date)

    appointment_time = parse_natural_time(request.new_time)

    new_start_datetime = dt.datetime.combine(
        actual_date,
        appointment_time
    )
    appointment.start_time = new_start_datetime

    if appointment.google_event_id:
        update_calendar_event(
            event_id=appointment.google_event_id,
            patient_name=appointment.patient_name,
            doctor=appointment.doctor,
            reason=appointment.reason,
            start_datetime=appointment.start_time
        )


    db.commit()
    db.refresh(appointment)

    return RescheduleAppointmentResponse(
        patient_name=appointment.patient_name,
        new_start_time=appointment.start_time
    )

# Find Patient by Phone number
@app.get("/find_patient/{phone_number}")
def find_patient(phone_number: str, db: Session = Depends(get_db)):

    patient = find_patient_by_phone(phone_number, db)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return {
        "id": patient.id,
        "name": patient.name,
        "age": patient.age,
        "phone_number": patient.phone_number
    }

import uvicorn
if __name__ == "__main__":
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)


# Step 5: StreamLit dashboard testing(just for testing)
