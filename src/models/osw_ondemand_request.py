# Message containing on demand request for osw formatting

from dataclasses import dataclass


@dataclass
class OSWOnDemandRequest:
    sourceUrl: str
    jobId: str
    source: str
    target: str
