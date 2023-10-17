from datetime import datetime
from typing import Callable

from logtools.log.sources.log_source import LogSource, TLocation, TrackedLogLine


class FilteredSource(LogSource[TrackedLogLine[TLocation]]):
    def __init__(self, source: LogSource, predicate: Callable[[TrackedLogLine[TLocation]], bool]):
        self.source = source
        self.predicate = predicate

    def __iter__(self):
        for line in self.source:
            if self.predicate(line):
                yield line


def timestamp_range(start: datetime, end: datetime):
    def predicate(line: TrackedLogLine[TLocation]):
        return start <= line.timestamp <= end

    return predicate
