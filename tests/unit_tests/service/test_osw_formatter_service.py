import os
import json
import unittest
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from unittest.mock import Mock, MagicMock, patch, call
from src.service.osw_formatter_service import OSWFomatterService
from src.osw_format import OSWFormat
from src.models.queue_message_content import ValidationResult
from src.models.osw_validation_message import OSWValidationMessage
from src.models.osw_ondemand_request import OSWOnDemandRequest
from src.models.osw_ondemand_response import OSWOnDemandResponse

current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../../')))
parent_dir = os.path.dirname(current_dir)

TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/osw-upload.json')
ON_DEMAND_TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/osw-format-on-demand-request.json')

TEST_FILE = open(TEST_JSON_FILE)
TEST_DATA = json.loads(TEST_FILE.read())

ONDEMAND_REQUEST_FILE = open(ON_DEMAND_TEST_JSON_FILE)
ONDEMAND_REQUEST_DATA = json.loads(ONDEMAND_REQUEST_FILE.read())

SAVED_FILE_PATH = f'{Path.cwd()}/tests/unit_tests/test_files'
DOWNLOAD_PATH = f'{Path.cwd()}/downloads'


@dataclass
class FormatFixture:
    status: bool
    error: Optional[str]
    generated_files: str


class TestOSWFomatterService(unittest.TestCase):

    def setUp(self):
        with patch.object(OSWFomatterService, '__init__', return_value=None):
            self.formatter = OSWFomatterService()
            self.formatter.subscription_name = MagicMock()
            self.formatter.listening_topic = MagicMock()
            self.formatter.publish_topic = MagicMock()
            self.formatter.logger = MagicMock()
            self.formatter.storage_client = MagicMock()
            self.formatter.container_name = MagicMock()
            self.formatter.core = MagicMock()
            self.formatter.core.return_value = MagicMock()
            self.formatter.core.get_topic = MagicMock()
            self.formatter.core.get_topic.return_value = MagicMock()
            self.formatter.download_dir = DOWNLOAD_PATH

    @patch.object(OSWFomatterService, 'start_listening')
    def test_start_listening(self, mock_start_listening):
        # Act
        self.formatter.start_listening()

        # Assert
        mock_start_listening.assert_called_once()

    @patch('src.service.osw_formatter_service.OSWFormat')
    @patch.object(OSWFormat, 'download_single_file')
    @patch.object(OSWFomatterService, 'send_status')
    def test_format_success(self, mock_send_status, mock_download_single_file, mock_osw_format):
        # Set up mock data
        file_path = f'{SAVED_FILE_PATH}/osw.zip'
        # Mock OSWFormat instance
        mock_osw_instance = MagicMock()
        mock_osw_instance.format.return_value = Mock(status=True, error=None, generated_files='file1.xml')
        mock_osw_instance.create_zip.return_value = 'file1.zip'
        mock_osw_format.return_value = mock_osw_instance
        mock_download_single_file.return_value = f'{DOWNLOAD_PATH}/osw.zip'

            # Arrange
        received_message = OSWValidationMessage(data=TEST_DATA)
        formatter_result = ValidationResult()
        formatter_result.is_valid = True
        formatter_result.validation_message = 'Validation successful'
        self.formatter.upload_to_azure = MagicMock()
        self.formatter.upload_to_azure.return_value = 'test_file.xml'

        # Act
        self.formatter.format(received_message=received_message)

        # Assert
        mock_send_status.assert_called_once()
        mock_osw_instance.create_zip.assert_called_once_with(['file1.xml'])

    @patch.object(OSWFomatterService, 'send_status')
    def test_format_failure(self, mock_send_status):
        # Set up mock data
        file_path = f'{SAVED_FILE_PATH}/osw.zip'

        # Mock OSWFormat instance
        with patch.object(OSWFormat, '__init__', return_value=None), \
                patch.object(OSWFormat, 'format', return_value=Mock(status=True, error=None, generated_files='file1.xml')), \
                patch.object(OSWFormat, 'create_zip', return_value='file1.zip'):
            self.OSW_format = OSWFormat(file_path=file_path, storage_client=MagicMock())

            # Arrange
            received_message = OSWValidationMessage(data=TEST_DATA)
            formatter_result = ValidationResult()
            formatter_result.is_valid = False
            formatter_result.validation_message = 'Validation failed'
            self.formatter.upload_to_azure = MagicMock()
            self.formatter.upload_to_azure.return_value = 'test_file.xml'

            # Act
            self.formatter.format(received_message=received_message)

            # Assert
            mock_send_status.assert_called_once()

    @patch.object(OSWFomatterService, 'send_status')
    def test_format_failure_with_invalid_file_path(self, mock_send_status):
        # Set up mock data
        file_path = f'{SAVED_FILE_PATH}/osw.zip'

        # Mock OSWFormat instance
        with patch.object(OSWFormat, '__init__', return_value=None), \
                patch.object(OSWFormat, 'format', return_value=Mock(status=True, error=None, generated_files='file1.xml')), \
                patch.object(OSWFormat, 'create_zip', return_value='file1.zip'):
            self.OSW_format = OSWFormat(file_path=file_path, storage_client=MagicMock())

            # Arrange
            received_message = OSWValidationMessage(data=TEST_DATA)
            formatter_result = ValidationResult()
            formatter_result.is_valid = False
            formatter_result.validation_message = 'Validation failed'
            self.formatter.upload_to_azure = MagicMock()
            self.formatter.upload_to_azure.return_value = 'test_file.xml'

            # Act
            self.formatter.format(received_message=received_message)

            # Assert
            mock_send_status.assert_called_once()

    @patch.object(OSWFomatterService, 'upload_to_azure_on_demand')
    def test_upload_to_azure_success(self, mock_upload_to_azure_on_demand):
        container_mock = Mock()
        file_mock = Mock()

        self.formatter.storage_client.return_value = container_mock
        container_mock.create_file.return_value = file_mock

        self.formatter.upload_to_azure(file_path=f'{SAVED_FILE_PATH}/test_file.txt', project_group_id='test',
                                       record_id='test')
        mock_upload_to_azure_on_demand.assert_called_once()

    def test_upload_to_azure_failure(self):
        result = self.formatter.upload_to_azure(file_path=None)
        self.assertIsNone(result)

    def test_valid_send_status(self):
        self.formatter.publishing_topic = MagicMock()
        self.formatter.publishing_topic.return_value = MagicMock()

        result = ValidationResult()
        result.is_valid = True
        result.validation_message = 'Formatting Successful'

        upload_message = OSWValidationMessage(TEST_DATA)
        # Call the send_status method
        self.formatter.send_status(result=result, upload_message=upload_message)

        # Add assertions for the expected behavior
        self.assertEqual(upload_message.data.success, True)
        self.assertEqual(upload_message.data.message, 'Formatting Successful')

    def test_valid_send_status_with_upload_url(self):
        self.formatter.publishing_topic = MagicMock()
        self.formatter.publishing_topic.return_value = MagicMock()

        result = ValidationResult()
        result.is_valid = True
        result.validation_message = 'Formatting Successful'

        upload_message = OSWValidationMessage(TEST_DATA)
        # Call the send_status method
        self.formatter.send_status(result=result, upload_message=upload_message, upload_url='some_url')

        # Add assertions for the expected behavior
        self.assertEqual(upload_message.data.success, True)
        self.assertEqual(upload_message.data.message, 'Formatting Successful')

    def test_invalid_send_status(self):
        self.formatter.publishing_topic = MagicMock()
        self.formatter.publishing_topic.return_value = MagicMock()

        result = ValidationResult()
        result.is_valid = False
        result.validation_message = 'Formatting Failed'

        upload_message = OSWValidationMessage(TEST_DATA)
        # Call the send_status method
        self.formatter.send_status(result=result, upload_message=upload_message)

        # Add assertions for the expected behavior
        self.assertEqual(upload_message.data.success, False)
        self.assertEqual(upload_message.data.message, 'Formatting Failed')

    @patch.object(OSWFormat, 'format')
    def test_process_on_demand_format_success(self, mock_format):
        file_path = f'{SAVED_FILE_PATH}/osw.zip'
        with patch.object(OSWFormat, '__init__', return_value=None), \
                patch.object(OSWFormat, 'create_zip', return_value='file1.zip') as mock_create_zip:
            mock_init = OSWFormat(file_path=file_path, storage_client=MagicMock())
            mock_init.file_path = file_path
            mock_init.file_relative_path = file_path.split('/')[-1]
            mock_format.return_value = Mock(status=True, error=None, generated_files='file1.xml')

            self.formatter.upload_to_azure_on_demand = MagicMock()
            self.formatter.upload_to_azure_on_demand.return_value = 'some_url'
            self.formatter.send_on_demand_response = MagicMock()
            self.formatter.send_on_demand_response.return_value = MagicMock()

            ondemand_request = ONDEMAND_REQUEST_DATA
            request = OSWOnDemandRequest(
                messageId=ondemand_request['messageId'],
                messageType=ondemand_request['messageType'],
                data=ondemand_request['data']
            )
            self.formatter.process_on_demand_format(request=request)

            mock_format.assert_called_once()
            mock_create_zip.assert_called_once_with(['file1.xml'])

    @patch.object(OSWFormat, 'format')
    def test_process_on_demand_format_failure(self, mock_format):
        file_path = f'{SAVED_FILE_PATH}/osw.zip'
        with patch.object(OSWFormat, '__init__', return_value=None):
            mock_init = OSWFormat(file_path=file_path, storage_client=MagicMock())
            mock_init.file_path = file_path
            mock_init.file_relative_path = file_path.split('/')[-1]
            mock_format.return_value = Mock(status=False, error='Some Error', generated_files='file1.xml')

            self.formatter.upload_to_azure_on_demand = MagicMock()
            self.formatter.upload_to_azure_on_demand.return_value = 'some_url'
            self.formatter.send_on_demand_response = MagicMock()
            self.formatter.send_on_demand_response.return_value = MagicMock()

            ondemand_request = ONDEMAND_REQUEST_DATA
            request = OSWOnDemandRequest(
                messageId=ondemand_request['messageId'],
                messageType=ondemand_request['messageType'],
                data=ondemand_request['data']
            )
            self.formatter.process_on_demand_format(request=request)

            mock_format.assert_called_once()

    def test_send_on_demand_response(self):
        self.formatter.publishing_topic = MagicMock()
        self.formatter.publishing_topic.return_value = MagicMock()
        self.formatter.publishing_topic.publish = MagicMock()
        self.formatter.publishing_topic.publish.return_value = MagicMock()

        ondemand_request = ONDEMAND_REQUEST_DATA
        upload_message = OSWOnDemandRequest(
            messageId=ondemand_request['messageId'],
            messageType=ondemand_request['messageType'],
            data=ondemand_request['data']
        )
        msg = asdict(upload_message.data)
        msg['status'] = 'completed'
        msg['formattedUrl'] = 'target_url'
        msg['message'] = 'some_message'
        msg['success'] = True

        response = OSWOnDemandResponse(messageId=upload_message.messageId, messageType=upload_message.messageType, data=msg)
        self.formatter.send_on_demand_response(response=response)
        self.formatter.core.get_topic().publish.assert_called_once()


if __name__ == '__main__':
    unittest.main()
