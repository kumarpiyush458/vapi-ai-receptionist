from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///./appointments_db.db",
    connect_args={"check_same_thread": False},
)

with engine.connect():
    print("Connected successfully!")