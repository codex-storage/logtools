import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Union, Self, Optional


class LogLevel(Enum):
    trace = 'TRC'
    debug = 'DBG'
    info = 'INF'
    error = 'ERR'


LOG_LINE = re.compile(
    r'(?P<line_type>\w{3}) (?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}\+\d{2}:\d{2}) (?P<message>.*) '
    r'count=(?P<count>\d+)$'
)


@dataclass
class LogLine:
    raw: str
    level: LogLevel
    line_number: int
    timestamp: Union[str, datetime]
    message: str
    count: Optional[int]

    @classmethod
    def from_str(cls, source: str, parse_datetime: bool = False) -> Self:
        parsed = LOG_LINE.search(source)
        if not parsed:
            raise ValueError(f'Could not parse log line: {source}')

        return cls(
            raw=source,
            level=LogLevel(parsed['line_type'].upper()),
            line_number=0,
            timestamp=(datetime.fromisoformat(parsed['timestamp']) if parse_datetime
                       else parsed['timestamp']),
            message=parsed['message'],
            count=int(parsed['count']) if parsed['count'] else None,
        )
