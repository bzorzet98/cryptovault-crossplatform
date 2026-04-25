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
    
    def __init__(self, credentials_path, token_path):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None  # Inicializamos en None, no creamos el servicio todavía

    def authenticate(self):
        """Este método es el único que debe disparar el navegador si es necesario."""
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import os

        creds = None
        # Solo intenta cargar si el archivo existe
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, 
                                                        ['https://www.googleapis.com/auth/drive.file'])

        # Si no hay credenciales válidas, las pedimos (AQUÍ se abre el navegador)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, ['https://www.googleapis.com/auth/drive.file'])
                creds = flow.run_local_server(port=0)
            
            # Guardamos el token para la próxima vez
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        # CAMBIO AQUÍ: Guardamos el servicio en la clase y luego lo retornamos
        self.service = build('drive', 'v3', credentials=creds)
        return self.service

    def upload_vault(self, file_path, folder_id=None):
        # 1. ¡DESPERTAR AL SERVICIO SI ESTÁ DORMIDO!
        if not self.service:
            self.authenticate()
            
        # 2. A partir de aquí sigue tu código normal
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)
        
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
    
    def find_file(self, filename):
        """Busca un archivo por nombre y devuelve su ID."""
        service = self.service
        query = f"name = '{filename}' and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None

    def download_file(self, file_id, local_path):
        """Descarga un archivo de Drive al disco local."""
        service = self.service
        request = service.files().get_media(fileId=file_id)
        with open(local_path, "wb") as f:
            f.write(request.execute())