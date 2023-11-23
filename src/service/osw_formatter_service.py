import os
import uuid
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
                        target=self.processOnDemandFormat, args=[ondemand_request]
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
                f"Received message for: {tdei_record_id} Message received for OSW format !"
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
                if (
                    result
                    and result.status
                    and result.error is None
                    and result.generated_files is not None
                ):
                    upload_path = self.upload_to_azure(
                        file_path=result.generated_files,
                        project_group_id=received_message.data.tdei_project_group_id,
                        record_id=received_message.data.tdei_record_id,
                    )
                    formatter_result.is_valid = True
                    formatter_result.validation_message = (
                        "OSW to OSM formatting successful!"
                    )
                    self.send_status(
                        result=formatter_result,
                        upload_message=received_message,
                        upload_url=upload_path,
                    )
                else:
                    formatter_result.is_valid = False
                    formatter_result.validation_message = "Could not format OSW to OSM"
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

    def upload_to_azure(self, file_path=None, project_group_id=None, record_id=None):
        try:
            base_filename = os.path.basename(file_path)
            now = datetime.now()
            year_month_str = now.strftime("%Y/%B").upper()
            filename = f"{year_month_str}"
            if project_group_id:
                filename = f"{filename}/{project_group_id}"
            if record_id:
                filename = f"{filename}/{record_id}"
            filename = f"{filename}/xml/{base_filename}"
            container = self.storage_client.get_container(
                container_name=self.container_name
            )
            file = container.create_file(filename)
            with open(file_path, "rb") as data:
                file.upload(data)
            return file.get_remote_url()
        except Exception as e:
            logger.error(e)
            return None

    def send_status(
        self,
        result: ValidationResult,
        upload_message: OSWValidationMessage,
        upload_url=None,
    ):
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
                "message": upload_message.message or "OSW validation output",
                "messageType": "osw-validation",
                "data": upload_message.data.to_json(),
                "publishedDate": str(datetime.now()),
            }
        )
        try:
            self.publishing_topic.publish(data=data)
        except Exception as e:
            logger.error(e)
        logger.info(f"Publishing message for : {upload_message.data.tdei_record_id}")

    def processOnDemandFormat(self, request: OSWOnDemandRequest):
        logger.info("Received on demand request")
        logger.info(request.jobId)
        logger.info(request.sourceUrl)
        logger.info(request.source)
        logger.info(request.target)
        self.sendOnDemandResponse(request, {})

    def sendOnDemandResponse(self, request: OSWOnDemandRequest, response: any):
        logger.info(f"Sending response for {request.jobId}")

        message_data = OSWOnDemandResponse(
            request.sourceUrl, request.jobId, "completed", "", "demo message"
        )

        data = QueueMessage.data_from({
            'messageId': uuid.uuid1().hex[0:24],
            'message': 'OSW formatter output',
            'messageType': 'osw-formatter-response',
            'data': asdict(message_data),
            'publishedDate': str(datetime.now())
        })
        self.publishing_topic.publish(data=data)
