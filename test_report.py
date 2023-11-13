import unittest
import HtmlTestRunner

# Define your test cases
from tests.unit_tests.test_formatter import TestOSWFormat, TestOSWFormatDownload, TesOSWFormatCleanUp
from tests.unit_tests.test_main import TestApp
from tests.unit_tests.test_osw_formatter import TestOSWFormatter
from tests.unit_tests.test_queue_message_content import TestUpload, TestUploadData, TestRequest, \
    TestMeta, TestResponse, TestToJson, TestValidationResult

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    # Add your test cases to the test suite
    test_suite.addTest(unittest.makeSuite(TestUpload))
    test_suite.addTest(unittest.makeSuite(TestUploadData))
    test_suite.addTest(unittest.makeSuite(TestRequest))
    test_suite.addTest(unittest.makeSuite(TestMeta))
    test_suite.addTest(unittest.makeSuite(TestResponse))
    test_suite.addTest(unittest.makeSuite(TestToJson))
    test_suite.addTest(unittest.makeSuite(TestValidationResult))
    test_suite.addTest(unittest.makeSuite(TestOSWFormat))
    test_suite.addTest(unittest.makeSuite(TestOSWFormatDownload))
    test_suite.addTest(unittest.makeSuite(TesOSWFormatCleanUp))
    test_suite.addTest(unittest.makeSuite(TestOSWFormatter))
    test_suite.addTest(unittest.makeSuite(TestApp))

    # Define the output file for the HTML report
    output_file = 'test_report.html'

    # Open the output file in write mode
    with open(output_file, 'w') as f:
        # Create an HTMLTestRunner instance with the output file and customize the template
        runner = HtmlTestRunner.HTMLTestRunner(stream=f, report_title='OSW Test Report', combine_reports=True)

        # Run the test suite with the HTMLTestRunner
        runner.run(test_suite)

    print(f'\nRunning the tests complete.. see the report at {output_file}')
