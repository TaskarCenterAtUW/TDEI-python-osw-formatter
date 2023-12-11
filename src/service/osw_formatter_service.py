import os
import uuid
import logging
import traceback
import threading
import urllib.parse
from pathlib import Path
from datetime import datetime
from src.config import Settings
from python_ms_core import Core
from src.osw_format import OSWFormat
from dataclasses import asdict
from src.models import (
    OSWValidationMessage,
    ValidationResult,
    OSWOnDemandRequest,
    OSWOnDemandResponse,
)
from python_ms_core.core.queue.models.queue_message import QueueMessage

logging.basicConfig()
logger = logging.getLogger("OSW_FORMATTER")
logger.setLevel(logging.INFO)


class OSWFomatterService:
    _settings = Settings()

    def __init__(self):
        core = Core()
        listening_topic_name = self._settings.event_bus.validation_topic or ""
        publishing_topic_name = self._settings.event_bus.formatter_topic or ""
        self.subscription_name = self._settings.event_bus.validation_subscription or ""
        self.listening_topic = core.get_topic(topic_name=listening_topic_name)
        self.publishing_topic = core.get_topic(topic_name=publishing_topic_name)
        self.logger = core.get_logger()
        self.storage_client = core.get_storage_client()
        self.container_name = self._settings.event_bus.container_name
        self.start_listening()
        self.download_dir = self._settings.get_download_directory()
        is_exists = os.path.exists(self.download_dir)
        if not is_exists:
            os.makedirs(self.download_dir)

    def start_listening(self):
        def process(message) -> None:
            if message is not None:
                queue_message = QueueMessage.to_dict(message)
                print(message.messageType)
                messageType = message.messageType
                if messageType == "osw-formatter-request":
                    print("received something")
                    print("Received on demand request")
                    ondemand_request = OSWOnDemandRequest(**queue_message["data"])
                    print(ondemand_request)
                    pthread = threading.Thread(
                        target=self.process_on_demand_format, args=[ondemand_request]
                    )
                    pthread.start()
                    return
                upload_message = OSWValidationMessage.data_from(queue_message)
                # Create a thread to process the message asynchronously
                process_thread = threading.Thread(
                    target=self.format, args=[upload_message]
                )
                process_thread.start()

        self.listening_topic.subscribe(
            subscription=self.subscription_name, callback=process
        )

    def format(self, received_message: OSWValidationMessage):
        tdei_record_id: str = ""
        try:
            tdei_record_id = received_message.data.tdei_record_id

            logger.info(
                f"Received message for: {tdei_record_id} Message received for formatting !"
            )
            if received_message.data.meta.isValid is False:
                error_msg = "Received failed workflow request"
                logger.error(f"{tdei_record_id}, {error_msg} !")
                raise Exception(error_msg)

            if received_message.data.meta.file_upload_path is None:
                error_msg = "Request does not have a valid file path specified."
                logger.error(f"{tdei_record_id}, {error_msg} !")
                raise Exception(error_msg)

            file_upload_path = urllib.parse.unquote(
                received_message.data.meta.file_upload_path
            )
            if file_upload_path:
                formatter = OSWFormat(
                    file_path=file_upload_path,
                    storage_client=self.storage_client,
                    prefix=tdei_record_id,
                )
                result = formatter.format()
                formatter_result = ValidationResult()
                if result and result.status and result.error is None and result.generated_files is not None:
                    if isinstance(result.generated_files, list):
                        converted_file = formatter.create_zip(result.generated_files)
                    else:
                        converted_file = result.generated_files
                    upload_path = self.upload_to_azure(file_path=converted_file,
                                                       project_group_id=received_message.data.tdei_project_group_id,
                                                       record_id=received_message.data.tdei_record_id)
                    formatter_result.is_valid = True
                    formatter_result.validation_message = (
                        "Formatting Successful!"
                    )
                    self.send_status(
                        result=formatter_result,
                        upload_message=received_message,
                        upload_url=upload_path,
                    )
                else:
                    formatter_result.is_valid = False
                    formatter_result.validation_message = "Could not format OSW to OSM or OSM to OSW"
                    logger.error(
                        f"error status : {result.status}, error details : {result.error}"
                    )
                    self.send_status(
                        result=formatter_result, upload_message=received_message
                    )
            else:
                raise Exception("File entity not found")
        except Exception as e:
            logger.error(
                f"{tdei_record_id} Error occurred while formatting OSW request, {e}"
            )
            result = ValidationResult()
            result.is_valid = False
            result.validation_message = (
                f"Error occurred while formatting OSW request {e}"
            )
            self.send_status(result=result, upload_message=received_message)
            traceback.print_exc()

    def upload_to_azure(self, file_path=None, project_group_id=None, record_id=None):
        try:
            base_filename = os.path.basename(file_path)
            file_extension = Path(file_path).suffix
            now = datetime.now()
            year_month_str = now.strftime("%Y/%B").upper()
            filename = f"{year_month_str}"
            if project_group_id:
                filename = f"{filename}/{project_group_id}"
            if record_id:
                filename = f"{filename}/{record_id}"
            if file_extension == '.zip':
                filename = f'{filename}/xml/{base_filename}'
            elif file_extension == '.pbf':
                filename = f'{filename}/pbf/{base_filename}'
            return self.upload_to_azure_on_demand(remote_path=filename, local_url=file_path)
        except Exception as e:
            logger.error(e)
            return None

    def send_status(self, result: ValidationResult, upload_message: OSWValidationMessage, upload_url=None):
        upload_message.data.meta.isValid = result.is_valid
        upload_message.data.meta.validationMessage = result.validation_message
        upload_message.data.stage = "osw-formatter"

        upload_message.data.response.success = result.is_valid
        upload_message.data.response.message = str(result.validation_message)
        if upload_url:
            upload_message.data.meta.download_xml_url = upload_url
        data = QueueMessage.data_from(
            {
                "messageId": uuid.uuid1().hex[0:24],
                "message": upload_message.message or "OSW format output",
                "messageType": "osw-format-result",
                "data": upload_message.data.to_json(),
                "publishedDate": str(datetime.now()),
            }
        )
        try:
            self.publishing_topic.publish(data=data)
        except Exception as e:
            logger.error(e)
        logger.info(f"Publishing message for : {upload_message.data.tdei_record_id}")

    def process_on_demand_format(self, request: OSWOnDemandRequest):
        logger.info("Received on demand request")
        logger.info(request.jobId)
        logger.info(request.sourceUrl)
        logger.info(request.source)
        logger.info(request.target)
        # Format the file
        formatter = OSWFormat(
            file_path=request.sourceUrl,
            storage_client=self.storage_client,
            prefix=request.jobId
        )
        result = formatter.format()
        formatter_result = ValidationResult()
        # Create remote path
        if result and result.status and result.error is None and result.generated_files is not None:
            logger.info('Formatting complete')
            source_file_name = os.path.basename(request.sourceUrl)
            source_file_name_only = os.path.splitext(source_file_name)[0]
            target_directory = f'jobs/{request.jobId}/{request.target}/'
            target_extension = os.path.splitext(result.generated_files)[1]
            target_file_name = source_file_name_only + target_extension
            target_file_remote_path = os.path.join(target_directory, target_file_name)
            logger.info('File to be uploaded to ')
            logger.info(target_file_remote_path)
            new_file_remote_url = self.upload_to_azure_on_demand(remote_path=target_file_remote_path,
                                                                 local_url=result.generated_files)
            response = OSWOnDemandResponse(request.sourceUrl, request.jobId, 'completed', new_file_remote_url, 'Ok')
        else:
            new_file_remote_url = ''
            response = OSWOnDemandResponse(request.sourceUrl, request.jobId, 'failed', new_file_remote_url,
                                           result.error)

        self.send_on_demand_response(response)

    def send_on_demand_response(self, response: OSWOnDemandResponse):
        logger.info(f"Sending response for {response.jobId}")

        data = QueueMessage.data_from({
            'messageId': uuid.uuid1().hex[0:24],
            'message': 'OSW formatter output',
            'messageType': 'osw-formatter-response',
            'data': asdict(response),
            'publishedDate': str(datetime.now())
        })
        self.publishing_topic.publish(data=data)
        logger.info(f'Finished sending response for {response.jobId}')

    def upload_to_azure_on_demand(self, remote_path: str, local_url: str):
        container = self.storage_client.get_container(
            container_name=self.container_name
        )
        file = container.create_file(remote_path)
        with open(local_url, "rb") as data:
            file.upload(data)
        return file.get_remote_url()
