# TDEI Python OSW Validation Service Unit Test Cases

## Purpose


This document details the unit test cases for the [TDEI-python-osw-formatter](https://github.com/TaskarCenterAtUW/TDEI-python-osw-formatter)

------------

## Test Framework

Unit test cases are to be written using [Python Unittest](https://docs.python.org/3/library/unittest.html)

------------
## Test Cases


### Test cases table definitions 
- **Component** -> Specifies the code component 
- **Class Under Test** -> Target method name
- **Test Target** -> Specific requirement to test_ ex. Functional, security etc.
- **Scenario** -> Requirement to test
- **Expectation** -> Expected result from executed scenario

### Python unittest code pattern

```python
import unittest

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
```


### Test cases

| Component   | Class Under Test       | Test Target | Scenario                                                            | Expectation                                                        | Status             |
|-------------|------------------------|-------------|---------------------------------------------------------------------|--------------------------------------------------------------------|--------------------|
| Model       | Upload                 | Functional  | When requested with upload data                                     | Expect to return same upload data                                  | :white_check_mark: |
| Model       | Upload                 | Functional  | When requested with upload data_from                                | Expect to return same upload data_from                             | :white_check_mark: |
| Model       | Upload                 | Functional  | When requested with upload message                                  | Expect to return same upload message                               | :white_check_mark: |
| Model       | Upload                 | Functional  | When requested with upload id                                       | Expect to return same upload id                                    | :white_check_mark: |
| Model       | Upload                 | Functional  | When requested with upload type                                     | Expect to return same upload type                                  | :white_check_mark: |
| Model       | Upload                 | Functional  | When requested with upload publish date                             | Expect to return same upload publish date                          | :white_check_mark: |
| Model       | Upload                 | Functional  | When requested with upload to_json                                  | Expect to return same dict                                         | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| Model       | UploadData             | Functional  | When requested with stage parameter                                 | Expect to return stage                                             | :white_check_mark: |
| Model       | UploadData             | Functional  | When requested with tdei_project_group_id parameter                           | Expect to return tdei_project_group_id                                       | :white_check_mark: |
| Model       | UploadData             | Functional  | When requested with tdei_record_id parameter                        | Expect to return tdei_record_id                                    | :white_check_mark: |
| Model       | UploadData             | Functional  | When requested with user_id parameter                               | Expect to return user_id                                           | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| Model       | TestRequest            | Functional  | When requested with tdei_project_group_id parameter                           | Expect to return tdei_project_group_id                                       | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| Model       | TestMeta               | Functional  | When requested with file_upload_path parameter                      | Expect to return file_upload_path                                  | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| Model       | TestResponse           | Functional  | When requested with response parameter                              | Expect to return either True or False                              | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| OSWFomatter | TestOSWFormatter       | Functional  | When requested for format function                                  | Expect to return format                                            | :white_check_mark: |
| OSWFomatter | TestOSWFormatter       | Functional  | When requested for format function                                  | Expect to return format and generate xml file in directory storage | :white_check_mark: |
| OSWFomatter | TestOSWFormatter       | Functional  | When requested for format function with invalid parameters          | Expect to fail                                                     | :white_check_mark: |
| OSWFomatter | TestOSWFormatter       | Functional  | When requested for download_single_file function                    | Expect to return True                                              | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| OSWFomatter | TestOSWFormatDownload  | Functional  | When requested for download_single_file function withvalid endpoint | Expect to download files in local storage                          | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| OSWFomatter | TesOSWFormatCleanUp    | Functional  | When requested for clean_up function if file exists                 | Expect to remove that file                                         | :white_check_mark: |
| OSWFomatter | TesOSWFormatCleanUp    | Functional  | When requested for clean_up function if folder exists               | Expect to remove that folder                                       | :white_check_mark: |
| OSWFomatter | TesOSWFormatCleanUp    | Functional  | When requested for clean_up function id file not exists             | Expect to raise exception                                          | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| OSWFomatter | TestOSWFormatter       | Functional  | When calling subscribe function                                     | Expect to return a message                                         | :white_check_mark: |
| OSWFomatter | TestOSWFormatter       | Functional  | When calling send_status function with valid parameters             | Expect to return valid parameters                                  | :white_check_mark: |
| OSWFomatter | TestOSWFormatter       | Functional  | When calling send_status function with upload url                   | Expect to upload the file to container                             | :white_check_mark: |
| OSWFomatter | TestOSWFormatter       | Functional  | When calling send_status function with invalid parameters           | Expect to return a invalid message                                 | :white_check_mark: |
| OSWFomatter | TestOSWFormatter       | Functional  | When calling upload_to_azure function with valid parameters         | Expect to upload the file to container                             | :white_check_mark: |
| OSWFomatter | TestOSWFormatter       | Functional  | When calling upload_to_azure function with invalid parameters       | Expect not to upload the file to container                         | :white_check_mark: |
| --          | --                     | --          | --                                                                  | --                                                                 | --                 |
| Server      | TestApp                | Functional  | When calling get_settings function                                  | Expect to return env variables                                     | :white_check_mark: |
| Server      | TestApp                | Functional  | When calling ping function                                          | Expect to return 200                                               | :white_check_mark: |
| Server      | TestApp                | Functional  | When calling root function                                          | Expect to return 200                                               | :white_check_mark: |


## Integration Test cases
In case of integration tests, the system will look for all the integration points to be tested

| Component   | Feature under test     | Scenario                                                   | Expectation                                                                                              | Status              |
|-------------|------------------------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|---------------------|
| OSWFomatter | Servicebus Integration | Subscribe to upload topic to verify servicebus integration | Expect to return message                                                                                 | :white_check_mark:  |
| OSWFomatter | Servicebus Integration | Should publish a message to be received on topic           | Expect to receive message on target topic                                                                | :white_check_mark:  |
| OSWFomatter | Storage Integration    | Fetching a file returns a file entity                      | Expect to return the file entity                                                                         | :white_check_mark:  |
| OSWFomatter | Storage Integration    | Should upload to storage container                         | Expect to return the uploaded url                                                                        | :white_check_mark:  |
| OSWFomatter | Functional             | Ween calling format function                               | Expect to format the file, download it to local and upload it to azure container and publish the message | :white_check_mark:  |

