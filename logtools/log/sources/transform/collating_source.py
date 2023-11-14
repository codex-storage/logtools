from typing import Iterator

from logtools.log.base import LogSource, TLogLine


class CollatingSource(LogSource[TLogLine]):
    def __init__(self, *sources: LogSource[TLogLine]):
        self.sources = sources

    def __iter__(self) -> Iterator[TLogLine]:
        for source in self.sources:
            for line in source:
                yield line
