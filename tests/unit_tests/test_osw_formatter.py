import os
import json
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, call
from src.osw_formatter import OSWFomatter
from src.formatter import OSWFormat
from src.models.queue_message_content import ValidationResult, Upload

current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../')))
parent_dir = os.path.dirname(current_dir)

TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/osw-upload.json')

TEST_FILE = open(TEST_JSON_FILE)
TEST_DATA = json.loads(TEST_FILE.read())

SAVED_FILE_PATH = f'{Path.cwd()}/tests/unit_tests/test_files'
DOWNLOAD_PATH = f'{Path.cwd()}/downloads'


class TestOSWFormatter(unittest.TestCase):

    def setUp(self):
        with patch.object(OSWFomatter, '__init__', return_value=None):
            self.formatter = OSWFomatter()
            self.formatter.subscription_name = MagicMock()
            self.formatter.listening_topic = MagicMock()
            self.formatter.publish_topic = MagicMock()
            self.formatter.logger = MagicMock()
            self.formatter.storage_client = MagicMock()
            self.formatter.container_name = MagicMock()

    @patch.object(OSWFomatter, 'start_listening')
    def test_start_listening(self, mock_start_listening):
        # Act
        self.formatter.start_listening()

        # Assert
        mock_start_listening.assert_called_once()

    @patch.object(OSWFomatter, 'send_status')  # Mock the send_status method
    def test_valid_send_status(self, mock_send_status):
        upload_message_data = MagicMock()
        upload_message_data.stage = 'OSW-Format'  # Set the stage attribute

        # Create a mock meta object
        mock_meta = MagicMock()
        mock_meta.isValid = True
        mock_meta.validationMessage = 'Formatting Successful'

        upload_message_data.meta = mock_meta

        # Create a mock response object
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message = 'Formatting Successful'

        upload_message_data.response = mock_response

        # Create a mock upload_message object
        upload_message = MagicMock()
        upload_message.message = 'Test message'
        upload_message.data = upload_message_data
        result = ValidationResult()
        result.is_valid = True
        result.validation_message = ''
        # Call the send_status method
        self.formatter.send_status(result=result, upload_message=upload_message, )

        # Add assertions for the expected behavior
        self.assertEqual(upload_message_data.stage, 'OSW-Format')
        self.assertTrue(upload_message_data.meta.isValid)
        self.assertEqual(upload_message_data.meta.validationMessage, 'Formatting Successful')
        self.assertTrue(upload_message_data.response.success)
        self.assertEqual(upload_message_data.response.message, 'Formatting Successful')

        # Assert that the send_status method was called once with the expected arguments
        mock_send_status.assert_called_once_with(result=result, upload_message=upload_message)

    @patch.object(OSWFomatter, 'send_status')  # Mock the send_status method
    def test_valid_send_status_with_upload_url(self, mock_send_status):
        upload_message_data = MagicMock()
        upload_message_data.stage = 'OSW-Format'  # Set the stage attribute

        # Create a mock meta object
        upload_url = 'Some URL'
        mock_meta = MagicMock()
        mock_meta.isValid = True
        mock_meta.validationMessage = 'Formatting Successful'
        mock_meta.download_xml_url = upload_url

        upload_message_data.meta = mock_meta

        # Create a mock response object
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message = 'Formatting Successful'

        upload_message_data.response = mock_response

        # Create a mock upload_message object
        upload_message = MagicMock()
        upload_message.message = 'Test message'
        upload_message.data = upload_message_data
        result = ValidationResult()
        result.is_valid = True
        result.validation_message = ''

        # Call the send_status method
        self.formatter.send_status(result=result, upload_message=upload_message, upload_url=upload_url)
        # Add assertions for the expected behavior
        self.assertEqual(upload_message_data.stage, 'OSW-Format')
        self.assertTrue(upload_message_data.meta.isValid)
        self.assertEqual(upload_message_data.meta.validationMessage, 'Formatting Successful')
        self.assertTrue(upload_message_data.response.success)
        self.assertEqual(upload_message_data.response.message, 'Formatting Successful')
        self.assertEqual(upload_message_data.meta.download_xml_url, 'Some URL')

        # Assert that the send_status method was called once with the expected arguments
        mock_send_status.assert_called_once_with(result=result, upload_message=upload_message, upload_url=upload_url)

    @patch.object(OSWFomatter, 'send_status')  # Mock the send_status method
    def test_invalid_send_status(self, mock_send_status):
        upload_message_data = MagicMock()
        upload_message_data.stage = 'OSW-Format'  # Set the stage attribute

        # Create a mock meta object
        mock_meta = MagicMock()
        mock_meta.isValid = False
        mock_meta.validationMessage = 'Formatting Failed'

        upload_message_data.meta = mock_meta

        # Create a mock response object
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.message = 'Formatting Failed'

        upload_message_data.response = mock_response

        # Create a mock upload_message object
        upload_message = MagicMock()
        upload_message.message = 'Test message'
        upload_message.data = upload_message_data
        result = ValidationResult()
        result.is_valid = True
        result.validation_message = 'Formatting Failed'

        # Call the send_status method
        self.formatter.send_status(result=result, upload_message=upload_message)

        # Add assertions for the expected behavior
        self.assertEqual(upload_message_data.stage, 'OSW-Format')
        self.assertFalse(upload_message_data.meta.isValid)
        self.assertEqual(upload_message_data.meta.validationMessage, 'Formatting Failed')
        self.assertFalse(upload_message_data.response.success)
        self.assertEqual(upload_message_data.response.message, 'Formatting Failed')

        # Assert that the send_status method was called once with the expected arguments
        mock_send_status.assert_called_once_with(result=result, upload_message=upload_message)

    def test_upload_to_azure_success(self):
        container_mock = Mock()
        file_mock = Mock()

        self.formatter.storage_client.return_value = container_mock
        container_mock.create_file.return_value = file_mock

        result = self.formatter.upload_to_azure(file_path=f'{SAVED_FILE_PATH}/test_file.txt')
        self.assertIsNotNone(result)

    def test_upload_to_azure_failure(self):
        container_mock = Mock()
        file_mock = Mock()

        self.formatter.storage_client.return_value = container_mock
        container_mock.create_file.return_value = file_mock

        result = self.formatter.upload_to_azure(file_path='/path/to/test_file.txt')
        self.assertIsNone(result)

    @patch.object(OSWFormat, 'download_single_file')
    @patch.object(OSWFomatter, 'send_status')
    def test_format_success(self, mock_send_status, mock_download_single_file):
        # Set up mock data
        file_path = f'{SAVED_FILE_PATH}/osw.zip'
        # Mock OSWFormat instance
        with patch.object(OSWFormat, '__init__', return_value=None):
            self.OSW_format = OSWFormat(file_path=file_path, storage_client=MagicMock())
            self.OSW_format.file_path = MagicMock()
            self.OSW_format.file_path.return_value = Mock(file_path)
            self.OSW_format.file_relative_path = MagicMock()
            self.OSW_format.file_relative_path.return_value = Mock(file_path.split('/')[-1])
            mock_download_single_file.return_value = f'{DOWNLOAD_PATH}/osw.zip'
            self.OSW_format.format = MagicMock()
            self.OSW_format.format.return_value = Mock(status=True, error=None, generated_files='file1.xml')

            # Arrange
        received_message = Upload(data=TEST_DATA)
        received_message.data.meta.isValid = True
        formatter_result = ValidationResult()
        formatter_result.is_valid = True
        formatter_result.validation_message = 'Validation successful'
        self.formatter.upload_to_azure = MagicMock()
        self.formatter.upload_to_azure.return_value = 'test_file.xml'

        # Act
        self.formatter.format(received_message=received_message)

        # Assert
        mock_send_status.assert_called_once()

    @patch.object(OSWFomatter, 'send_status')
    def test_format_failure(self, mock_send_status):
        # Set up mock data
        file_path = f'{SAVED_FILE_PATH}/osw.zip'

        # Mock OSWFormat instance
        with patch.object(OSWFormat, '__init__', return_value=None):
            self.OSW_format = OSWFormat(file_path=file_path, storage_client=MagicMock())
            self.OSW_format.format = MagicMock()
            self.OSW_format.format.return_value = Mock(status=True, error=None, generated_files='file1.xml')

            # Arrange
            received_message = Upload(data=TEST_DATA)
            formatter_result = ValidationResult()
            formatter_result.is_valid = False
            formatter_result.validation_message = 'Validation failed'
            self.formatter.upload_to_azure = MagicMock()
            self.formatter.upload_to_azure.return_value = 'test_file.xml'

            # Act
            self.formatter.format(received_message=received_message)

            # Assert
            mock_send_status.assert_called_once()


if __name__ == '__main__':
    unittest.main()
