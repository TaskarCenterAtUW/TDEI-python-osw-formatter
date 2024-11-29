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

class TestRequest(unittest.TestCase):
    def test_request_init(self):
        data = {
            'tdei_project_group_id': 'test_group_id',
            'collected_by': 'tester',
            'collection_date': '2024-01-01',
            'collection_method': 'manual',
            'publication_date': '2024-02-01',
            'data_source': 'test_source',
            'polygon': {'type': 'Polygon', 'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
            'osw_schema_version': '1.0'
        }
        request = Request(data)

        self.assertEqual(request.tdei_project_group_id, 'test_group_id')
        self.assertEqual(request.collected_by, 'tester')
        self.assertEqual(request.collection_date, '2024-01-01')
        self.assertEqual(request.collection_method, 'manual')
        self.assertEqual(request.publication_date, '2024-02-01')
        self.assertEqual(request.data_source, 'test_source')
        self.assertEqual(request.polygon, data['polygon'])
        self.assertEqual(request.osw_schema_version, '1.0')


class TestMeta(unittest.TestCase):
    def test_meta_init(self):
        data = {
            'file_upload_path': '/path/to/file',
            'isValid': True,
            'validationMessage': 'Validation successful',
            'download_osm_url': '/path/to/osm',
            'download_xml_url': '/path/to/xml'
        }
        meta = Meta(data)
        self.assertEqual(meta.file_upload_path, '/path/to/file')
        self.assertTrue(meta.isValid)
        self.assertEqual(meta.validationMessage, 'Validation successful')
        self.assertEqual(meta.download_osm_url, '/path/to/file')
        self.assertEqual(meta.download_xml_url, '/path/to/xml')


class TestResponse(unittest.TestCase):
    def test_response_init(self):
        data = {
            'success': True,
            'message': 'Operation completed successfully'
        }
        response = Response(data)

        self.assertTrue(response.success)
        self.assertEqual(response.message, 'Operation completed successfully')


if __name__ == '__main__':
    unittest.main()
