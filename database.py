import os
import datetime as dt

from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Use Railway PostgreSQL if available, otherwise use SQLite locally
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./appointments_db.db")

# Railway uses postgres://, SQLAlchemy expects postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread, PostgreSQL does not
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)

    reason = Column(String, nullable=True)

    doctor = Column(String, nullable=True)   # NEW

    start_time = Column(DateTime, index=True)

    canceled = Column(Boolean, default=False)

    google_event_id = Column(String, nullable=True)

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

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done!")


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()