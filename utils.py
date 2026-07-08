import datetime as dt

from sqlalchemy.orm import Session

from database import Appointment

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
    
def get_next_slot(current_time: dt.datetime):
    return current_time + dt.timedelta(minutes=30)


def is_slot_available(
    doctor: str,
    slot: dt.datetime,
    db: Session
):
    existing = (
        db.query(Appointment)
        .filter(
            Appointment.doctor == doctor,
            Appointment.start_time == slot,
            Appointment.canceled == False
        )
        .first()
    )

    return existing is None


def find_next_available_slot(
    doctor: str,
    requested_slot: dt.datetime,
    db: Session
):
    current_slot = requested_slot

    while not is_slot_available(
        doctor,
        current_slot,
        db
    ):
        current_slot = get_next_slot(current_slot)

    return current_slot