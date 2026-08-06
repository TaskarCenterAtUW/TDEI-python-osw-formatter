import os
import json
import unittest
from src.models.osw_validation_data import OSWValidationData, remove_underscore, to_json
from src.models.queue_message_content import Request, Response, Meta

current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../../')))
parent_dir = os.path.dirname(current_dir)

TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/osw-upload.json')

TEST_FILE = open(TEST_JSON_FILE)
TEST_DATA = json.loads(TEST_FILE.read())


class TestOSWValidationData(unittest.TestCase):

    def setUp(self):
        self.data = TEST_DATA['data']

    def test_init(self):
        data = {
            'tdei_project_group_id': 'group_id',
            'file_upload_path': 'some_url'
        }
        validation_data = OSWValidationData(data)

        self.assertEqual(validation_data.tdei_project_group_id, 'group_id')
        self.assertEqual(validation_data.file_upload_path, 'some_url')

    def test_tdei_project_group_id(self):
        validation_data = OSWValidationData(self.data)
        validation_data.tdei_project_group_id = 'TEST_PROJECT_ID'

        self.assertEqual(validation_data.tdei_project_group_id, 'TEST_PROJECT_ID')

    def test_to_json(self):
        data = {
            'tdei_project_group_id': 'group_id',
            'file_upload_path': 'some_url'
        }
        validation_data = OSWValidationData(data)

        json_data = validation_data.to_json()

        self.assertIn('tdei_project_group_id', json_data)
        self.assertIn('file_upload_path', json_data)

        self.assertEqual(json_data['tdei_project_group_id'], 'group_id')
        self.assertEqual(json_data['file_upload_path'], 'some_url')

    def test_remove_underscore(self):
        underscored_string = '_test_string'
        result = remove_underscore(underscored_string)
        self.assertEqual(result, 'test_string')

        non_underscored_string = 'test_string'
        result = remove_underscore(non_underscored_string)
        self.assertEqual(result, 'test_string')

    def test_to_json_function(self):
        data = {'param1': 'value1', 'param2': 'value2'}
        json_data = to_json(data)
        self.assertIn('param1', json_data)
        self.assertIn('param2', json_data)
        self.assertEqual(json_data['param1'], 'value1')
        self.assertEqual(json_data['param2'], 'value2')


if __name__ == '__main__':
    unittest.main()
