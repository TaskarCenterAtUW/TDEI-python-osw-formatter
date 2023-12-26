import unittest
import HtmlTestRunner

# Define your test cases
from tests.unit_tests.test_main import TestApp
from tests.unit_tests.models.test_osw_validation_data import TestOSWValidationData
from tests.unit_tests.models.test_osw_ondemand_request import TestOSWOnDemandRequest
from tests.unit_tests.service.test_osw_formatter_service import TestOSWFomatterService
from tests.unit_tests.models.test_osw_ondemand_response import TestOSWOnDemandResponse
from tests.unit_tests.models.test_osw_validation_message import TestOSWValidationMessage
from tests.unit_tests.test_osw_format import TestOSWFormat, TestOSMFormat, TestOSWFormatDownload, TesOSWFormatCleanUp
from tests.unit_tests.models.test_queue_message_content import TestToJson, TestValidationResult

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    # Add your test cases to the test suite
    test_suite.addTest(unittest.makeSuite(TestApp))
    test_suite.addTest(unittest.makeSuite(TestOSWValidationData))
    test_suite.addTest(unittest.makeSuite(TestOSWOnDemandRequest))
    test_suite.addTest(unittest.makeSuite(TestOSWFomatterService))
    test_suite.addTest(unittest.makeSuite(TestOSWOnDemandResponse))
    test_suite.addTest(unittest.makeSuite(TestOSWValidationMessage))
    test_suite.addTest(unittest.makeSuite(TestOSWFormat))
    test_suite.addTest(unittest.makeSuite(TestOSMFormat))
    test_suite.addTest(unittest.makeSuite(TestOSWFormatDownload))
    test_suite.addTest(unittest.makeSuite(TesOSWFormatCleanUp))
    test_suite.addTest(unittest.makeSuite(TestToJson))
    test_suite.addTest(unittest.makeSuite(TestValidationResult))

    # Define the output file for the HTML report
    output_file = 'test_report.html'
    report_name = f'unit_test_report'

    # Open the output file in write mode
    with open(output_file, 'w') as f:
        # Create an HTMLTestRunner instance with the output file and customize the template
        runner = HtmlTestRunner.HTMLTestRunner(stream=f, report_name=report_name, report_title='OSW Test Report',
                                               add_timestamp=True, combine_reports=True)

        # Run the test suite with the HTMLTestRunner
        runner.run(test_suite)

    print(f'\nRunning the tests complete.. see the report at {output_file}')
