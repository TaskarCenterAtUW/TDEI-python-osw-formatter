import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from src.osw_format import OSWFormat

DOWNLOAD_FILE_PATH = f'{Path.cwd()}/downloads'
SAVED_FILE_PATH = f'{Path.cwd()}/tests/unit_tests/test_files'


class TestOSWFormat(unittest.TestCase):
    @patch.object(OSWFormat, 'download_single_file')
    def setUp(self, mock_download_single_file):
        file_path = f'{SAVED_FILE_PATH}/osw.zip'

        with patch.object(OSWFormat, '__init__', return_value=None):
            self.formatter = OSWFormat(file_path=file_path, storage_client=MagicMock(), prefix='test')
            self.formatter.download_dir = DOWNLOAD_FILE_PATH
            self.formatter.file_path = file_path
            self.formatter.file_relative_path = f'{SAVED_FILE_PATH}/osw.zip'
            self.formatter.container_name = None
            self.formatter.prefix = 'test'
            mock_download_single_file.return_value = f'{DOWNLOAD_FILE_PATH}/osw.zip'
            self.formatter.download_single_file = MagicMock(return_value=file_path)
            self.formatter.storage_client = MagicMock()
            self.formatter.storage_client.get_file_from_url = MagicMock()

    def tearDown(self):
        pass

    @patch.object(OSWFormat, 'clean_up')
    def test_format_with_valid_file(self, mock_clean_up):
        mock_clean_up.return_value = None
        result = self.formatter.format()
        self.assertTrue(result.status)

    @patch.object(OSWFormat, 'clean_up')
    def test_format_with_valid_file_should_generate_xml_file(self, mock_clean_up):
        mock_clean_up.return_value = None
        result = self.formatter.format()
        self.assertTrue(result.status)
        self.assertTrue(os.path.exists(result.generated_files))
        self.assertEqual(os.path.basename(result.generated_files), 'test.graph.osm.xml')

    @patch.object(OSWFormat, 'clean_up')
    def test_format_with_invalid_file(self, mock_clean_up):
        file_path = f'{SAVED_FILE_PATH}/test_file.txt'
        self.formatter.file_path = file_path
        self.formatter.file_relative_path = f'{SAVED_FILE_PATH}/test_file.txt'
        mock_clean_up.return_value = None
        with self.assertRaises(Exception):
            self.formatter.format()

    def test_download_single_file(self):
        file_path = f'{SAVED_FILE_PATH}/osw.zip'
        downloaded_file_path = self.formatter.download_single_file(file_upload_path=file_path)
        self.assertEqual(downloaded_file_path, file_path)


class TestOSMFormat(unittest.TestCase):
    @patch.object(OSWFormat, 'download_single_file')
    def setUp(self, mock_download_single_file):
        file_path = f'{SAVED_FILE_PATH}/wa.microsoft.osm.pbf'

        with patch.object(OSWFormat, '__init__', return_value=None):
            self.formatter = OSWFormat(file_path=file_path, storage_client=MagicMock(), prefix='test')
            self.formatter.download_dir = DOWNLOAD_FILE_PATH
            self.formatter.file_path = file_path
            self.formatter.file_relative_path = f'{SAVED_FILE_PATH}/wa.microsoft.osm.pbf'
            self.formatter.container_name = None
            self.formatter.prefix = 'test'
            mock_download_single_file.return_value = f'{DOWNLOAD_FILE_PATH}/wa.microsoft.osm.pbf'
            self.formatter.download_single_file = MagicMock(return_value=file_path)
            self.formatter.storage_client = MagicMock()
            self.formatter.storage_client.get_file_from_url = MagicMock()

    def tearDown(self):
        pass

    @patch.object(OSWFormat, 'clean_up')
    async def test_format_with_valid_file(self, mock_clean_up):
        mock_clean_up.return_value = None
        result = await self.formatter.format()
        self.assertTrue(result.status)

    @patch.object(OSWFormat, 'clean_up')
    def test_format_with_valid_file_should_generate_pbf_file(self, mock_clean_up):
        mock_clean_up.return_value = None
        result = self.formatter.format()
        self.assertTrue(result.status)
        files = result.generated_files
        self.assertLessEqual(len(files), 6)
        self.assertTrue(os.path.exists(files[0])) # one is enough

    @patch.object(OSWFormat, 'clean_up')
    async def test_format_with_invalid_file(self, mock_clean_up):
        file_path = f'{SAVED_FILE_PATH}/test_file.txt'
        self.formatter.file_path = file_path
        self.formatter.file_relative_path = f'{SAVED_FILE_PATH}/test_file.txt'
        mock_clean_up.return_value = None
        result = await self.formatter.format()
        self.assertIsNone(result)

    def test_download_single_file(self):
        file_path = f'{SAVED_FILE_PATH}/wa.microsoft.osm.pbf'
        downloaded_file_path = self.formatter.download_single_file(file_upload_path=file_path)
        self.assertEqual(downloaded_file_path, file_path)

    def test_create_zip(self):
        file_paths = []
        for i in range(3):
            file_path = os.path.join(self.formatter.download_dir, f'test_file_{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f'Test content for file {i}')
            file_paths.append(file_path)

        zip_filename = self.formatter.create_zip(file_paths)
        self.assertTrue(os.path.isfile(zip_filename))

        for file_path in file_paths:
            self.assertFalse(os.path.exists(file_path))


class TestOSWFormatDownload(unittest.TestCase):
    @patch.object(OSWFormat, 'download_single_file')
    def setUp(self, mock_download_single_file):
        file_path = f'{SAVED_FILE_PATH}/osw.zip'

        with patch.object(OSWFormat, '__init__', return_value=None):
            self.formatter = OSWFormat(file_path=file_path, storage_client=MagicMock(), prefix='test')
            self.formatter.file_path = file_path
            self.formatter.file_relative_path = 'osw.zip'
            self.formatter.download_dir = DOWNLOAD_FILE_PATH
            self.formatter.container_name = None
            mock_download_single_file.return_value = file_path

    def tearDown(self):
        pass

    def test_download_single_file_success(self):
        # Arrange
        file_upload_path = DOWNLOAD_FILE_PATH
        self.formatter.storage_client = MagicMock()
        self.formatter.storage_client.get_file_from_url = MagicMock()
        file = MagicMock()
        file.file_path = 'text_file.txt'
        file.get_stream = MagicMock(return_value=b'file_content')
        self.formatter.storage_client.get_file_from_url.return_value = file
        self.formatter.get_unique_id = MagicMock(return_value=f'abc')

        # Act
        result = self.formatter.download_single_file(file_upload_path=file_upload_path)

        

        expected_file_path = f'{self.formatter.download_dir}/abc/text_file.txt'
        file.get_stream.assert_called_once()
        # Assert
        with open(expected_file_path, 'rb') as file:
            self.assertEqual(file.read(), b'file_content')
        self.assertEqual(result, expected_file_path)

    def test_download_single_file_file_not_found(self):
        # Arrange
        mock_file = Mock()
        mock_file.file_path = None

        self.formatter.storage_client = MagicMock()
        self.formatter.storage_client.get_file_from_url = MagicMock()
        self.formatter.storage_client.get_file_from_url.return_value = mock_file

        result = self.formatter.download_single_file(file_upload_path='nonexistent/file/path.zip')

        # Assert
        self.assertIsNone(result)
        mock_file.get_stream.assert_not_called()


class TesOSWFormatCleanUp(unittest.TestCase):

    def test_clean_up_file_exists(self):
        filename = 'file1.txt'
        file_path = f'{DOWNLOAD_FILE_PATH}/{filename}'
        with open(file_path, 'w') as file:
            file.write('Test file content')
        OSWFormat.clean_up(file_path)
        self.assertFalse(os.path.exists(file_path))

    def test_clean_up_folder_exists(self):
        folder_path = f'{DOWNLOAD_FILE_PATH}/test'
        os.makedirs(folder_path)
        OSWFormat.clean_up(folder_path, DOWNLOAD_FILE_PATH)
        self.assertFalse(os.path.exists(folder_path))

    def test_clean_up_not_exists(self):
        non_existent_path = 'nonexistent/file.txt'
        OSWFormat.clean_up(non_existent_path, DOWNLOAD_FILE_PATH)
        self.assertFalse(os.path.exists(non_existent_path))


if __name__ == '__main__':
    unittest.main()
