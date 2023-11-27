import unittest
from src.models.osw_ondemand_response import OSWOnDemandResponse


class TestOSWOnDemandResponse(unittest.TestCase):

    def test_equal_instances(self):
        request_instance_1 = OSWOnDemandResponse('url1', '123', 'True', 'formattedUrl1', 'test1')
        request_instance_2 = OSWOnDemandResponse('url1', '123', 'True', 'formattedUrl1', 'test1')
        request_instance_3 = OSWOnDemandResponse('url3', '123', 'False', 'formattedUrl3', 'test3')

        self.assertEqual(request_instance_1, request_instance_2)
        self.assertNotEqual(request_instance_1, request_instance_3)
        self.assertNotEqual(request_instance_2, request_instance_3)

    def test_repr(self):
        response_instance = OSWOnDemandResponse('url', '123', 'True', 'formattedUrl', 'test')
        self.assertEqual(repr(response_instance),
                         "OSWOnDemandResponse(sourceUrl='url', jobId='123', status='True', formattedUrl='formattedUrl', message='test')")

    def test_str(self):
        response_instance = OSWOnDemandResponse('url', '123', 'True', 'formattedUrl', 'test')
        self.assertEqual(str(response_instance),
                         "OSWOnDemandResponse(sourceUrl='url', jobId='123', status='True', formattedUrl='formattedUrl', message='test')")


if __name__ == '__main__':
    unittest.main()
