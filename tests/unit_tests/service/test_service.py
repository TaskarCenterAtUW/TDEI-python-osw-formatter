import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.service.osw_formatter_service import OSWFomatterService


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
        self.service.process = MagicMock()

        # Act
        self.service.start_listening()
        callback = self.service.listening_topic.subscribe.call_args[1]['callback']
        callback(mock_message)

        # Assert
        self.service.process.assert_called_once_with(mock_request_message)

    @patch('src.service.osw_formatter_service.QueueMessage')
    @patch('src.service.osw_formatter_service.OSWValidationMessage')
    def test_subscribe_with_valid_ondemand_message(self, mock_request_message, mock_queue_message):
        # Arrange
        mock_message = MagicMock()
        mock_queue_message.to_dict.return_value = {'messageId': '1234', 'messageType': 'on_demand', 'data': {'jobId': '5678'}}
        mock_request_message.from_dict.return_value = mock_request_message
        self.service.process = MagicMock()

        # Act
        self.service.start_listening()
        callback = self.service.listening_topic.subscribe.call_args[1]['callback']
        callback(mock_message)

        # Assert
        self.service.process.assert_called_once_with(mock_request_message)


if __name__ == '__main__':
    unittest.main()
