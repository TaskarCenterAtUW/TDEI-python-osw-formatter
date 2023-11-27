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
            'polygon': {'coordinates': [1, 2, 3]},
            'request': {'param1': 'value1'},
            'meta': {'param2': 'value2'},
            'response': {'param3': 'value3'},
            'stage': 'test_stage',
            'tdei_record_id': 'test_id',
            'tdei_project_group_id': 'group_id',
            'user_id': 'user123'
        }
        validation_data = OSWValidationData(data)

        self.assertEqual(validation_data.stage, 'test_stage')
        self.assertEqual(validation_data.tdei_record_id, 'test_id')
        self.assertEqual(validation_data.tdei_project_group_id, 'group_id')
        self.assertEqual(validation_data.user_id, 'user123')

        self.assertIsInstance(validation_data.request, Request)
        self.assertIsInstance(validation_data.meta, Meta)
        self.assertIsInstance(validation_data.response, Response)

    def test_state(self):
        validation_data = OSWValidationData(self.data)
        validation_data.stage = 'new_stage'

        self.assertEqual(validation_data.stage, 'new_stage')

    def test_tdei_record_id(self):
        validation_data = OSWValidationData(self.data)
        validation_data.tdei_record_id = 'TEST_RECORD_ID'

        self.assertEqual(validation_data.tdei_record_id, 'TEST_RECORD_ID')

    def test_tdei_project_group_id(self):
        validation_data = OSWValidationData(self.data)
        validation_data.tdei_project_group_id = 'TEST_PROJECT_ID'

        self.assertEqual(validation_data.tdei_project_group_id, 'TEST_PROJECT_ID')

    def test_user_id(self):
        validation_data = OSWValidationData(self.data)
        validation_data.user_id = 'TEST_USER_ID'

        self.assertEqual(validation_data.user_id, 'TEST_USER_ID')

    def test_to_json(self):
        data = {
            'request': {'param1': 'value1'},
            'meta': {'param2': 'value2'},
            'response': {'param3': 'value3'},
            'stage': 'test_stage',
            'tdei_record_id': 'test_id',
            'tdei_project_group_id': 'group_id',
            'user_id': 'user123'
        }
        validation_data = OSWValidationData(data)

        json_data = validation_data.to_json()

        self.assertIn('stage', json_data)
        self.assertIn('tdei_record_id', json_data)
        self.assertIn('tdei_project_group_id', json_data)
        self.assertIn('user_id', json_data)
        self.assertIn('request', json_data)
        self.assertIn('meta', json_data)
        self.assertIn('response', json_data)

        self.assertEqual(json_data['stage'], 'test_stage')
        self.assertEqual(json_data['tdei_record_id'], 'test_id')
        self.assertEqual(json_data['tdei_project_group_id'], 'group_id')
        self.assertEqual(json_data['user_id'], 'user123')

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
