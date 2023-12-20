## Holds the message from osw_validation
## Sample found in osw-validation-output.json
import json
from .osw_validation_data import OSWValidationData


class OSWValidationMessage:

    def __init__(self, data: dict):
        upload_data = data.get('data', None)
        self._message = data.get('message', None)
        self._message_type = data.get('messageType', None)
        self._message_id = data.get('messageId', '')
        self.data = OSWValidationData(data=upload_data) if upload_data else {}

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

    def to_json(self):
        self.data = self.data.to_json()
        return to_json(self.__dict__)

    def data_from(self):
        message = self
        if isinstance(message, str):
            message = json.loads(self)
        if message:
            try:
                return OSWValidationMessage(data=message)
            except Exception as e:
                error = str(e).replace('Upload', 'Invalid parameter,')
                raise TypeError(error)


def remove_underscore(string: str):
    return string if not string.startswith('_') else string[1:]


def to_json(data: object):
    result = {}
    for key in data:
        value = data[key]
        key = remove_underscore(key)
        result[key] = value

    return result
