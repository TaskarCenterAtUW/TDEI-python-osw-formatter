import os
import gc
import time
import shutil
import logging
import zipfile
import asyncio
import traceback
from .config import Settings
from osm_osw_reformatter import Formatter
import uuid
import urllib.parse
import wget

logging.basicConfig()
logger = logging.getLogger('osw-formatter')
logger.setLevel(logging.INFO)

AVAILABLE_EXTENSIONS = ['.zip', '.pbf', '.xml', '.osm']


async def async_format(formatter):
    return await formatter.osm2osw()


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
        start_time = time.time()
        root, ext = os.path.splitext(self.file_relative_path)
        if ext and ext.lower() in AVAILABLE_EXTENSIONS:
            downloaded_file_path = self.download_single_file(self.file_path)
            if downloaded_file_path is None:
                logger.error(f' Failed to download file from path: {self.file_path}')
                raise Exception('Failed to download file')

            # get the parent folder for downloaded_file_path
            unique_download_path = os.path.dirname(downloaded_file_path)
            try:
                logger.info(f' Downloaded file path: {unique_download_path}')
                formatter = Formatter(workdir=unique_download_path, file_path=downloaded_file_path, prefix=self.prefix)
                if ext.lower() == '.zip':
                    formatter_response = formatter.osw2osm()
                else:
                    formatter_response = asyncio.run(asyncio.wait_for(async_format(formatter), timeout=60 * 60))
                end_time = time.time()
                logger.info(f' Time taken to format: {end_time - start_time}')
                return formatter_response
            except Exception as err:
                traceback.print_exc()
                logger.error(f' Error While Formatting File: {str(err)}')
                raise err
        else:
            logger.error(f' Failed to format because unknown file format')
            raise Exception('Unknown file format')

    def download_single_file(self, file_upload_path=None) -> str:
        logger.info(f' Downloading file from path: {file_upload_path}')
        start_time = time.time()
        # file = self.storage_client.get_file_from_url(self.container_name, file_upload_path)
        file_relative_path = self.get_relative_path(file_upload_path)
        file_sas_url = self.storage_client.get_sas_url(container_name=self.container_name, file_path= file_relative_path,expiry_hours=1)
        # file_download_url = self.storage_client.get_sas_url(self.container_name, file_upload_path)
        logger.info(f' File SAS URL: {file_sas_url}')
        try:
            if file_sas_url:
                file_path = os.path.basename(file_upload_path)
                unique_id = self.get_unique_id()
                unique_directory = os.path.join(self.download_dir, unique_id)
                if not os.path.exists(unique_directory):
                    os.makedirs(unique_directory)
                local_download_path = os.path.join(unique_directory, file_path)
                
                # download file using wget
                wget.download(file_sas_url, local_download_path)
                # with open(local_download_path, 'wb') as blob:
                    # blob.write(file.get_stream())

                logger.info(f' File downloaded to location: {local_download_path}')
                end_time = time.time()
                logger.info(f' Time taken to download: {end_time - start_time}')
                return local_download_path
            else:
                logger.info(' Could not get SAS url for file!')
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
    
    
    def get_relative_path(self,full_path:str)-> str|None:
        """
        Get the relative path from a full path
        """
        try:
            # get the result after the first slash
            full_url = urllib.parse.urlparse(full_path)
            url_base_path = full_url.path
            # get the result after the first slash
            relative_path = url_base_path.split('/')[2:]
            # join parts by `/`
            relative_path = '/'.join(relative_path)
            return relative_path
        except Exception as e:
            logger.error(f"Error while getting relative path: {str(e)}")
            return None

    @staticmethod
    def clean_up(path, download_dir=None):
        if os.path.isfile(path):
            logger.info(f' Removing File: {path}')
            os.remove(path)
        else:
            logger.info(f' Removing Folder: {path}')
            shutil.rmtree(path, ignore_errors=True)
        gc.collect()

    def create_zip(self, files):
        zip_filename = os.path.join(self.download_dir, f'{self.prefix}.zip')
        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            for file in files:
                # Add each file to the zip file
                zip_file.write(file, os.path.basename(file))

        for file in files:
            os.remove(file)
        return zip_filename

    def get_unique_id(self) -> str:
        return uuid.uuid1().hex[0:24]
