import io
import logging
import os
import pickle
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from src.core.util import Utils
from src.google_drive.corpora import Corpora
from src.google_drive.file import File

# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive']

logger = logging.getLogger(__name__)


class Drive:
    _creds: Credentials = None
    _service: Resource = None

    def __new__(cls):  # __new__ always a classmethod
        if Drive._service is None:
            Drive._service = Drive._get_service()
        return super(Drive, cls).__new__(cls)

    @staticmethod
    def _get_credential(credentials_path: str = None) -> Credentials:
        if Drive._creds is None:
            if credentials_path is None:
                credentials_path = os.path.join(Utils.get_project_root(), 'credentials.json')
            creds: Credentials or None = None
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            Drive._creds = creds
        return Drive._creds

    @staticmethod
    def _get_service() -> Resource:
        if Drive._service is None:
            Drive._service = build('drive', 'v3', credentials=Drive._get_credential())
        return Drive._service

    @staticmethod
    def file_info(file_id: str) -> File:
        d: Dict[str, str] = Drive._get_service().files().get(fileId=file_id).execute()
        return File(**d)

    @staticmethod
    def list(file_id: str, max_count=10) -> List[File]:
        folder_info: File = Drive.file_info(file_id)
        logger.info(f'Fetching file for {folder_info}')
        page_token: str or None = None
        i = 0
        files = []
        while (i == 0 or page_token is not None) and len(files) < max_count:
            query = f"'{file_id}' in parents"
            response: Dict[str, object] = Drive._get_service().files().list(corpora=Corpora.USER.value, q=query,
                                                                            pageToken=page_token).execute()
            response_files = [File(**file_dict) for file_dict in response.get('files', [])]
            files.extend(response_files[0:max_count - len(files)])
            page_token = response.get('nextPageToken', None)
            i += 1
        logger.info(f'{len(files)} files fetched for {folder_info}')
        return files

    @staticmethod
    def download(file_id: str, target_folder: str, override=False) -> None:
        drive_file: File = Drive.file_info(file_id)
        file = os.path.join(target_folder, drive_file.name)
        if os.path.isfile(file) and not override:
            logger.info(f'Downloading skipped, {file} already exists')
            return
        logger.info(f'Downloading {drive_file} to {file}')
        request = Drive._get_service().files().get_media(fileId=file_id)
        handle = io.FileIO(os.path.join(target_folder, drive_file.name), 'wb')
        downloader = MediaIoBaseDownload(handle, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info(f'Download {int(status.progress() * 100)}%.')
        logger.info(f'Download done for {drive_file}')

    @staticmethod
    def upload(file_id: str, source_file: str) -> None:
        drive_file: File = Drive.file_info(file_id)
        if not os.path.isfile(source_file):
            logger.error(f'Uploading failed: {source_file} not exist')
            return
        logger.info(f'Uploading {source_file} to {drive_file}')
        metadata = {'name': os.path.basename(source_file), 'parents': [file_id]}
        media = MediaFileUpload(source_file)
        d = Drive._get_service().files().create(body=metadata, media_body=media).execute()
        logger.info(f'Uploading done for {File(**d)}')

    @staticmethod
    def rename(file_id: str, new_name: str) -> None:
        drive_file: File = Drive.file_info(file_id)
        logger.info(f'Renaming file for {drive_file} to {new_name}')
        d = Drive._get_service().files().update(fileId=file_id, body={'name': new_name}).execute()
        logger.info(f'Renamed file to {File(**d)}')
