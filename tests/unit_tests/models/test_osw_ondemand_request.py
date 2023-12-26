import unittest
from src.models.osw_ondemand_request import OSWOnDemandRequest, RequestData


class TestOSWOnDemandRequest(unittest.TestCase):

    def test_init(self):
        # Test initialization of OSWOnDemandResponse
        message_type = 'on_demand_response'
        message_id = '123456'
        data = {
            'sourceUrl': 'https://example.com/source.zip',
            'jobId': '789',
            'source': 'osw',
            'target': 'osm'
        }

        osw_request = OSWOnDemandRequest(messageType=message_type, messageId=message_id, data=data)

        self.assertEqual(osw_request.messageType, message_type)
        self.assertEqual(osw_request.messageId, message_id)
        self.assertIsInstance(osw_request.data, RequestData)
        self.assertEqual(osw_request.data.sourceUrl, data['sourceUrl'])
        self.assertEqual(osw_request.data.jobId, data['jobId'])
        self.assertEqual(osw_request.data.source, data['source'])
        self.assertEqual(osw_request.data.target, data['target'])

    def test_post_init(self):
        # Test post-init behavior
        message_type = 'on_demand_request'
        message_id = '123456'
        data = {
            'sourceUrl': 'https://example.com/source.zip',
            'jobId': '789',
            'source': 'osw',
            'target': 'osm'
        }

        osw_request = OSWOnDemandRequest(messageType=message_type, messageId=message_id, data=data)

        # Ensure data is an instance of ResponseData after __post_init__
        self.assertIsInstance(osw_request.data, RequestData)

    def test_invalid_data_type(self):
        # Test when data is not a dictionary
        with self.assertRaises(TypeError):
            OSWOnDemandRequest(messageType='on_demand_response', messageId='123456', data='invalid_data_type')

    def test_missing_data_field(self):
        # Test when 'data' field is missing
        with self.assertRaises(TypeError):
            OSWOnDemandRequest(messageType='on_demand_response', messageId='123456')

    def test_missing_required_data_fields(self):
        # Test when some required fields are missing in the 'data' dictionary
        incomplete_data = {
            'sourceUrl': 'https://example.com/source.zip',
            'jobId': '789',
            'source': 'osw',
            # 'target' and 'formattedUrl' are missing
        }

        with self.assertRaises(TypeError):
            RequestData(messageType='on_demand_response', messageId='123456', data=incomplete_data)


if __name__ == '__main__':
    unittest.main()
