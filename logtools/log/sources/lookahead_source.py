from typing import Optional

from logtools.log.sources.log_source import TLocation, LogSource, TrackedLogLine


class LookAheadSource(LogSource[TLocation]):
    def __init__(self, source: LogSource[TLocation]):
        self.source = iter(source)
        self._lookahead = next(self.source, None)

    @property
    def peek(self) -> Optional[TrackedLogLine[TLocation]]:
        return self._lookahead

    def __iter__(self):
        return self

    def __next__(self):
        if self._lookahead is None:
            raise StopIteration()

        value = self._lookahead
        self._lookahead = next(self.source, None)
        return value
