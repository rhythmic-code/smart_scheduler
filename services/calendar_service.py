# # services/calendar_service.py
# import os
# from datetime import datetime, time, timedelta
# from dateutil import parser as date_parser
# from dateutil.tz import gettz
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from config import CALENDAR_TIMEZONE, WORKING_HOURS, SLOT_INTERVAL, SCOPES, GCAL_CREDS_PATH, GCAL_TOKEN_PATH

# def get_calendar_service():
#     """Authenticate and return Google Calendar service"""
#     creds = None
#     if os.path.exists(GCAL_TOKEN_PATH):
#         creds = Credentials.from_authorized_user_file(GCAL_TOKEN_PATH, SCOPES)
    
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(GCAL_CREDS_PATH, SCOPES)
#             creds = flow.run_local_server(port=0)
        
#         with open(GCAL_TOKEN_PATH, 'w') as token:
#             token.write(creds.to_json())
    
#     return build('calendar', 'v3', credentials=creds)

# def get_upcoming_events(days_ahead=30):
#     """Get upcoming events from Google Calendar"""
#     service = get_calendar_service()
#     tz = gettz(CALENDAR_TIMEZONE)
#     now = datetime.now(tz).isoformat()  # Use local timezone
#     later = (datetime.now(tz) + timedelta(days=days_ahead)).isoformat()
    
#     events_result = service.events().list(
#         calendarId='primary', 
#         timeMin=now, 
#         timeMax=later,
#         singleEvents=True,
#         orderBy='startTime'
#     ).execute()
#     return events_result.get('items', [])

# def create_event(summary, start_iso, end_iso):
#     """Create a new calendar event"""
#     service = get_calendar_service()
#     event = {
#         'summary': summary,
#         'start': {'dateTime': start_iso, 'timeZone': CALENDAR_TIMEZONE},
#         'end': {'dateTime': end_iso, 'timeZone': CALENDAR_TIMEZONE},
#     }
#     created_event = service.events().insert(calendarId='primary', body=event).execute()
#     return created_event.get('htmlLink')

# def find_available_slots(duration_minutes, preferred_date=None, preferred_time_range=None):
#     """Find available time slots in calendar"""
#     tz = gettz(CALENDAR_TIMEZONE)
#     events = get_upcoming_events(7)
#     slots = []
    
#     # Determine dates to check
#     dates_to_check = [preferred_date] if preferred_date else [
#         (datetime.now(tz) + timedelta(days=i)).date() for i in range(7)
#     ]
    
#     for date_obj in dates_to_check:
#         # Set time boundaries in local timezone
#         work_start = datetime.combine(date_obj, time(WORKING_HOURS[0], 0), tzinfo=tz)
#         work_end = datetime.combine(date_obj, time(WORKING_HOURS[1], 0), tzinfo=tz)
        
#         # Get ALL events overlapping this day
#         busy_slots = []
#         for event in events:
#             # Parse with timezone awareness
#             start = event['start'].get('dateTime', event['start'].get('date'))
#             end = event['end'].get('dateTime', event['end'].get('date'))
            
#             event_start = date_parser.parse(start).astimezone(tz)
#             event_end = date_parser.parse(end).astimezone(tz)
            
#             # Check for day overlap
#             if (event_start.date() <= date_obj <= event_end.date()) or \
#                (event_start.date() == date_obj) or \
#                (event_end.date() == date_obj):
#                 busy_slots.append((event_start, event_end))
        
#         # Generate slots within working hours
#         current_time = work_start
#         while current_time <= work_end - timedelta(minutes=duration_minutes):
#             slot_end = current_time + timedelta(minutes=duration_minutes)
            
#             # Skip if slot ends after working hours
#             if slot_end > work_end:
#                 current_time += timedelta(minutes=SLOT_INTERVAL)
#                 continue
            
#             # Check for event conflicts
#             conflict = any(
#                 current_time < busy_end and slot_end > busy_start
#                 for busy_start, busy_end in busy_slots
#             )
            
#             if not conflict:
#                 # Apply time range filtering
#                 if preferred_time_range:
#                     hour = current_time.hour
#                     if (preferred_time_range == "morning" and 6 <= hour < 12) or \
#                        (preferred_time_range == "afternoon" and 12 <= hour < 17) or \
#                        (preferred_time_range == "evening" and 17 <= hour < 21):
#                         slots.append(current_time)
#                 else:
#                     slots.append(current_time)
            
#             current_time += timedelta(minutes=SLOT_INTERVAL)
    
#     return slots

import os
from datetime import datetime, time, timedelta
from dateutil import parser as date_parser
from dateutil.tz import gettz
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from config import CALENDAR_TIMEZONE, WORKING_HOURS, SLOT_INTERVAL, SCOPES, GCAL_CREDS_PATH, GCAL_TOKEN_PATH

# Cache for events to prevent multiple API calls
EVENT_CACHE = {"last_fetched": None, "events": []}

def get_calendar_service():
    """Authenticate with Google Calendar API"""
    creds = None
    if os.path.exists(GCAL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GCAL_TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GCAL_CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(GCAL_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def get_upcoming_events(days_ahead=7, force_refresh=False):
    """Get events with caching to prevent double-booking"""
    global EVENT_CACHE
    
    # Return cached events if recent and not forced to refresh
    if not force_refresh and EVENT_CACHE["last_fetched"] and \
       (datetime.now() - EVENT_CACHE["last_fetched"]).seconds < 30:
        return EVENT_CACHE["events"]
    
    service = get_calendar_service()
    tz = gettz(CALENDAR_TIMEZONE)
    now = datetime.now(tz).isoformat()
    later = (datetime.now(tz) + timedelta(days=days_ahead)).isoformat()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=later,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # Update cache
    EVENT_CACHE = {
        "last_fetched": datetime.now(),
        "events": events
    }
    
    return events

def create_event(summary, start_iso, end_iso, timezone=CALENDAR_TIMEZONE):
    """Create new calendar event and refresh cache"""
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start_iso, 'timeZone': timezone},
        'end': {'dateTime': end_iso, 'timeZone': timezone},
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    
    # Force refresh of event cache
    get_upcoming_events(force_refresh=True)
    
    return created_event.get('htmlLink')

def find_available_slots(duration_minutes, days_ahead=7, preferred_date=None, preferred_time_range=None):
    """Find available time slots with date/time preferences and double-booking prevention"""
    tz = gettz(CALENDAR_TIMEZONE)
    events = get_upcoming_events(days_ahead)
    slots = []
    
    # Determine dates to check
    if preferred_date:
        dates_to_check = [preferred_date]
    else:
        dates_to_check = [
            (datetime.now(tz) + timedelta(days=day)).date() 
            for day in range(days_ahead)
        ]
    
    # Determine time range based on preference
    if preferred_time_range == "morning":
        time_range = (6, 12)
    elif preferred_time_range == "afternoon":
        time_range = (12, 17)
    elif preferred_time_range == "evening":
        time_range = (17, 21)
    else:
        time_range = None
    
    for date_obj in dates_to_check:
        # Create datetime objects for work hours
        work_start = datetime.combine(date_obj, time(WORKING_HOURS[0], 0), tzinfo=tz)
        work_end = datetime.combine(date_obj, time(WORKING_HOURS[1], 0), tzinfo=tz)
        
        # Adjust for preferred time range
        if time_range:
            work_start = max(work_start, work_start.replace(hour=time_range[0]))
            work_end = min(work_end, work_end.replace(hour=time_range[1]))

        # Collect busy slots
        busy_slots = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            event_start = date_parser.parse(start).astimezone(tz)
            event_end = date_parser.parse(end).astimezone(tz)
            
            # Check date overlap
            if event_start.date() <= date_obj <= event_end.date():
                busy_slots.append((event_start, event_end))

        # Generate available slots
        current_time = work_start
        while current_time <= work_end - timedelta(minutes=duration_minutes):
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Skip if beyond work hours
            if slot_end > work_end:
                current_time += timedelta(minutes=SLOT_INTERVAL)
                continue
            
            # Check for conflicts
            conflict = any(
                current_time < busy_end and slot_end > busy_start
                for busy_start, busy_end in busy_slots
            )
            
            if not conflict:
                slots.append(current_time)
            
            current_time += timedelta(minutes=SLOT_INTERVAL)
    
    return slots