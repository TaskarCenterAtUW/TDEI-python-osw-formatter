import unittest
from unittest.mock import patch, MagicMock, mock_open, PropertyMock
from src.service.osw_formatter_service import OSWFomatterService
from src.models.osw_ondemand_request import OSWOnDemandRequest, RequestData
from src.models.osw_ondemand_response import OSWOnDemandResponse
from src.models.osw_validation_message import OSWValidationMessage


class TestOSWFormatterService(unittest.TestCase):

    @patch('src.service.osw_formatter_service.Settings')
    @patch('src.service.osw_formatter_service.Core')
    def setUp(self, mock_core, mock_settings):
        # Mock Settings
        mock_settings.return_value.event_bus.validation_subscription = 'test_subscription'
        mock_settings.return_value.event_bus.validation_topic = 'test_request_topic'
        mock_settings.return_value.event_bus.formatter_topic = 'test_response_topic'
        mock_settings.return_value.max_concurrent_messages = 10
        mock_settings.return_value.get_download_directory.return_value = '/tmp'
        mock_settings.return_value.event_bus.container_name = 'test_container'

        # Mock Core
        mock_core.return_value.get_topic.return_value = MagicMock()
        mock_core.return_value.get_storage_client.return_value = MagicMock()

        # Initialize InclinationService with mocked dependencies
        self.service = OSWFomatterService()
        self.service.storage_client = MagicMock()
        self.service.container_name = 'test_container'

    @patch('src.service.osw_formatter_service.QueueMessage')
    @patch('src.service.osw_formatter_service.OSWValidationMessage')
    def test_subscribe_with_valid_message(self, mock_request_message, mock_queue_message):
        # Arrange
        mock_message = MagicMock()
        mock_queue_message.to_dict.return_value = {'messageId': '1234', 'data': {'jobId': '5678'}}
        mock_request_message.from_dict.return_value = mock_request_message
        self.service.format = MagicMock()

        # Act
        self.service.start_listening()
        callback = self.service.listening_topic.subscribe.call_args[1]['callback']
        callback(mock_message)

        # Assert
        self.service.format.assert_called_once_with(received_message=mock_request_message.data_from())

    @patch('src.service.osw_formatter_service.QueueMessage')
    @patch('src.service.osw_formatter_service.OSWValidationMessage')
    def test_subscribe_with_valid_ondemand_message(self, mock_request_message, mock_queue_message):
        # Arrange
        mock_message = MagicMock()
        mock_queue_message.to_dict.return_value = {'messageId': '1234', 'messageType': 'on_demand',
                                                   'data': {'jobId': '5678'}}
        mock_request_message.from_dict.return_value = mock_request_message
        self.service.format = MagicMock()

        # Act
        self.service.start_listening()
        callback = self.service.listening_topic.subscribe.call_args[1]['callback']
        callback(mock_message)

        # Assert
        self.service.format.assert_called_once_with(received_message=mock_request_message.data_from())

    @patch('src.service.osw_formatter_service.OSWOnDemandRequest')
    @patch('src.service.osw_formatter_service.logger')
    @patch('src.service.osw_formatter_service.QueueMessage')
    def test_on_demand_request_success(self, mock_queue_message, mock_logger, mock_request):
        # Arrange
        mock_message = MagicMock()
        mock_message.messageType = 'on_demand'
        mock_message.messageId = '1234'
        mock_queue_message.to_dict.return_value = {'data': {'jobId': '5678'}}
        mock_request.return_value.data.jobId = '5678'

        self.service.process_on_demand_format = MagicMock()

        # Act
        callback = self.service.listening_topic.subscribe.call_args[1]['callback']
        callback(mock_message)

        # Assert
        mock_request.assert_called_once_with(
            messageType='on_demand',
            messageId='1234',
            data={'jobId': '5678'}
        )
        mock_logger.info.assert_called_with('Received on demand request: 5678')
        self.service.process_on_demand_format.assert_called_once_with(request=mock_request.return_value)


    @patch('src.service.osw_formatter_service.OSWOnDemandRequest')
    @patch('src.service.osw_formatter_service.OSWOnDemandResponse')
    @patch('src.service.osw_formatter_service.logger')
    def test_on_demand_request_exception(self, mock_logger, mock_response, mock_request):
        # Arrange
        mock_message = MagicMock()
        mock_message.messageType = 'on_demand'
        mock_message.messageId = '1234'
        mock_queue_message = {'data': {'jobId': '5678'}}
        mock_request.side_effect = Exception("Mocked exception")
        mock_response.return_value = MagicMock()

        self.service.send_on_demand_response = MagicMock()

        # Act
        callback = self.service.listening_topic.subscribe.call_args[1]['callback']
        callback(mock_message)

        # Assert
        mock_logger.error.assert_called_with(
            "Error occurred while processing on demand message, Mocked exception"
        )
        self.service.send_on_demand_response.assert_called_once_with(
            response=mock_response.return_value
        )
        mock_response.assert_called_once_with(
            messageId='1234',
            messageType='on_demand',
            data={
                'status': 'failed',
                'message': 'Mocked exception',
                'success': False
            }
        )

    @patch('src.service.osw_formatter_service.ValidationResult')
    @patch('src.service.osw_formatter_service.QueueMessage')
    @patch('src.service.osw_formatter_service.logger')
    def test_start_listening_exception(self, mock_logger, mock_queue_message, mock_validation_result):
        # Arrange
        mock_message = MagicMock()
        mock_queue_message.to_dict.side_effect = Exception("Mocked exception")
        mock_validation_result.return_value = MagicMock()

        # Act
        self.service.start_listening()
        callback = self.service.listening_topic.subscribe.call_args[1]['callback']
        callback(mock_message)

        # Assert
        mock_logger.error.assert_called_with("Error occurred while processing message, Mocked exception")

    def test_format_file_upload_path_none(self):
        # Arrange
        received_message = OSWValidationMessage({
            'messageId': '1234',
            'messageType': 'message_type',
            'data': {
                'file_upload_path': None,
                'tdei_project_group_id': '1',
                'formatted_url': '',
                'success': False,
                'message': ''
            }
        })

        with patch('src.service.osw_formatter_service.logger') as mock_logger:
            # Act
            self.service.format(received_message)

            # Assert
            mock_logger.error.assert_any_call(
                "1234, Request does not have a valid file path specified. !"
            )

    @patch('src.service.osw_formatter_service.OSWFormat')
    def test_format_with_generated_files_list(self, mock_osw_format):
        # Arrange
        received_message = OSWValidationMessage({
            'messageId': '1234',
            'messageType': 'message_type',
            'data': {
                'file_upload_path': 'http://example.com/file.osm',
                'tdei_project_group_id': '1',
                'formatted_url': '',
                'success': True,
                'message': ''
            }
        })

        # Mock OSWFormat instance
        mock_osw_instance = MagicMock()
        mock_osw_format.return_value = mock_osw_instance

        # Mock format method return values
        mock_format_result = MagicMock()
        mock_format_result.status = True
        mock_format_result.error = None
        mock_format_result.generated_files = ['file1.geojson', 'file2.geojson']
        mock_osw_instance.format.return_value = mock_format_result

        # Mock create_zip return value
        mock_osw_instance.create_zip.return_value = 'zipped_file.zip'

        self.service.upload_to_azure = MagicMock()
        self.service.upload_to_azure.return_value = 'uploaded_path'

        # Act
        self.service.format(received_message)

        # Assert
        mock_osw_instance.create_zip.assert_called_once_with(['file1.geojson', 'file2.geojson'])
        self.service.upload_to_azure.assert_called_once()

    @patch('src.service.osw_formatter_service.OSWFormat')
    def test_format_with_generated_file(self, mock_osw_format):
        # Arrange
        received_message = OSWValidationMessage({
            'messageId': '1234',
            'messageType': 'message_type',
            'data': {
                'file_upload_path': 'http://example.com/file.osm',
                'tdei_project_group_id': '1',
                'formatted_url': '',
                'success': True,
                'message': ''
            }
        })

        # Mock OSWFormat instance
        mock_osw_instance = MagicMock()
        mock_osw_format.return_value = mock_osw_instance

        # Mock format method return values
        mock_format_result = MagicMock()
        mock_format_result.status = True
        mock_format_result.error = None
        mock_format_result.generated_files = 'file1.xml'
        mock_osw_instance.format.return_value = mock_format_result

        mock_osw_instance.create_zip.return_value = 'zipped_file.zip'

        self.service.upload_to_azure = MagicMock()
        self.service.upload_to_azure.return_value = 'uploaded_path'

        # Act
        self.service.format(received_message)

        mock_osw_instance.create_zip.assert_called_once_with(['file1.xml'])
        self.service.upload_to_azure.assert_called_once()

    @patch('src.service.osw_formatter_service.OSWFormat')
    def test_process_on_demand_format_with_generated_files_list(self, mock_osw_format):
        # Arrange
        message_data = {
            'sourceUrl': 'http://example.com/file.osm',
            'jobId': '1234',
            'source': 'source_format',
            'target': 'target_format'
        }
        received_message = OSWOnDemandRequest(
            messageId='1234',
            messageType='message_type',
            data=message_data
        )

        # Mock OSWFormat instance
        mock_osw_instance = MagicMock()
        mock_osw_format.return_value = mock_osw_instance

        # Mock format method return values
        mock_format_result = MagicMock()
        mock_format_result.status = True
        mock_format_result.error = None
        mock_format_result.generated_files = ['file1.geojson', 'file2.geojson']
        mock_osw_instance.format.return_value = mock_format_result

        # Mock create_zip return value
        mock_osw_instance.create_zip.return_value = 'zipped_file.zip'

        self.service.upload_to_azure_on_demand = MagicMock()
        self.service.upload_to_azure_on_demand.return_value = 'uploaded_path'

        # Act
        self.service.process_on_demand_format(received_message)

        # Assert
        mock_osw_instance.create_zip.assert_called_once_with(['file1.geojson', 'file2.geojson'])
        self.service.upload_to_azure_on_demand.assert_called_once()

    @patch('src.service.osw_formatter_service.OSWFormat')
    def test_process_on_demand_format_with_generated_xml(self, mock_osw_format):
        # Arrange
        message_data = {
            'sourceUrl': 'http://example.com/file.osm',
            'jobId': '1234',
            'source': 'source_format',
            'target': 'target_format'
        }
        received_message = OSWOnDemandRequest(
            messageId='1234',
            messageType='message_type',
            data=message_data
        )

        # Mock OSWFormat instance
        mock_osw_instance = MagicMock()
        mock_osw_format.return_value = mock_osw_instance

        # Mock format method return values
        mock_format_result = MagicMock()
        mock_format_result.status = True
        mock_format_result.error = None
        mock_format_result.generated_files = 'file1.xml'
        mock_osw_instance.format.return_value = mock_format_result

        # Mock create_zip return value
        mock_osw_instance.create_zip.return_value = 'zipped_file.zip'

        self.service.upload_to_azure_on_demand = MagicMock()
        self.service.upload_to_azure_on_demand.return_value = 'uploaded_path'

        # Act
        self.service.process_on_demand_format(received_message)

        # Assert
        mock_osw_instance.create_zip.assert_called_once_with(['file1.xml'])
        self.service.upload_to_azure_on_demand.assert_called_once()

    @patch('src.service.osw_formatter_service.OSWFormat')
    @patch('src.service.osw_formatter_service.logger')
    def test_process_on_demand_format_exception(self, mock_logger, mock_osw_format):
        # Arrange
        self.service.send_on_demand_response = MagicMock()

        message_data = {
            'sourceUrl': 'http://example.com/file.osm',
            'jobId': '1234',
            'source': 'source_format',
            'target': 'target_format'
        }
        received_message = OSWOnDemandRequest(
            messageId='1234',
            messageType='message_type',
            data=message_data
        )

        mock_osw_instance = MagicMock()
        mock_osw_format.return_value = mock_osw_instance
        mock_osw_instance.format.side_effect = Exception("Mocked formatting exception")

        # Act
        self.service.process_on_demand_format(received_message)

        # Assert
        mock_logger.error.assert_called_with(
            'Error occurred while processing on demand message, Mocked formatting exception'
        )

        # Verify `send_on_demand_response` was called with the correct parameters
        self.service.send_on_demand_response.assert_called_once()
        response = self.service.send_on_demand_response.call_args[1]['response']

        # Validate the response object
        self.assertEqual(response.messageId, '1234')
        self.assertEqual(response.messageType, 'message_type')
        self.assertEqual(response.data.sourceUrl, '')
        self.assertEqual(response.data.jobId, '1234')
        self.assertEqual(response.data.source, '')
        self.assertEqual(response.data.target, '')
        self.assertEqual(response.data.status, 'failed')
        self.assertIn('Mocked formatting exception', response.data.message)
        self.assertFalse(response.data.success)
        self.assertEqual(response.data.formattedUrl, '')

    @patch('src.service.osw_formatter_service.open', new_callable=mock_open, read_data=b"mock file content")
    @patch('src.service.osw_formatter_service.OSWFomatterService')
    def test_upload_to_azure_on_demand(self, mock_service, mock_open_file):
        # Arrange
        mock_container = MagicMock()
        mock_file = MagicMock()
        mock_file.get_remote_url.return_value = "https://example.com/mock_remote_url"
        mock_container.create_file.return_value = mock_file
        mock_service.storage_client.get_container.return_value = mock_container


        self.service.storage_client = mock_service.storage_client
        self.service.container_name = "mock_container"

        remote_path = "mock/remote/path/file.txt"
        local_url = "/mock/local/path/file.txt"

        # Act
        result = self.service.upload_to_azure_on_demand(remote_path, local_url)

        # Assert
        mock_service.storage_client.get_container.assert_called_once_with(container_name="mock_container")
        mock_container.create_file.assert_called_once_with(remote_path)
        mock_file.upload.assert_called_once()
        mock_open_file.assert_called_once_with(local_url, "rb")
        self.assertEqual(result, "https://example.com/mock_remote_url")

    @patch('src.service.osw_formatter_service.threading.Thread')
    def test_stop_listening(self, mock_thread):
        # Arrange
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        self.service.listening_thread = mock_thread_instance

        # Act
        result = self.service.stop_listening()

        # Assert
        mock_thread_instance.join.assert_called_once_with(timeout=0)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
