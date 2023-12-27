import os
import json
import unittest
from src.models.queue_message_content import ValidationResult, Request, Meta, Response, to_json

current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../../')))
parent_dir = os.path.dirname(current_dir)

TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/osw-upload.json')

TEST_FILE = open(TEST_JSON_FILE)
TEST_DATA = json.loads(TEST_FILE.read())


class TestToJson(unittest.TestCase):
    def test_to_json(self):
        data = {
            'key1': 'value1',
            'key2': 'value2'
        }
        result = to_json(data)
        self.assertEqual(result, {'key1': 'value1', 'key2': 'value2'})


class TestValidationResult(unittest.TestCase):
    def test_validation_result_init(self):
        result = ValidationResult()
        result.is_valid = True
        result.validation_message = 'Validated'
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validation_message, 'Validated')


if __name__ == '__main__':
    unittest.main()
