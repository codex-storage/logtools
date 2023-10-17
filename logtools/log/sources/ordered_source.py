import datetime
from typing import Self

from logtools.log.sources.log_source import TrackedLogLine, TLocation
from logtools.log.sources.lookahead_source import LookAheadSource


class OrderedSource(LookAheadSource[TLocation]):
    def __lt__(self, other: Self) -> bool:
        return self._peek.timestamp < other._peek.timestamp  # type: ignore

    def __le__(self, other: Self) -> bool:
        return self._peek.timestamp <= other._peek.timestamp  # type: ignore

    def __gt__(self, other: Self) -> bool:
        return self._peek.timestamp > other._peek.timestamp  # type: ignore

    def __ge__(self, other: Self) -> bool:
        return self._peek.timestamp >= other._peek.timestamp  # type: ignore

    @property
    def _peek(self) -> TrackedLogLine[TLocation]:
        value = self.peek
        if value is None:
            raise ValueError('Cannot order sources that ran out of elements')

        # FIXME too hacky, need to use a proper generic which mypy can track
        if not isinstance(value.timestamp, datetime.datetime):
            raise ValueError('Cannot order sources that do not have parsed timestamps')

        return value
