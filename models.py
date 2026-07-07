
import datetime as dt

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from database import Base





class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)

    reason = Column(String, nullable=True)

    doctor = Column(String, nullable=True)   # NEW

    start_time = Column(DateTime, index=True)

    canceled = Column(Boolean, default=False)

    created_at = Column(DateTime, default=dt.datetime.utcnow)

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)

    doctor_name = Column(String, nullable=False)

    department = Column(String, nullable=False)

    experience = Column(Integer)

    available = Column(Boolean, default=True)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    age = Column(Integer)

    phone_number = Column(String, unique=True, nullable=False)
