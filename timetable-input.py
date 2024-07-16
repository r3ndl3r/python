import os
import pickle
import sys
import datetime
import re
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Global variables
TIMEZONE = 'Australia/Melbourne'
SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PICKLE_PATH = 'token.pickle'
CREDENTIALS_JSON_PATH = 'credentials.json'

# URL for obtaining Google API credentials
GOOGLE_API_CREDENTIALS_URL = 'https://developers.google.com/docs/api/quickstart/python'

logging.basicConfig(level=logging.WARNING)  # Set logging level to WARNING by default

def authenticate_google():
    creds = None

    if os.path.exists(TOKEN_PICKLE_PATH):
        with open(TOKEN_PICKLE_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_JSON_PATH):
                logging.error(f"Credentials file '{CREDENTIALS_JSON_PATH}' not found.")
                logging.info(f"Please download credentials.json from {GOOGLE_API_CREDENTIALS_URL}")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_JSON_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PICKLE_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def parse_schedule(input_data):
    schedule = []
    day_map = {"Mo": "Monday", "Tu": "Tuesday", "We": "Wednesday", "Th": "Thursday", "Fr": "Friday"}

    pattern = re.compile(r'^(Mo|Tu|We|Th|Fr) (\d{1,2}/\d{1,2}): (\d{2}:\d{2})->(\d{2}:\d{2})$')

    for line in input_data.strip().splitlines():
        line = line.strip()
        if "NO REPLY" in line:
            break
        elif pattern.match(line):
            try:
                match = pattern.match(line)
                day = match.group(1)
                date_str = match.group(2)
                start_time = match.group(3)
                end_time = match.group(4)

                # Parse date and time
                date_obj = datetime.datetime.strptime(date_str, '%d/%m')
                current_year = datetime.datetime.now().year
                start_datetime = datetime.datetime.combine(date_obj.replace(year=current_year),
                                                           datetime.datetime.strptime(start_time, '%H:%M').time())
                end_datetime = datetime.datetime.combine(date_obj.replace(year=current_year),
                                                         datetime.datetime.strptime(end_time, '%H:%M').time())

                # Adjust for day of the week
                day_of_week = day_map[day]
                while start_datetime.weekday() != list(day_map.keys()).index(day):
                    start_datetime += datetime.timedelta(days=1)
                    end_datetime += datetime.timedelta(days=1)

                schedule.append((day_of_week, start_datetime, end_datetime))
            except Exception as e:
                logging.error(f"Failed to parse line: {line}. Error: {e}")

    return schedule

def delete_existing_work_events(service, calendar_id, date):
    start_datetime = datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z'
    end_datetime = datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z'

    try:
        events_result = service.events().list(calendarId=calendar_id,
                                              timeMin=start_datetime,
                                              timeMax=end_datetime,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        for event in events:
            if event.get('summary') == 'Work':
                try:
                    service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
                except HttpError as err:
                    logging.error(f"HTTP error occurred while deleting event: {event.get('summary')} at {event['start'].get('dateTime')}. Error: {err.content}")
                except Exception as e:
                    logging.error(f"Failed to delete event: {event.get('summary')} at {event['start'].get('dateTime')}. Error: {e}")

    except HttpError as err:
        logging.error(f"HTTP error occurred while querying events: {err.content}")
    except Exception as e:
        logging.error(f"Failed to query events for {date}. Error: {e}")

def create_event(service, calendar_id, day, start_datetime, end_datetime):
    event = {
        'summary': 'Work',
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': TIMEZONE,
        },
    }
    try:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"-> {day}, {start_datetime.strftime('%Y-%m-%d %H:%M')} to {end_datetime.strftime('%H:%M')}")
    except HttpError as err:
        logging.error(f"HTTP error occurred while creating event: {err.content}")

def main():
    creds = authenticate_google()

    if not creds:
        return

    calendar_service = build('calendar', 'v3', credentials=creds)

    print("Paste your schedule:")
    input_data = ""
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        input_data += line + "\n"
        if "NO REPLY" in line:
            print("Detected 'NO REPLY'. Stopping further input processing.")
            break

    print(f"Input data received:\n{input_data}")

    schedule = parse_schedule(input_data)
    print(f"\nParsed schedule: {schedule}\n")

    if not schedule:
        print("No valid schedule data found.")
        return

    calendar_id = 'primary'

    for day, start_datetime, end_datetime in schedule:
        delete_existing_work_events(calendar_service, calendar_id, start_datetime.date())
        create_event(calendar_service, calendar_id, day, start_datetime, end_datetime)

if __name__ == '__main__':
    main()
