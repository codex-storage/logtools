from datetime import datetime
from typing import Callable, Iterator

from logtools.log.base import LogSource, TLogLine, TimestampedLogLine, TLocation


class FilteredSource(LogSource[TLogLine]):
    def __init__(self, source: LogSource[TLogLine], predicate: Callable[[TLogLine], bool]):
        self.source = source
        self.predicate = predicate

    def __iter__(self) -> Iterator[TLogLine]:
        for line in self.source:
            if self.predicate(line):
                yield line


def timestamp_range(start: datetime, end: datetime) -> Callable[[TimestampedLogLine[TLocation]], bool]:
    def predicate(line: TimestampedLogLine[TLocation]):
        return start <= line.timestamp <= end

    return predicate
