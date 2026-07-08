import datetime as dt

from google_calendar import create_calendar_event

create_calendar_event(
    patient_name="Piyush Kumar",
    doctor="Dr Ahmed Sharma",
    reason="Google Calendar Integration Test",
    start_datetime=dt.datetime.now() + dt.timedelta(minutes=5)
)

print("✅ Test event created successfully!")