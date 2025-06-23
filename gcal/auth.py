# gcal/auth.py
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from config import SCOPES, GCAL_CREDS_PATH, GCAL_TOKEN_PATH

def get_google_credentials():
    """Authenticate and return Google credentials"""
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
    
    return creds