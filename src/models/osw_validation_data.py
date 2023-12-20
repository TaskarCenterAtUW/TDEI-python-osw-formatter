# data part of it
from .queue_message_content import Request, Response, Meta


class OSWValidationData:
    def __init__(self, data: dict):
        self._tdei_project_group_id = data.get('tdei_project_group_id', '')
        self._file_upload_path = data.get('file_upload_path', '')
        self._source_url = data.get('file_upload_path', '')
        self._formatted_url = data.get('formatted_url', None)
        self._success = data.get('success', False)
        self._message = data.get('message', '')

    @property
    def tdei_project_group_id(self): return self._tdei_project_group_id

    @tdei_project_group_id.setter
    def tdei_project_group_id(self, value): self._tdei_project_group_id = value

    @property
    def file_upload_path(self): return self._file_upload_path

    @file_upload_path.setter
    def file_upload_path(self, value): self._file_upload_path = value

    @property
    def formatted_url(self): return self._formatted_url

    @formatted_url.setter
    def formatted_url(self, value): self._formatted_url = value

    @property
    def success(self): return self._success

    @success.setter
    def success(self, value): self._success = value

    @property
    def message(self): return self._message

    @message.setter
    def message(self, value): self._message = value

    def to_json(self):
        return to_json(self.__dict__)


def remove_underscore(string: str):
    return string if not string.startswith('_') else string[1:]


def to_json(data: object):
    result = {}
    for key in data:
        value = data[key]
        key = remove_underscore(key)
        result[key] = value

    return result
