# Message containing on demand request for osw formatting

from dataclasses import dataclass


@dataclass
class RequestData:
    sourceUrl: str
    jobId: str
    source: str
    target: str


@dataclass
class OSWOnDemandRequest:
    messageType: str
    messageId: str
    data: RequestData

    def __post_init__(self):
        self.data = RequestData(**self.data)
