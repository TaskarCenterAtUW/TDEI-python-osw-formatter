# Message containing on demand request for osw formatting

from dataclasses import dataclass


@dataclass
class ResponseData:
    sourceUrl: str
    jobId: str
    source: str
    target: str
    status: str
    formattedUrl: str
    success: bool
    message: str


@dataclass
class OSWOnDemandResponse:
    messageType: str
    messageId: str
    data: ResponseData

    def __post_init__(self):
        self.data = ResponseData(**self.data)
