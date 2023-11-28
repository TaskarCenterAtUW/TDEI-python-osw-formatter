# Message containing on demand request for osw formatting

from dataclasses import dataclass


@dataclass
class OSWOnDemandResponse:
    sourceUrl: str
    jobId: str
    status: str
    formattedUrl: str
    message: str = ""
