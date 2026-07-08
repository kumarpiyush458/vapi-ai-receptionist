
from sqlalchemy.orm import Session

from database import Doctor, Patient
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