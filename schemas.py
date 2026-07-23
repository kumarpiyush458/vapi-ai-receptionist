from pydantic import BaseModel, EmailStr
import datetime as dt 

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
    date: str


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

class DemoRequestCreate(BaseModel):
    full_name: str
    email: EmailStr
    organization_name: str
    phone: str
    message: str | None = None


class DemoRequestResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    organization_name: str
    phone: str
    message: str | None = None
    created_at: dt.datetime

    model_config = {
        "from_attributes": True
    }