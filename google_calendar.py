

from __future__ import print_function

import datetime as dt
import os.path

from config import (
    GOOGLE_CALENDAR_SCOPES,
    GOOGLE_TIMEZONE,
    APPOINTMENT_DURATION_MINUTES,
)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# authentication of google calender

def authenticate_google_calendar():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            GOOGLE_CALENDAR_SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                GOOGLE_CALENDAR_SCOPES
            )

            creds = flow.run_local_server(
                port=8080,
                open_browser=True
            )

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    return service


#create calender event
def create_calendar_event(
    patient_name: str,
    doctor: str,
    reason: str,
    start_datetime: dt.datetime
):
    service = authenticate_google_calendar()

    end_datetime = start_datetime + dt.timedelta(minutes=30)

    event = {
        "summary": f"Appointment - {patient_name}",
        "description": (
            f"Doctor: {doctor}\n"
            f"Reason: {reason}"
        ),
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return event


#delete calender event
def delete_calendar_event(event_id: str):
    service = authenticate_google_calendar()

    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()


#update calender event (reschedule)
def update_calendar_event(
    event_id: str,
    patient_name: str,
    doctor: str,
    reason: str,
    start_datetime: dt.datetime
):
    service = authenticate_google_calendar()

    end_datetime = start_datetime + dt.timedelta(
    minutes=APPOINTMENT_DURATION_MINUTES
    )

    event = {
        "summary": f"Appointment - {patient_name}",
        "description": (
            f"Doctor: {doctor}\n"
            f"Reason: {reason}"
        ),
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": GOOGLE_TIMEZONE,
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": GOOGLE_TIMEZONE,
        },
    }

    service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=event
    ).execute()