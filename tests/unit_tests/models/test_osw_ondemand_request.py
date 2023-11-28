import unittest
from src.models.osw_ondemand_request import OSWOnDemandRequest


class TestOSWOnDemandRequest(unittest.TestCase):

    def test_equal_instances(self):
        request_instance_1 = OSWOnDemandRequest('url1', '123', 'source1', 'target1')
        request_instance_2 = OSWOnDemandRequest('url1', '123', 'source1', 'target1')
        request_instance_3 = OSWOnDemandRequest('url2', '456', 'source2', 'target2')

        self.assertEqual(request_instance_1, request_instance_2)
        self.assertNotEqual(request_instance_1, request_instance_3)
        self.assertNotEqual(request_instance_2, request_instance_3)

    def test_repr(self):
        request_instance = OSWOnDemandRequest('url', '123', 'source', 'target')
        self.assertEqual(repr(request_instance),
                         "OSWOnDemandRequest(sourceUrl='url', jobId='123', source='source', target='target')")

    def test_str(self):
        request_instance = OSWOnDemandRequest('url', '123', 'source', 'target')
        self.assertEqual(str(request_instance),
                         "OSWOnDemandRequest(sourceUrl='url', jobId='123', source='source', target='target')")


if __name__ == '__main__':
    unittest.main()
