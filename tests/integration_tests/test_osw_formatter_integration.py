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
from src.models.osw_ondemand_request import OSWOnDemandRequest

# Execute to apply environment variable overrides
load_dotenv()

os.environ['FORMATTER_TOPIC'] = 'temp-upload'
os.environ['FORMATTER_SUBSCRIPTION'] = 'upload-validation-processor'
os.environ['FORMATTER_UPLOAD_TOPIC'] = 'temp-validation'

from python_ms_core import Core
from src.service.osw_formatter_service import OSWFomatterService
from src.models.osw_validation_message import OSWValidationMessage
from python_ms_core.core.queue.models.queue_message import QueueMessage

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_JSON_FILE1 = os.path.join(TEST_DIR, 'test_harness/test_files/passed_case1.json')
TEST_JSON_FILE2 = os.path.join(TEST_DIR, 'test_harness/test_files/passed_case2.json')
TEST_JSON_FILE3 = os.path.join(TEST_DIR, 'test_harness/test_files/passed_case3.json')
SAVED_FILE_PATH = f'{Path.cwd()}/tests/unit_tests/test_files'
DOWNLOAD_FILE_PATH = f'{Path.cwd()}/downloads'


class TestOSWFormatterIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core()
        cls.upload_topic_name = os.environ['FORMATTER_TOPIC']
        cls.upload_subscription_name = os.environ['FORMATTER_UPLOAD_TOPIC']
        cls.validation_topic_name = os.environ['FORMATTER_UPLOAD_TOPIC']

    def setUp(self):
        self.test_data1 = self.read_test_data(TEST_JSON_FILE1)
        self.test_data2 = self.read_test_data(TEST_JSON_FILE2)
        self.test_data3 = self.read_test_data(TEST_JSON_FILE3)

    @staticmethod
    def read_test_data(file):
        with open(file, 'r') as test_file:
            test_data = json.loads(test_file.read())
        return test_data

    def tearDown(self):
        pass

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    def test_subscribe_to_upload_topic_with_zip(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')
        formatter = OSWFomatterService()
        self.test_data1['messageId'] = str(uuid.uuid4())
        upload_topic = self.core.get_topic(topic_name=self.upload_topic_name)
        message = QueueMessage.data_from(self.test_data1)
        upload_topic.publish(data=message)
        time.sleep(0.5)  # Wait to get the callback
        formatter.start_listening.assert_called_once()

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    def test_subscribe_to_upload_topic_with_pbf(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')
        formatter = OSWFomatterService()
        self.test_data2['messageId'] = str(uuid.uuid4())
        upload_topic = self.core.get_topic(topic_name=self.upload_topic_name)
        message = QueueMessage.data_from(self.test_data2)
        upload_topic.publish(data=message)
        time.sleep(0.5)  # Wait to get the callback
        formatter.start_listening.assert_called_once()

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    async def test_servicebus_receive_with_zip(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')
        formatter = OSWFomatterService()
        subscribe_function = MagicMock()
        self.test_data1['messageId'] = str(uuid.uuid4())
        message = QueueMessage.data_from(self.test_data1)
        formatter.publishing_topic.publish(data=message)
        validation_topic = self.core.get_topic(topic_name=self.validation_topic_name)
        with validation_topic.subscribe(subscription='temp-validation-result', callback=subscribe_function):
            await asyncio.sleep(0.5)  # Wait for callback
            subscribe_function.assert_called_once()
            formatter.start_listening.assert_called_once()

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    async def test_servicebus_receive_with_pbf(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')
        formatter = OSWFomatterService()
        subscribe_function = MagicMock()
        self.test_data2['messageId'] = str(uuid.uuid4())
        message = QueueMessage.data_from(self.test_data2)
        formatter.publishing_topic.publish(data=message)
        validation_topic = self.core.get_topic(topic_name=self.validation_topic_name)
        with validation_topic.subscribe(subscription='temp-validation-result', callback=subscribe_function):
            await asyncio.sleep(0.5)  # Wait for callback
            subscribe_function.assert_called_once()
            formatter.start_listening.assert_called_once()

    def test_zip_file_entity(self):
        test_file_url = 'https://tdeisamplestorage.blob.core.windows.net/osw/test_upload/osw.zip'
        url = urlparse(test_file_url)
        file_path = url.path
        file_components = file_path.split('/')
        container_name = file_components[1]
        file = self.core.get_storage_client().get_file_from_url(container_name=container_name, full_url=test_file_url)
        content = file.get_stream()
        self.assertTrue(content)

    def test_pbf_file_entity(self):
        test_file_url = 'https://tdeisamplestorage.blob.core.windows.net/osw/test_upload/wa.microsoft.osm.pbf'
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
        # Extract filenames without timestamp
        uploaded_filename = os.path.splitext(os.path.basename(uploaded_path))[0].rsplit('_', 1)[0]
        destination_filename = os.path.splitext(destination_file)[0]

        # Assert filenames without timestamp are equal
        self.assertEqual(uploaded_filename, destination_filename)

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    def test_format_zip(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')

        formatter = OSWFomatterService()
        record_id = str(uuid.uuid4())
        self.test_data1['messageId'] = record_id
        message = QueueMessage.data_from(self.test_data1)
        queue_message = QueueMessage.to_dict(message)
        upload_message = OSWValidationMessage.data_from(queue_message)
        formatter.format(received_message=upload_message)
        self.assertTrue(os.path.isfile(f'{DOWNLOAD_FILE_PATH}/{record_id}.graph.osm.xml'))

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    def test_format_pbf(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')

        formatter = OSWFomatterService()
        record_id = str(uuid.uuid4())
        self.test_data2['messageId'] = record_id
        message = QueueMessage.data_from(self.test_data2)
        queue_message = QueueMessage.to_dict(message)
        upload_message = OSWValidationMessage.data_from(queue_message)
        formatter.format(received_message=upload_message)
        self.assertTrue(os.path.isfile(f'{DOWNLOAD_FILE_PATH}/{record_id}.zip'))

    @patch.object(OSWFomatterService, 'start_listening', new=MagicMock())
    def test_ondemand(self):
        if os.environ['QUEUECONNECTION'] is None:
            self.fail('QUEUECONNECTION environment not set')

        formatter = OSWFomatterService()
        record_id = str(uuid.uuid4())
        self.test_data3['messageId'] = record_id
        message = QueueMessage.data_from(self.test_data3)
        queue_message = QueueMessage.to_dict(message)
        queue_message['data']['jobId'] = record_id
        upload_message = OSWOnDemandRequest(messageType=queue_message['messageType'], messageId=queue_message['messageId'], data=queue_message['data'])
        formatter.process_on_demand_format(request=upload_message)
        self.assertTrue(os.path.isfile(f'{DOWNLOAD_FILE_PATH}/{record_id}.graph.osm.xml'))





if __name__ == '__main__':
    unittest.main()
