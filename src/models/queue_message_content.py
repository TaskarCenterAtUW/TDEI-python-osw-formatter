import json


class ValidationResult:
    is_valid: bool
    validation_message: str = ''


class Upload:

    def __init__(self, data: dict):
        upload_data = data.get('data', None)
        self._message = data.get('message', None)
        self._message_type = data.get('messageType', None)
        self._message_id = data.get('messageId', '')
        self._published_date = data.get('publishedDate', None)
        self.data = UploadData(data=upload_data) if upload_data else {}

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, value):
        self._message_type = value

    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, value):
        self._message_id = value

    @property
    def published_date(self):
        return self._published_date

    @published_date.setter
    def published_date(self, value):
        self._published_date = value

    def to_json(self):
        self.data = self.data.to_json()
        return to_json(self.__dict__)

    def data_from(self):
        message = self
        if isinstance(message, str):
            message = json.loads(self)
        if message:
            try:
                return Upload(data=message)
            except Exception as e:
                error = str(e).replace('Upload', 'Invalid parameter,')
                raise TypeError(error)


class UploadData:
    def __init__(self, data: dict):
        polygon = data.get('polygon', None)
        request = data.get('request', None)
        meta = data.get('meta', None)

        response = data.get('response', None)
        self._stage = data.get('stage', '')
        self.request = Request(data=request) if request else {}
        self.meta = Meta(data=meta) if meta else {}
        self.response = Response(data=response) if response else {}
        self._tdei_record_id = data.get('tdei_record_id', '')
        self._tdei_project_group_id = data.get('tdei_project_group_id', '')
        self._user_id = data.get('user_id', '')

    @property
    def stage(self): return self._stage

    @stage.setter
    def stage(self, value): self._stage = value

    @property
    def tdei_record_id(self): return self._tdei_record_id

    @tdei_record_id.setter
    def tdei_record_id(self, value): self._tdei_record_id = value

    @property
    def tdei_project_group_id(self): return self._tdei_project_group_id

    @tdei_project_group_id.setter
    def tdei_project_group_id(self, value): self._tdei_project_group_id = value

    @property
    def user_id(self): return self._user_id

    @user_id.setter
    def user_id(self, value): self._user_id = value

    def to_json(self):
        self.request = to_json(self.request.__dict__)
        self.meta = to_json(self.meta.__dict__)
        self.response = to_json(self.response.__dict__)
        return to_json(self.__dict__)


class Request:
    def __init__(self, data: dict):
        self._tdei_project_group_id = data.get('tdei_project_group_id', '')
        self._collected_by = data.get('collected_by', '')
        self._collection_date = data.get('collection_date', '')
        self._collection_method = data.get('collection_method', '')
        self._publication_date = data.get('publication_date', '')
        self._data_source = data.get('data_source', '')
        self._polygon = data.get('polygon', {})
        self._osw_schema_version = data.get('osw_schema_version', '')

    @property
    def tdei_project_group_id(self): return self._tdei_project_group_id

    @tdei_project_group_id.setter
    def tdei_project_group_id(self, value): self._tdei_project_group_id = value

    @property
    def collected_by(self): return self._collected_by

    @collected_by.setter
    def collected_by(self, value): self._collected_by = value

    @property
    def collection_date(self): return self._collection_date

    @collection_date.setter
    def collection_date(self, value): self._collection_date = value

    @property
    def collection_method(self): return self._collection_method

    @collection_method.setter
    def collection_method(self, value): self._collection_method = value

    @property
    def data_source(self): return self._data_source

    @data_source.setter
    def data_source(self, value): self._data_source = value

    @property
    def polygon(self): return self._polygon

    @polygon.setter
    def polygon(self, value): self._polygon = value

    @property
    def publication_date(self): return self._publication_date

    @publication_date.setter
    def publication_date(self, value): self._publication_date = value

    @property
    def osw_schema_version(self): return self._osw_schema_version

    @osw_schema_version.setter
    def osw_schema_version(self, value): self._osw_schema_version = value


class Meta:
    def __init__(self, data: dict):
        self._file_upload_path = data.get('file_upload_path', '')
        self._isValid = data.get('isValid', False)
        self._validationMessage = data.get('validationMessage', '')
        self.validationTime = 90
        self._download_osm_url = data.get('file_upload_path', '')
        self._download_xml_url = data.get('download_xml_url', '')

    @property
    def file_upload_path(self): return self._file_upload_path

    @file_upload_path.setter
    def file_upload_path(self, value): self._file_upload_path = value

    @property
    def isValid(self): return self._isValid

    @isValid.setter
    def isValid(self, value): self._isValid = value

    @property
    def validationMessage(self): return self._validationMessage

    @validationMessage.setter
    def validationMessage(self, value): self._validationMessage = value

    @property
    def download_osm_url(self): return self._download_osm_url

    @download_osm_url.setter
    def download_osm_url(self, value): self._download_osm_url = value

    @property
    def download_xml_url(self): return self._download_xml_url

    @download_xml_url.setter
    def download_xml_url(self, value): self._download_xml_url = value


class Response:

    def __init__(self, data: dict):
        self._success = data.get('success', False)
        self._message = data.get('message', '')

    @property
    def success(self): return self._success

    @success.setter
    def success(self, value): self._success = value

    @property
    def message(self): return self._message

    @message.setter
    def message(self, value): self._message = value


def remove_underscore(string: str):
    return string if not string.startswith('_') else string[1:]


def to_json(data: object):
    result = {}
    for key in data:
        value = data[key]
        key = remove_underscore(key)
        result[key] = value

    return result
