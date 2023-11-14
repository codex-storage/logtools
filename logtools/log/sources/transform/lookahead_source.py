from typing import Optional, Iterator

from logtools.log.base import LogSource, TLogLine


class LookAheadSource(LogSource[TLogLine]):
    def __init__(self, source: LogSource[TLogLine]):
        self.source = iter(source)
        self._lookahead = next(self.source, None)

    @property
    def peek(self) -> Optional[TLogLine]:
        return self._lookahead

    def __iter__(self) -> Iterator[TLogLine]:
        return self

    def __next__(self) -> TLogLine:
        if self._lookahead is None:
            raise StopIteration()

        value = self._lookahead
        self._lookahead = next(self.source, None)
        return value
