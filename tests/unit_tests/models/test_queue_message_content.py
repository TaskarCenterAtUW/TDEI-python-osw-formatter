import os
import json
import unittest
from src.models.queue_message_content import ValidationResult, Request, Meta, Response, to_json

current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../../')))
parent_dir = os.path.dirname(current_dir)

TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/osw-upload.json')

TEST_FILE = open(TEST_JSON_FILE)
TEST_DATA = json.loads(TEST_FILE.read())


class TestRequest(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA['data']['request']
        self.request = Request(data)

    def test_tdei_project_group_id(self):
        self.assertEqual(self.request.tdei_project_group_id, '0b41ebc5-350c-42d3-90af-3af4ad3628fb')
        self.request.tdei_project_group_id = 'Test project group ID'
        self.assertEqual(self.request.tdei_project_group_id, 'Test project group ID')

    def test_collected_by(self):
        self.assertEqual(self.request.collected_by, '6D3E5B8C-FB16-4B6A-9436-72FD24756CC9')
        self.request.collected_by = 'Test Collected By'
        self.assertEqual(self.request.collected_by, 'Test Collected By')

    def test_collection_date(self):
        self.assertEqual(self.request.collection_date, '2022-11-22T09:43:07.978Z')
        self.request.collection_date = 'Test Collected Date'
        self.assertEqual(self.request.collection_date, 'Test Collected Date')

    def test_collection_method(self):
        self.assertEqual(self.request.collection_method, 'manual')
        self.request.collection_method = 'Test Collected Method'
        self.assertEqual(self.request.collection_method, 'Test Collected Method')

    def test_publication_date(self):
        self.assertEqual(self.request.publication_date, '2022-11-22T09:43:07.978Z')
        self.request.publication_date = 'Test Publication Date'
        self.assertEqual(self.request.publication_date, 'Test Publication Date')

    def test_data_source(self):
        self.assertEqual(self.request.data_source, 'local')
        self.request.data_source = 'Test Data Source'
        self.assertEqual(self.request.data_source, 'Test Data Source')

    def test_polygon(self):
        self.request.polygon = {
            'test': 'Polygon'
        }
        self.assertEqual(self.request.polygon, {
            'test': 'Polygon'
        })

    def test_osw_schema_version(self):
        self.assertEqual(self.request.osw_schema_version, '1.0.0')
        self.request.osw_schema_version = '1.1.0'
        self.assertEqual(self.request.osw_schema_version, '1.1.0')


class TestMeta(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA['data']['meta']
        self.meta = Meta(data)

    def test_file_upload_path(self):
        self.assertEqual(self.meta.file_upload_path,
                         'https://tdeisamplestorage.blob.core.windows.net/osw/test_upload/osw.zip')
        self.meta.file_upload_path = 'Test file path'
        self.assertEqual(self.meta.file_upload_path, 'Test file path')

    def test_is_valid(self):
        self.assertEqual(self.meta.isValid, True)
        self.meta.isValid = False
        self.assertEqual(self.meta.isValid, False)

    def test_validation_message(self):
        self.assertEqual(self.meta.validationMessage, '')
        self.meta.validationMessage = 'Test Message'
        self.assertEqual(self.meta.validationMessage, 'Test Message')

    def test_download_osm_url(self):
        self.meta.download_osm_url = 'Test OSM URL'
        self.assertEqual(self.meta.download_osm_url, 'Test OSM URL')

    def test_download_xml_url(self):
        self.assertEqual(self.meta.download_xml_url, '')
        self.meta.download_xml_url = 'Download XML URL'
        self.assertEqual(self.meta.download_xml_url, 'Download XML URL')


class TestResponse(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA['data']['response']
        self.response = Response(data)

    def test_success(self):
        self.assertEqual(self.response.success, True)
        self.response.success = False
        self.assertEqual(self.response.success, False)

    def test_message(self):
        self.assertEqual(self.response.message,
                         'File uploaded for the Project Group : 0b41ebc5-350c-42d3-90af-3af4ad3628fb with tdei record id : c8c76e89f30944d2b2abd2491bd95337')
        self.response.message = 'Successful'
        self.assertEqual(self.response.message, 'Successful')


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
