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

    def test_message_type(self):
        self.assertEqual(self.upload.message_type, 'workflow_identifier')
        self.upload.message_type = 'New messageType'
        self.assertEqual(self.upload.message_type, 'New messageType')

    def test_message_id(self):
        self.upload.message_id = 'New messageId'
        self.assertEqual(self.upload.message_id, 'New messageId')

    def test_data(self):
        self.assertIsInstance(self.upload.data, OSWValidationData)
        self.upload.data.tdei_project_group_id = 'Test Group ID'
        self.assertEqual(self.upload.data.tdei_project_group_id, 'Test Group ID')

    def test_to_json(self):
        self.upload.data.to_json = MagicMock(return_value={})
        json_data = self.upload.to_json()
        self.assertIsInstance(json_data, dict)
        self.assertEqual(json_data['message_type'], 'workflow_identifier')

    def test_data_from(self):
        message = TEST_DATA
        upload = OSWValidationMessage.data_from(json.dumps(message))
        self.assertIsInstance(upload, OSWValidationMessage)
        self.assertEqual(upload.message_type, 'workflow_identifier')

    def test_upload_to_json(self):
        json_data = self.upload.to_json()
        self.assertTrue(isinstance(json_data, dict))


if __name__ == '__main__':
    unittest.main()
