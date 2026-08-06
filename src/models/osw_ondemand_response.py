# Message containing on demand request for osw formatting

from dataclasses import dataclass
from typing import Optional


@dataclass
class ResponseData:
    sourceUrl: Optional[str] = ''
    jobId: str = ''
    source: Optional[str] = ''
    target: Optional[str] = ''
    status: str = ''
    formattedUrl: Optional[str] = ''
    success: bool = False
    message: str = ''


@dataclass
class OSWOnDemandResponse:
    messageType: str
    messageId: str
    data: ResponseData

    def __post_init__(self):
        self.data = ResponseData(**self.data)
