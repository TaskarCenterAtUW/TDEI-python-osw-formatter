import os
import time
import logging
import traceback
import threading
import urllib.parse
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
        def process(message: QueueMessage) -> None:
            if message is not None:
                queue_message = QueueMessage.to_dict(message)
                messageType = message.messageType
                if "ON_DEMAND" in messageType:
                    logger.info("Received on demand request")
                    ondemand_request = OSWOnDemandRequest(messageType=messageType, messageId=message.messageId, data=queue_message['data'])
                    logger.info(ondemand_request)
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
            tdei_record_id = received_message.message_id

            logger.info(
                f"Received message for: {tdei_record_id} Message received for formatting !"
            )

            if received_message.data.file_upload_path is None:
                error_msg = "Request does not have a valid file path specified."
                logger.error(f"{tdei_record_id}, {error_msg} !")
                raise Exception(error_msg)

            file_upload_path = urllib.parse.unquote(
                received_message.data.file_upload_path
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
                    # Generated files can be .xml or bunch of geojson
                    if isinstance(result.generated_files, list): # If its a list
                        converted_file = formatter.create_zip(result.generated_files)
                    else:
                        converted_file = result.generated_files
                    upload_path = self.upload_to_azure(file_path=converted_file,
                                                       project_group_id=received_message.data.tdei_project_group_id,
                                                       record_id=tdei_record_id)
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
                raise Exception('File entity not found')
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
            unix_timestamp = int(time.time())
            now = datetime.now()
            year_month_str = now.strftime("%Y/%B").upper()
            filename = f"{year_month_str}"

            base_filename, file_extension = os.path.splitext(os.path.basename(file_path))
            updated_filename = f'{base_filename}_{unix_timestamp}{file_extension}'

            if project_group_id:
                filename = f"{filename}/{project_group_id}"
            if record_id:
                filename = f"{filename}/{record_id}"
            filename = f'{filename}/{updated_filename}'
            return self.upload_to_azure_on_demand(remote_path=filename, local_url=file_path)
        except Exception as e:
            logger.error(e)
            return None

    def send_status(self, result: ValidationResult, upload_message: OSWValidationMessage, upload_url=None):
        upload_message.data.success = result.is_valid
        upload_message.data.message = result.validation_message
        if upload_url:
            upload_message.data.formatted_url = upload_url
        data = QueueMessage.data_from(
            {
                "messageId": upload_message.message_id,
                "messageType": upload_message.message_type,
                "data": upload_message.data.to_json(),
            }
        )
        try:
            self.publishing_topic.publish(data=data)
        except Exception as e:
            logger.error(e)
        logger.info(f"Publishing message for : {upload_message.message_id}")

    def process_on_demand_format(self, request: OSWOnDemandRequest):
        logger.info("Received on demand request")
        logger.info(request.data.jobId)
        logger.info(request.data.sourceUrl)
        logger.info(request.data.source)
        logger.info(request.data.target)
        # Format the file
        formatter = OSWFormat(
            file_path=request.data.sourceUrl,
            storage_client=self.storage_client,
            prefix=request.data.jobId
        )
        result = formatter.format()
        formatter_result = ValidationResult()
        osw_response = asdict(request.data)
        # Create remote path
        if result and result.status and result.error is None and result.generated_files is not None:
            logger.info('Formatting complete')
            if isinstance(result.generated_files, list): # If its a list
                converted_file = formatter.create_zip(result.generated_files)
            else:
                converted_file = result.generated_files

            target_directory = f'jobs/{request.data.jobId}/{request.data.target}'
            target_file_remote_path = f'{target_directory}/{os.path.basename(converted_file)}'

            new_file_remote_url = self.upload_to_azure_on_demand(remote_path=target_file_remote_path,
                                                                 local_url=converted_file)

            logger.info(f'File to be uploaded to: {target_file_remote_path}')

            osw_response['status'] = 'completed'
            osw_response['formattedUrl'] = new_file_remote_url
            osw_response['message'] = 'OK'
            osw_response['success'] = True
        else:
            osw_response['status'] = 'failed'
            osw_response['formattedUrl'] = ''
            osw_response['message'] = result.error
            osw_response['success'] = False

        response = OSWOnDemandResponse(messageId=request.messageId, messageType=request.messageType, data=osw_response)

        self.send_on_demand_response(response= response)

    def send_on_demand_response(self, response: OSWOnDemandResponse):
        logger.info(f"Sending response for {response.data.jobId}")
        data = QueueMessage.data_from({
            "messageId": response.messageId,
            "messageType": response.messageType,
            'data': asdict(response.data)
        })
        self.publishing_topic.publish(data=data)
        logger.info(f'Finished sending response for {response.data.jobId}')

    def upload_to_azure_on_demand(self, remote_path: str, local_url: str):
        container = self.storage_client.get_container(
            container_name=self.container_name
        )
        file = container.create_file(remote_path)
        with open(local_url, "rb") as data:
            file.upload(data)
        return file.get_remote_url()
