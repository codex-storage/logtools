from typing import Iterator

from logtools.log.sources.log_source import LogSource, TLocation, TrackedLogLine


class CollatingSource(LogSource[TLocation]):
    def __init__(self, *sources: LogSource[TLocation]):
        self.sources = sources

    def __iter__(self) -> Iterator[TrackedLogLine[TLocation]]:
        for source in self.sources:
            for line in source:
                yield line
