"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: services/google_calendar_service.py
Description: Integration service for Google Calendar API. Handles OAuth2 
             authentication, event retrieval, and event creation to keep the
             user synchronized with their schedule.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import os.path
import datetime
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sentinel.core.events import Events

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    """
    Service layer for interacting with Google Calendar.
    
    Manages the persistent token lifecycle and provides high-level methods
    for skill modules to query and modify the user's calendar.
    """
    
    def __init__(self, credentials_path: str, token_path: str) -> None:
        """
        Initializes the service with file paths for secrets.
        
        Args:
            credentials_path: Path to the credentials.json from Google Console.
            token_path: Path where the authorized user token will be stored.
        """
        self.creds_path = credentials_path
        self.token_path = token_path
        self.service: Optional[Any] = None

    def authenticate(self) -> bool:
        """
        Handles the OAuth2 flow. Attempts to load cached tokens or initiates 
        a local server flow for user login.
        
        Returns:
            bool: True if authentication was successful.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.creds_path):
                    Events.emit(Events.ERROR_OCCURRED, message="Google Calendar credentials missing in config.")
                    return False
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            Events.emit(Events.ERROR_OCCURRED, message=f"Calendar Build Error: {e}")
            return False

    def get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves the next set of events from the primary calendar.
        
        Returns:
            List[Dict]: A list of event resource dictionaries.
        """
        if not self.service: 
            return []
            
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId='primary', 
            timeMin=now,
            maxResults=max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])

    def create_event(self, 
                     summary: str, 
                     start_time: datetime.datetime, 
                     end_time: Optional[datetime.datetime] = None, 
                     description: str = "") -> Dict[str, Any]:
        """
        Creates a new event on the user's primary calendar.
        
        Args:
            summary: Title of the event.
            start_time: Datetime object for start.
            end_time: Datetime object for end. Defaults to start + 1 hour.
            description: Optional body text for the event.
        """
        if not self.service: 
            raise ConnectionError("Calendar service not authenticated.")
            
        if not end_time:
            end_time = start_time + datetime.timedelta(hours=1)
            
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time.isoformat() + 'Z'},
            'end': {'dateTime': end_time.isoformat() + 'Z'},
        }
        
        return self.service.events().insert(calendarId='primary', body=event).execute()
