# data part of it

class OSWValidationData:
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

def remove_underscore(string: str):
    return string if not string.startswith('_') else string[1:]


def to_json(data: object):
    result = {}
    for key in data:
        value = data[key]
        key = remove_underscore(key)
        result[key] = value

    return result