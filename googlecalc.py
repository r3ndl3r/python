import datetime
import re
import sys
import os.path
import pickle

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

def parse_schedule(input_data):
    schedule = []
    day_map = {"Mo": "Monday", "Tu": "Tuesday", "We": "Wednesday", "Th": "Thursday", "Fr": "Friday"}
    
    pattern = re.compile(r'^(Mo|Tu|We|Th|Fr) (\d{1,2}/\d{1,2}): (\d{2}:\d{2})->(\d{2}:\d{2})$')
    
    lines = input_data.strip().split('\n')
    for line in lines:
        line = line.strip()
        if "NO REPLY" in line:
            break
        elif pattern.match(line):
            try:
                print(f"Parsing line: {line}")
                match = pattern.match(line)
                day = match.group(1)
                date_str = match.group(2)
                start_time = match.group(3)
                end_time = match.group(4)
                
                # Parse date and time
                date_obj = datetime.datetime.strptime(date_str, '%d/%m')
                current_year = datetime.datetime.now().year
                start_datetime = datetime.datetime.combine(date_obj.replace(year=current_year), datetime.datetime.strptime(start_time, '%H:%M').time())
                end_datetime = datetime.datetime.combine(date_obj.replace(year=current_year), datetime.datetime.strptime(end_time, '%H:%M').time())
                
                # Adjust for day of the week
                day_of_week = day_map[day]
                while start_datetime.weekday() != list(day_map.keys()).index(day):
                    start_datetime += datetime.timedelta(days=1)
                    end_datetime += datetime.timedelta(days=1)
                
                schedule.append((start_datetime, end_datetime))
            except Exception as e:
                print(f"Failed to parse line: {line}. Error: {e}")
        else:
            print(f"Skipping line: {line}. Does not match expected format.")
    return schedule

def event_exists(service, calendar_id, start_time, end_time):
    events_result = service.events().list(calendarId=calendar_id, timeMin=start_time.isoformat() + 'Z',
                                          timeMax=end_time.isoformat() + 'Z', singleEvents=True, 
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(f"Checking if event exists between {start_time} and {end_time}: {len(events) > 0}")
    return len(events) > 0

def create_event(service, calendar_id, start_datetime, end_datetime):
    event = {
        'summary': 'Work',
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'UTC',
        },
    }
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def main():
    print("Paste your schedule:")
    input_data = sys.stdin.read()
    print(f"Input data received:\n{input_data}")
    
    # Split input into lines and process each line
    lines = input_data.strip().split('\n')
    for line in lines:
        line = line.strip()
        
        if "NO REPLY" in line:
            print("Detected 'NO REPLY'. Stopping further input processing.")
            break
        
        # Process valid schedule lines
        schedule = parse_schedule(line)
        print(f"\nParsed schedule: {schedule}")
        
        if not schedule:
            print("No valid schedule data found.")
            continue

        calendar_id = 'primary'

        service = authenticate_google()

        for start_datetime, end_datetime in schedule:
            if not event_exists(service, calendar_id, start_datetime, end_datetime):
                create_event(service, calendar_id, start_datetime, end_datetime)
            else:
                print(f"Event already exists for {start_datetime}")

if __name__ == '__main__':
    main()
