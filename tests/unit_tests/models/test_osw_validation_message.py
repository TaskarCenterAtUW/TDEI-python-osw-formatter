import os
import json
import unittest
from unittest.mock import MagicMock
from src.models.osw_validation_message import OSWValidationMessage
from src.models.osw_validation_data import OSWValidationData

current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../../')))
parent_dir = os.path.dirname(current_dir)

TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/osw-upload.json')

TEST_FILE = open(TEST_JSON_FILE)
TEST_DATA = json.loads(TEST_FILE.read())


class TestOSWValidationMessage(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA
        self.upload = OSWValidationMessage(data)

    def test_message(self):
        self.upload.message = 'New message'
        self.assertEqual(self.upload.message, 'New message')

    def test_message_type(self):
        self.assertEqual(self.upload.message_type, 'osw-upload')
        self.upload.message_type = 'New messageType'
        self.assertEqual(self.upload.message_type, 'New messageType')

    def test_message_id(self):
        self.upload.message_id = 'New messageId'
        self.assertEqual(self.upload.message_id, 'New messageId')

    def test_published_date(self):
        self.assertEqual(self.upload.published_date, '2023-02-08T08:33:36.267213Z')
        self.upload.published_date = '2023-05-24'
        self.assertEqual(self.upload.published_date, '2023-05-24')

    def test_data(self):
        self.assertIsInstance(self.upload.data, OSWValidationData)
        self.assertEqual(self.upload.data.stage, 'OSW-Upload')
        self.upload.data.stage = 'Test stage'
        self.assertEqual(self.upload.data.stage, 'Test stage')

    def test_to_json(self):
        self.upload.data.to_json = MagicMock(return_value={})
        json_data = self.upload.to_json()
        self.assertIsInstance(json_data, dict)
        self.assertEqual(json_data['message_type'], 'osw-upload')
        self.assertEqual(json_data['published_date'], '2023-02-08T08:33:36.267213Z')

    def test_data_from(self):
        message = TEST_DATA
        upload = OSWValidationMessage.data_from(json.dumps(message))
        self.assertIsInstance(upload, OSWValidationMessage)
        self.assertEqual(upload.message_type, 'osw-upload')
        self.assertEqual(upload.published_date, '2023-02-08T08:33:36.267213Z')

    def test_upload_to_json(self):
        json_data = self.upload.to_json()
        self.assertTrue(isinstance(json_data, dict))


if __name__ == '__main__':
    unittest.main()