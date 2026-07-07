# Step 1: Import Database Objects

from database import init_db, Appointment, Doctor, Patient, get_db

init_db()

# step 3: Create Data Contracts using Pydantic models
import datetime as dt 
from pydantic import BaseModel

class AppointmentRequest(BaseModel):
    patient_name: str
    doctor: str
    reason: str
    appointment_date: str
    appointment_time: str


class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    doctor: str
    reason: str
    start_time: dt.datetime
    canceled: bool
    created_at: dt.datetime

class CancelAppointmentRequest(BaseModel):
    patient_name: str
    date: dt.date


class CancelAppointmentResponse(BaseModel):
    patient_name: str
    canceled_count: int

class ListAppointmentRequest(BaseModel):
    date: dt.date

class RecommendDoctorRequest(BaseModel):
    symptoms: str

class RescheduleAppointmentRequest(BaseModel):
    patient_name: str
    old_date: str
    new_date: str
    new_time: str


class RescheduleAppointmentResponse(BaseModel):
    patient_name: str
    new_start_time: dt.datetime



class RecommendDoctorResponse(BaseModel):
    department: str
    doctor_name: str
    experience: int

SYMPTOM_TO_DEPARTMENT = {
    "fever": "General Medicine",
    "cold": "ENT",
    "cough": "General Medicine",
    "sore throat": "ENT",
    "ear pain": "ENT",
    "skin rash": "Dermatology",
    "acne": "Dermatology",
    "back pain": "Orthopedics",
    "joint pain": "Orthopedics",
    "chest pain": "Cardiology",
    "heart pain": "Cardiology",
    "headache": "Neurology",
    "migraine": "Neurology",
    "child fever": "Pediatrics",
    "pregnancy": "Gynecology"
}

def parse_natural_date(date_text: str):

    date_text = date_text.lower()

    today = dt.date.today()

    if date_text == "today":
        return today

    elif date_text == "tomorrow":
        return today + dt.timedelta(days=1)

    else:
        return dt.datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

def parse_natural_time(time_text: str):

    try:
        return dt.datetime.strptime(
            time_text,
            "%I %p"
        ).time()

    except ValueError:
        return dt.datetime.strptime(
            time_text,
            "%I:%M %p"
        ).time()

def find_patient_by_phone(phone_number: str, db: Session):

    patient = (
        db.query(Patient)
        .filter(Patient.phone_number == phone_number)
        .first()
    )

    return patient

def recommend_doctor(reason: str, db: Session):
    reason = reason.lower()

    department = None

    for symptom, dept in SYMPTOM_TO_DEPARTMENT.items():
        if symptom in reason:
            department = dept
            break

    if not department:
        return None

    doctor = (
        db.query(Doctor)
        .filter(
            Doctor.department == department,
            Doctor.available == True
        )
        .order_by(Doctor.experience.desc())
        .first()
    )

    return doctor
# Step 2: Create FastAPI application and endpoints pseudoo code

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

app = FastAPI()

# Schedule Appointments
@app.post("/schedule_appointment/")
def schedule_appointment(
    request: AppointmentRequest,
    db: Session = Depends(get_db)
):
   # Parse date
    actual_date = parse_natural_date(request.appointment_date)

# Parse time
    appointment_time = parse_natural_time(request.appointment_time)


    # Combine date and time
    start_datetime = dt.datetime.combine(
        actual_date,
        appointment_time
    )

    # Save appointment
    new_appointment = Appointment(
        patient_name=request.patient_name,
        doctor=request.doctor,
        reason=request.reason,
        start_time=start_datetime,
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return AppointmentResponse(
        id=new_appointment.id,
        patient_name=new_appointment.patient_name,
        doctor=new_appointment.doctor,
        reason=new_appointment.reason,
        start_time=new_appointment.start_time,
        canceled=new_appointment.canceled,
        created_at=new_appointment.created_at,
    )
    

# Cancel Appointments
from sqlalchemy import select

@app.post("/cancel_appointment/")
def cancel_appointment(
    request: CancelAppointmentRequest,
    db: Session = Depends(get_db)
):

    start_dt = dt.datetime.combine(request.date, dt.time.min)
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
        appointment.canceled = True

    db.commit()

    return CancelAppointmentResponse(
        patient_name=request.patient_name,
        canceled_count=len(appointments)
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
