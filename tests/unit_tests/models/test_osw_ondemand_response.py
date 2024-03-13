import unittest
from src.models.osw_ondemand_response import OSWOnDemandResponse, ResponseData


class TestOSWOnDemandResponse(unittest.TestCase):

    def test_init(self):
        # Test initialization of OSWOnDemandResponse
        message_type = 'on_demand_response'
        message_id = '123456'
        data = {
            'sourceUrl': 'https://example.com/source.zip',
            'jobId': '789',
            'source': 'osw',
            'target': 'osm',
            'status': 'completed',
            'formattedUrl': 'https://example.com/formatted.zip',
            'success': True,
            'message': 'Formatting successful'
        }

        osw_response = OSWOnDemandResponse(messageType=message_type, messageId=message_id, data=data)

        self.assertEqual(osw_response.messageType, message_type)
        self.assertEqual(osw_response.messageId, message_id)
        self.assertIsInstance(osw_response.data, ResponseData)
        self.assertEqual(osw_response.data.sourceUrl, data['sourceUrl'])
        self.assertEqual(osw_response.data.jobId, data['jobId'])
        self.assertEqual(osw_response.data.source, data['source'])
        self.assertEqual(osw_response.data.target, data['target'])
        self.assertEqual(osw_response.data.status, data['status'])
        self.assertEqual(osw_response.data.formattedUrl, data['formattedUrl'])
        self.assertEqual(osw_response.data.success, data['success'])
        self.assertEqual(osw_response.data.message, data['message'])

    def test_post_init(self):
        # Test post-init behavior
        message_type = 'on_demand_response'
        message_id = '123456'
        data = {
            'sourceUrl': 'https://example.com/source.zip',
            'jobId': '789',
            'source': 'osw',
            'target': 'osm',
            'status': 'completed',
            'formattedUrl': 'https://example.com/formatted.zip',
            'success': True,
            'message': 'Formatting successful'
        }

        osw_response = OSWOnDemandResponse(messageType=message_type, messageId=message_id, data=data)

        # Ensure data is an instance of ResponseData after __post_init__
        self.assertIsInstance(osw_response.data, ResponseData)

    def test_invalid_data_type(self):
        # Test when data is not a dictionary
        with self.assertRaises(TypeError):
            OSWOnDemandResponse(messageType='on_demand_response', messageId='123456', data='invalid_data_type')

    def test_missing_data_field(self):
        # Test when 'data' field is missing
        with self.assertRaises(TypeError):
            OSWOnDemandResponse(messageType='on_demand_response', messageId='123456')

    def test_missing_required_data_fields(self):
        # Test when some required fields are missing in the 'data' dictionary
        incomplete_data = {
            'sourceUrl': 'https://example.com/source.zip',
            'jobId': '789',
            'source': 'osw',
            'status': 'completed',
            'formattedUrl': 'https://example.com/formatted.zip',
            # 'target' and 'formattedUrl' are missing
            'success': True,
            'message': 'Formatting successful'
        }

        with self.assertRaises(TypeError):
            OSWOnDemandResponse(messageType='on_demand_response', messageId='123456', data=incomplete_data)


if __name__ == '__main__':
    unittest.main()
