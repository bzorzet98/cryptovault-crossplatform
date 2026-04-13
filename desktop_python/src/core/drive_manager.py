import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

class DriveManager:
    """
    Handles authentication and file operations with Google Drive API.
    """
    # Scope: Access only to files created or opened by this app.
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        """
        Handles the OAuth2 flow. Returns an authorized Drive API service.
        """
        creds = None
        # The token.json stores the user's access and refresh tokens.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        return build('drive', 'v3', credentials=creds)

    def upload_vault(self, file_path, folder_id=None):
        """
        Uploads or updates the vault file in Google Drive.
        """
        file_metadata = {'name': os.path.basename(file_path)}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)
        
        # First, check if the file already exists to update it instead of creating a duplicate
        query = f"name = '{file_metadata['name']}' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])

        if files:
            file_id = files[0]['id']
            updated_file = self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            return updated_file.get('id')
        else:
            new_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            return new_file.get('id')