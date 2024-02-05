import re
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Iterator, Optional

from dateutil import parser

from logtools.log.base import LogSource, TLocation, RawLogLine, TimestampedLogLine

_LOG_LINE = re.compile(
    r'(?P<line_type>\w{3}) (?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}\+\d{2}:\d{2}) (?P<message>.*) '
    r'count=(?P<count>\d+)$'
)

_TOPICS = re.compile(r'((\w+=("[^"]+"|\S+) )+)?\w+=("([^"\\]|\\")+"|\S+)$')

_TOPICS_KV = re.compile(r'(?P<key>\w+)=(?P<value>"(?:[^"\\]|\\")+"|\S+)')


class LogLevel(Enum):
    trace = 'TRC'
    debug = 'DBG'
    info = 'INF'
    error = 'ERR'
    warning = 'WRN'
    note = 'NOT'


@dataclass
class ChroniclesLogLine(TimestampedLogLine[TLocation]):
    """
    A :class:`ChroniclesLogLine` is a log line coming from [Chronicles](https://github.com/status-im/nim-chronicles).
    """
    timestamp: datetime
    level: LogLevel
    message: str
    topics: str
    count: Optional[int]

    @property
    def fields(self):
        fields = _TOPICS_KV.findall(self.topics)
        return {key: value for key, value in fields} if fields else {}


class ChroniclesRawSource(LogSource[ChroniclesLogLine[TLocation]]):
    """Parses a Chronicles log from raw text. Other variants could parse from JSON or CSV."""

    def __init__(self, stream: LogSource[RawLogLine[TLocation]]):
        self.stream = stream

    def __iter__(self) -> Iterator[ChroniclesLogLine[TLocation]]:
        for line in self.stream:
            parsed = self._parse_raw(line)
            if not parsed:
                print(f'Skip unparseable line: {line}', file=sys.stderr)
                continue
            parsed.location = line.location
            yield parsed

    @staticmethod
    def _parse_raw(line: RawLogLine[TLocation]) -> Optional[ChroniclesLogLine[TLocation]]:
        parsed = _LOG_LINE.search(line.raw)
        if not parsed:
            return None

        topics = _TOPICS.search(parsed['message'])
        if not topics:
            return None

        return ChroniclesLogLine(
            location=line.location,
            raw=line.raw,
            level=LogLevel(parsed['line_type'].upper()),
            timestamp=parser.parse(parsed['timestamp']),
            message=parsed['message'][:topics.start() - 1].strip(),
            count=int(parsed['count']) if parsed['count'] else None,
            topics=topics.group()
        )
