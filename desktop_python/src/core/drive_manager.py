import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

APP_FOLDER_NAME = "CryptoVault"


class DriveManager:
    """
    Handles Google Drive auth and file operations.
    All vaults are stored inside a dedicated 'CryptoVault' folder in Drive,
    so they are isolated from the user's other files and harder to delete by accident.
    """

    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._folder_id = None  # Cached ID of the CryptoVault folder

    # ------------------------------------------------------------------
    # AUTH
    # ------------------------------------------------------------------
    def is_authenticated(self):
        """Verifica si el servicio ya está listo."""
        return self.service is not None
    
    def authenticate(self):
        """
        Authenticates with Google Drive.
        Opens a browser window only the first time (or if token is invalid).
        """
        if self.is_authenticated():
            return self.service
        
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        return self.service

    def is_authenticated(self) -> bool:
        return self.service is not None

    # ------------------------------------------------------------------
    # APP FOLDER MANAGEMENT
    # ------------------------------------------------------------------

    def _get_or_create_app_folder(self) -> str:
        """
        Returns the Drive folder ID for 'CryptoVault/'.
        Creates the folder if it doesn't exist yet.
        This keeps all vaults in one safe, predictable location.
        """
        if self._folder_id:
            return self._folder_id

        # Search for existing folder
        query = (
            f"name = '{APP_FOLDER_NAME}' "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false"
        )
        results = self.service.files().list(
            q=query, fields="files(id, name)"
        ).execute()
        folders = results.get('files', [])

        if folders:
            self._folder_id = folders[0]['id']
        else:
            # Create it
            metadata = {
                'name': APP_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(
                body=metadata, fields='id'
            ).execute()
            self._folder_id = folder['id']

        return self._folder_id

    # ------------------------------------------------------------------
    # VAULT LISTING
    # ------------------------------------------------------------------

    def list_vaults(self) -> list[dict]:
        """
        Returns a list of all .data vaults inside the CryptoVault/ folder.
        Each item: { 'id': str, 'name': str, 'modifiedTime': str }
        """
        folder_id = self._get_or_create_app_folder()
        query = (
            f"'{folder_id}' in parents "
            f"and name contains '.data' "
            f"and trashed = false"
        )
        results = self.service.files().list(
            q=query,
            fields="files(id, name, modifiedTime, size)",
            orderBy="modifiedTime desc"
        ).execute()
        return results.get('files', [])

    # ------------------------------------------------------------------
    # UPLOAD
    # ------------------------------------------------------------------

    def upload_vault(self, file_path: str) -> str:
        """
        Uploads a vault file into the CryptoVault/ folder.
        If a file with the same name already exists there, it updates it (no duplicates).
        Returns the Drive file ID.
        """
        folder_id = self._get_or_create_app_folder()
        filename = os.path.basename(file_path)
        media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)

        # Check if it already exists in the folder
        query = (
            f"'{folder_id}' in parents "
            f"and name = '{filename}' "
            f"and trashed = false"
        )
        results = self.service.files().list(q=query, fields="files(id)").execute()
        existing = results.get('files', [])

        if existing:
            updated = self.service.files().update(
                fileId=existing[0]['id'],
                media_body=media
            ).execute()
            return updated.get('id')
        else:
            metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            created = self.service.files().create(
                body=metadata,
                media_body=media,
                fields='id'
            ).execute()
            return created.get('id')

    # ------------------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------------------

    def download_vault(self, file_id: str, local_path: str):
        """
        Downloads a vault from Drive by its file ID to a local path.
        """
        request = self.service.files().get_media(fileId=file_id)
        with open(local_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

    # ------------------------------------------------------------------
    # LEGACY HELPERS (kept for compatibility)
    # ------------------------------------------------------------------

    def find_file(self, filename: str) -> str | None:
        """Searches for a file by name anywhere accessible. Returns ID or None."""
        folder_id = self._get_or_create_app_folder()
        query = (
            f"'{folder_id}' in parents "
            f"and name = '{filename}' "
            f"and trashed = false"
        )
        results = self.service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None

    def download_file(self, file_id: str, local_path: str):
        """Alias for download_vault for backward compatibility."""
        self.download_vault(file_id, local_path)