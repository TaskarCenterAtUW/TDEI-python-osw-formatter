import os
import uuid
import time
import json
import shutil
import asyncio
import unittest
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
from unittest.mock import patch, MagicMock

# Execute to apply environment variable overrides
load_dotenv()

os.environ['VALIDATION_TOPIC'] = 'temp-upload'
os.environ['VALIDATION_SUBSCRIPTION'] = 'upload-validation-processor'
os.environ['FORMATTER_TOPIC'] = 'temp-validation'

from python_ms_core import Core
from src.service.osw_formatter_service import OSWFomatterService
from src.models.osw_validation_message import OSWValidationMessage
from python_ms_core.core.queue.models.queue_message import QueueMessage

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_JSON_FILE = os.path.join(TEST_DIR, 'test_harness/test_files/passed_case.json')
SAVED_FILE_PATH = f'{Path.cwd()}/tests/unit_tests/test_files'
DOWNLOAD_FILE_PATH = f'{Path.cwd()}/downloads'


class TestOSWFormatterIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core()
        cls.upload_topic_name = os.environ['VALIDATION_TOPIC']
        cls.upload_subscription_name = os.environ['VALIDATION_SUBSCRIPTION']
        cls.validation_topic_name = os.environ['FORMATTER_TOPIC']

    def setUp(self):
        self.test_data = self.read_test_data()

    @staticmethod
    def read_test_data():
        with open(TEST_JSON_FILE, 'r') as test_file:
            test_data = json.loads(test_file.read())
        return test_data

    def tearDown(self):
        pass

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    def test_subscribe_to_upload_topic(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')
        formatter = OSWFomatterService()
        self.test_data['tdei_record_id'] = str(uuid.uuid4())
        self.test_data['tdei_project_group_id'] = str(uuid.uuid4())
        upload_topic = self.core.get_topic(topic_name=self.upload_topic_name)
        message = QueueMessage.data_from({'message': '', 'data': self.test_data})
        upload_topic.publish(data=message)
        time.sleep(0.5)  # Wait to get the callback
        formatter.start_listening.assert_called_once()

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    async def test_servicebus_receive(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')
        formatter = OSWFomatterService()
        subscribe_function = MagicMock()
        self.test_data['tdei_record_id'] = str(uuid.uuid4())
        message = QueueMessage.data_from({'message': '', 'data': self.test_data})
        formatter.publishing_topic.publish(data=message)
        validation_topic = self.core.get_topic(topic_name=self.validation_topic_name)
        async with validation_topic.subscribe(subscription='temp-validation-result', callback=subscribe_function):
            await asyncio.sleep(0.5)  # Wait for callback
            subscribe_function.assert_called_once()
            formatter.start_listening.assert_called_once()

    def test_file_entity(self):
        test_file_url = 'https://tdeisamplestorage.blob.core.windows.net/osw/test_upload/osw.zip'
        url = urlparse(test_file_url)
        file_path = url.path
        file_components = file_path.split('/')
        container_name = file_components[1]
        file = self.core.get_storage_client().get_file_from_url(container_name=container_name, full_url=test_file_url)
        content = file.get_stream()
        self.assertTrue(content)

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    def test_upload_to_azure(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')

        source_file = f'{SAVED_FILE_PATH}/c8c76e89f30944d2b2abd2491bd95337.graph.osm.xml'
        destination_file = f'{str(uuid.uuid4())}.test.xml'
        shutil.copy(source_file, f'{DOWNLOAD_FILE_PATH}/{destination_file}')
        formatter = OSWFomatterService()
        record_id = str(uuid.uuid4())
        project_id = str(uuid.uuid4())
        uploaded_path = formatter.upload_to_azure(
            file_path=f'{DOWNLOAD_FILE_PATH}/{destination_file}',
            project_group_id=project_id,
            record_id=record_id
        )
        self.assertEqual(os.path.basename(uploaded_path), destination_file)

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    def test_format(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')

        formatter = OSWFomatterService()
        record_id = str(uuid.uuid4())
        self.test_data['tdei_record_id'] = record_id
        message = QueueMessage.data_from({'message': '', 'data': self.test_data})
        queue_message = QueueMessage.to_dict(message)
        upload_message = OSWValidationMessage.data_from(queue_message)
        formatter.format(received_message=upload_message)
        self.assertTrue(os.path.isfile(f'{DOWNLOAD_FILE_PATH}/{record_id}.graph.osm.xml'))


if __name__ == '__main__':
    unittest.main()
