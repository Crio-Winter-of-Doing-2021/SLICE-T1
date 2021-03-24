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

    def check_name(self, file):
        file_name = file['name']
        last_dot_ind = -1
        for i in range(len(file_name)-1,-1,-1):
            if(file_name[i]=="."):
                last_dot_ind = i
                break
        if(os.path.exists(os.path.join(media_dir, file_name))):
            file_name = file_name[:last_dot_ind] + "_" + file["file_id"] + file_name[last_dot_ind:]
            file["name"] = file_name

    def locally_download_files(self, fileList,dm=False):
        """
        For locally downloading the files
        """
        self.get_drive_service()

        for file in fileList:
            if dm==True:
                media_request = self.drive_service.files().get(fileId=file['file_id'])
            else:
                media_request = self.drive_service.files().get_media(fileId=file['file_id'])
            print(media_request)
            self.check_name(file)
            fh = io.FileIO(os.path.join(media_dir, file['name']), 'wb')
            downloader = MediaIoBaseDownload(fh, media_request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %s, %d%%"%(file['name'],int(status.progress() * 100)))
