# TDEI-python-osw-formatter

## Introduction 
Service to Convert the OSW files to OSM files and OSM to OSW files. At the moment, the service does the following:
- Listens to the topic which is mentioned in `.env` file for any new message (that is triggered when a file is uploaded), example  `UPLOAD_TOPIC=osw-validation` 
- Consumes the message and perform following checks - 
  - Download the file locally 
  - File location is in the message `data.meta.file_upload_path`
  - Uses `osm-osw-reformatter` to convert OSM file to OSW file
  - Upload the converted files to `osw` storage containter
  - Adds the `file_upload_path` and `download_xml_url` keys to the original message 
- Publishes the result to the topic mentioned in `.env` file, example `VALIDATION_TOPIC=osw-formatting-service`

## Getting Started
The project is built on Python with FastAPI framework. All the regular nuances for a Python project are valid for this.

### System requirements
| Software   | Version |
|------------|---------|
| Python     | 3.10.x  |
| GDAL       | 3.4.1   |  

### Connectivity to cloud
- Connecting this to cloud will need the following in the `.env` file

```bash
QUEUECONNECTION=xxx
STORAGECONNECTION=xxx
FORMATTER_TOPIC=xxx
FORMATTER_SUBSCRIPTION=xxx
FORMATTER_UPLOAD_TOPIC=xxx
CONTAINER_NAME=xxx
MAX_CONCURRENT_MESSAGES=xx
```

The application connect with the `STORAGECONNECTION` string provided in `.env` file and validates downloaded zipfile using `python-osw-validation` package.
`QUEUECONNECTION` is used to send out the messages and listen to messages.

`MAX_CONCURRENT_MESSAGES` is the maximum number of concurrent messages that the service can handle. If not provided, defaults to 2

## Establishing python env for the project
Running the code base requires a proper Python environment set up. The following lines of code helps one establish such env named `tdei-osw`. replace `tdei-osw` with the name of your choice.

```
conda create -n tdei-osw python==3.10.3 gdal
conda activate tdei-osw
pip install -r requirements.txt
```
Alternatively one can use the `setup_env.sh` script provided with this repo. One can run 
`source ./setup_env.sh`. Once run, the command creates an environment with the name `tdei`

## How to install GDAL   
If for some reason the above conda creation fails to install GDAL, please follow the procedure below.
  
To install the GDAL library (Geospatial Data Abstraction Library) on your system, you can follow the steps below. The specific installation process may vary depending on your operating system.  
  
1. **Linux (Ubuntu/Debian):**  GDAL is available in the Ubuntu and Debian repositories. You can install it using apt: 
    ``` 
    sudo apt update 
    sudo apt install gdal-bin libgdal-dev python3-gdal 
    ```
   
  2.   **Linux (CentOS/RHEL):** On CentOS/RHEL, you can install GDAL using `yum`:
        ``` 
        sudo yum install gdal 
        ```  
	    
  3. **macOS (Homebrew):** If you're using Homebrew on macOS, you can install GDAL with the following command:
      ```
      brew install gdal
      ```
  4. **Windows:** On Windows, you can install GDAL using the GDAL Windows binaries provided by the GIS Internals project:
  
        1. Go to the [GIS Internals download page](https://www.gisinternals.com/release.php).
        2. Choose the GDAL version that matches your system (e.g., 32-bit or 64-bit) and download the core components.
        3. Install the downloaded MSI file.
        4. Make sure to add the GDAL bin directory to your system's PATH variable if it's not added automatically.


### How to Set up and Build
Follow the steps to install the python packages required for both building and running the application

1. Setup virtual environment
    ```
    python3.10 -m venv .venv
    source .venv/bin/activate
    ```

2. Install the dependencies. Run the following command in terminal on the same directory as `requirements.txt`
    ```
    # Installing requirements
    pip install -r requirements.txt
    ```
### How to Run the Server/APIs   

1. The http server by default starts with `8000` port
2. Run server
    ```
    uvicorn src.main:app --reload
    ```
3. By default `get` call on `localhost:8000/health` gives a sample response
4. Other routes include a `ping` with get and post. Make `get` or `post` request to `http://localhost:8000/health/ping`
5. Once the server starts, it will start to listening the subscriber(`FORMATTER_SUBSCRIPTION` should be in env file)

#### Request Format
```json
  {
    "messageId": "tdei_record_id",
    "messageType": "workflow_identifier",
    "data": {
      "file_upload_path": "file_upload_path",
      "tdei_project_group_id": "tdei_project_group_id"
    } 
  }
```

#### Response Format
```json
  {
    "messageId": "tdei_record_id",
    "messageType": "workflow_identifier",
    "data": {
      "file_upload_path": "file_upload_path",
      "tdei_project_group_id": "tdei_project_group_id",
      "source_url": "file_upload_path",
      "formatted_url": "uploaded_url",
      "success": true/false,
      "message": "message" 
    },
  "publishedDate": "published date"
  }
```

### On Demand Request Format
```json
{
  "messageId": "c8c76e89f30944d2b2abd2491bd95337",
  "messageType": "workflow_identifier ON_DEMAND",
  "data": {
    "sourceUrl": "https://tdeisamplestorage.blob.core.windows.net/osw/2023/11/c552d5d1-0719-4647-b86d-6ae9b25327b7/aff14a0d29ab4acbaef639063462e85b/naresh-som-2.zip",
    "jobId": "42",
    "source": "osw",
    "target": "osm"
  }
}
```

### On Demand Response Format
```json
{
  "messageId": "c8c76e89f30944d2b2abd2491bd95337",
  "messageType": "workflow_identifier ON_DEMAND",
  "data": {
    "sourceUrl": "https://tdeisamplestorage.blob.core.windows.net/osw/2023/11/c552d5d1-0719-4647-b86d-6ae9b25327b7/aff14a0d29ab4acbaef639063462e85b/naresh-som-2.zip",
    "jobId": "42",
    "source": "osw",
    "target": "osm",
    "formattedUrl": "https://tdeisamplestorage.blob.core.windows.net/osw/2023/11/c552d5d1-0719-4647-b86d-6ae9b25327b7/aff14a0d29ab4acbaef639063462e85b/naresh-som-2.zip",
    "success": true,
    "message": ""
  }
}
```


### How to Set up and run the Tests

Make sure you have set up the project properly before running the tests, see above for `How to Setup and Build`.

#### How to run test harness
1. Add the new set of test inside `tests/test_harness/tests.json` file like -
    ```
    {
     "Name": "Test Name",
     "Input_file": "test_files/osw_test_case1.json", // Input file path which you want to provide to the test
     "Result": true/false // Defining the test output 
     }
    ```
2. Test Harness would require a valid `.env` file.
3. To run the test harness `python tests/test_harness/run_tests.py` 
#### How to run unit test cases
1. `.env` file is not required for Unit test cases.
2. To run the unit test cases
   1. `python test_report.py`
   2. Above command will run all test cases and generate the html report, in `reports` folder at the root level.
3. To run the coverage
   1. `python -m coverage run --source=src -m unittest discover -s tests/unit_tests`
   2. Above command will run all the unit test cases.
   3. To generate the coverage report in console
      1. `coverage report`
      2. Above command will generate the code coverage report in terminal. 
   4. To generate the coverage report in html.
      1. `coverage html`
      2. Above command will generate the html report, and generated html would be in `htmlcov` directory at the root level.
   5. _NOTE :_ To run the `html` or `report` coverage, 3.i) command is mandatory

#### How to run integration test cases
1. `.env` file is required for integration test cases.
2. To run the integration test cases, run the below command
   1. `python test_integration.py`
   2. Above command will run all integration test cases and generate the html report, in `reports` folder at the root level.


### Messaging

This microservice deals with two topics/queues. 
- upload queue from osw-validation
- formatter queue from osw-formatting-service


#### Incoming
The incoming messages will be from the upload queue `osw-upload`.
The format is mentioned in [osw-upload.json](./src/assets/osw-upload.json)

#### Outgoing
The outgoing messages will be to the `osw-validation` topic.
The format of the message is at [osw-format.json](./src/assets/osw-format.json)

