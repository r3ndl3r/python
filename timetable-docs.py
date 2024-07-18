# Head to https://developers.google.com/docs/api/quickstart/python and follow steps:
# Enable the API > Configure OAuth consent > Authorize credentials for a desktop application > Save the downloaded JSON file as credentials.json

# Make sure required python modules are installed:
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import os
import pickle
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
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/calendar']
TOKEN_PICKLE_PATH = 'token.pickle'
CREDENTIALS_JSON_PATH = 'credentials.json'
DOCS_URL_FILE = 'docs.url'
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
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PICKLE_PATH, 'wb') as token:
                pickle.dump(creds, token)
    return creds

def get_docs_url():
    """Get the Google Docs URL from the file or prompt the user if not available."""
    if os.path.exists(DOCS_URL_FILE):
        with open(DOCS_URL_FILE, 'r') as file:
            url = file.read().strip()
        if url:
            return url
    
    # If file doesn't exist or is empty, prompt the user
    url = input("Please enter the Google Docs URL for the timetable: ")
    with open(DOCS_URL_FILE, 'w') as file:
        file.write(url)
    return url

def read_google_doc(doc_id, service):
    document = service.documents().get(documentId=doc_id).execute()
    doc_content = document.get('body').get('content')
    lines = []
    for element in doc_content:
        if 'paragraph' in element:
            elements = element['paragraph']['elements']
            for elem in elements:
                if 'textRun' in elem:
                    lines.append(elem['textRun']['content'])
    return '\n'.join(lines)

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
                
                date_obj = datetime.datetime.strptime(date_str, '%d/%m')
                current_year = datetime.datetime.now().year
                start_datetime = datetime.datetime.combine(date_obj.replace(year=current_year),
                                                           datetime.datetime.strptime(start_time, '%H:%M').time())
                end_datetime = datetime.datetime.combine(date_obj.replace(year=current_year),
                                                         datetime.datetime.strptime(end_time, '%H:%M').time())
                
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
                    logging.error(f"Failed to delete event: {event.get('summary')} at {event.get('start').get('dateTime')}. Error: {e}")
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
        print(f"-> {day}, {start_datetime.strftime('%Y-%m-%d [%H:%M')} -> {end_datetime.strftime('%H:%M')}]")
    except HttpError as err:
        logging.error(f"HTTP error occurred while creating event: {err.content}")

def clear_document(service, document_id):
    """Clear the entire content of the Google Document."""
    try:
        # Get the current content of the document
        document = service.documents().get(documentId=document_id).execute()
        end_index = document['body']['content'][-1]['endIndex'] - 1

        # Clear the content
        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_index
                    }
                }
            }
        ]
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        print("Document content cleared successfully.")
    except HttpError as err:
        logging.error(f"An error occurred while clearing the document: {err}")

def insert_pastehere(service, document_id):
    """Insert 'PASTEHERE' at the beginning of the document."""
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': 'PASTEHERE\n'
            }
        }
    ]
    try:
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        print("'PASTEHERE' inserted successfully.")
    except HttpError as err:
        logging.error(f"An error occurred while inserting 'PASTEHERE': {err}")

def main():
    creds = authenticate_google()
    if not creds:
        return

    docs_service = build('docs', 'v1', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
    
    # Get the Google Docs URL
    docs_url = get_docs_url()
    doc_id = docs_url.split('/')[-2]

    print("Reading schedule from Google Docs...")
    input_data = read_google_doc(doc_id, docs_service)
    schedule = parse_schedule(input_data)

    print(f"\nParsed schedule: {schedule}\n")
    if not schedule:
        print("No valid schedule data found.")
        return

    calendar_id = 'primary'
    for day, start_datetime, end_datetime in schedule:
        delete_existing_work_events(calendar_service, calendar_id, start_datetime.date())
        create_event(calendar_service, calendar_id, day, start_datetime, end_datetime)

    # Clear the entire document
    clear_document(docs_service, doc_id)

    # Insert 'PASTEHERE' at the beginning of the document
    insert_pastehere(docs_service, doc_id)

if __name__ == '__main__':
    main()
