import os
import io
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from django.conf import settings

SCOPES = "https://www.googleapis.com/auth/drive.file"
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
static_dir = os.path.join(base_dir, 'sliceT1app/static')
media_dir = os.path.join(base_dir, 'media')
CLIENT_SECRET_FILE = os.path.join(static_dir,"json/credentials.json")

class Auth:
    def __init__(self):
        self.client_secret = CLIENT_SECRET_FILE
        self.scopes = SCOPES
        self.creds = None

    def get_credentials(self):
        """
        For getting the credentials (say accessToken) of the user
        """
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secret, self.scopes)
        self.creds = flow.run_local_server(port=8080)
    
    def get_drive_service(self):
        """
        For getting the drive_service instance from 
        the credentials of the user
        """
        self.get_credentials()
        self.drive_service = build('drive', 'v3', credentials=self.creds)
    
    def locally_download_files(self, fileList):
        """
        For locally downloading the files
        """
        self.get_drive_service()

        for file in fileList:
            media_request = self.drive_service.files().get_media(fileId=file['file_id'])
            fh = io.FileIO(os.path.join(media_dir,file['name']), 'wb')
            downloader = MediaIoBaseDownload(fh, media_request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %s, %d%%"%(file['name'],int(status.progress() * 100)))