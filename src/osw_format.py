import os
import shutil
import logging
import traceback
from pathlib import Path
from .config import Settings
from osm_osw_reformatter import Formatter

logging.basicConfig()
logger = logging.getLogger('osw-formatter')
logger.setLevel(logging.INFO)


class OSWFormat:
    def __init__(self, file_path=None, storage_client=None, prefix=None):
        settings = Settings()
        self.download_dir = settings.get_download_directory()
        is_exists = os.path.exists(self.download_dir)
        if not is_exists:
            os.makedirs(self.download_dir)

        self.container_name = settings.event_bus.container_name
        self.storage_client = storage_client
        self.file_path = file_path
        self.file_relative_path = file_path.split('/')[-1]
        self.client = self.storage_client.get_container(container_name=self.container_name)
        self.prefix = prefix

    def format(self):
        root, ext = os.path.splitext(self.file_relative_path)
        print(self.file_path)
        if ext and ext.lower() == '.zip':
            downloaded_file_path = self.download_single_file(self.file_path)

            try:
                logger.info(f' Downloaded file path: {downloaded_file_path}')
                formatter = Formatter(workdir=self.download_dir, file_path=downloaded_file_path, prefix=self.prefix)
                formatter_response = formatter.osw2osm()
                OSWFormat.clean_up(downloaded_file_path, self.download_dir)
                return formatter_response
            except Exception as err:
                traceback.print_exc()
                logger.error(f' Error While Formatting File: {str(err)}')
                return None
        else:
            logger.error(f' Failed to format because unknown file format')
            return None

    def download_single_file(self, file_upload_path=None) -> str:

        file = self.storage_client.get_file_from_url(self.container_name, file_upload_path)
        try:
            if file.file_path:
                file_path = os.path.basename(file.file_path)
                with open(f'{self.download_dir}/{file_path}', 'wb') as blob:
                    blob.write(file.get_stream())
                logger.info(f' File downloaded to location: {self.download_dir}/{file_path}')
                return f'{self.download_dir}/{file_path}'
            else:
                logger.info(' File not found!')
        except Exception as e:
            traceback.print_exc()
            logger.error(e)

    @staticmethod
    def clean_up(path, download_dir=None):
        if os.path.isfile(path):
            logger.info(f' Removing File: {path}')
            os.remove(path)
        else:
            folder = os.path.join(download_dir, path)
            logger.info(f' Removing Folder: {folder}')
            shutil.rmtree(folder, ignore_errors=True)
