import abc
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Generic, Iterator

TLocation = TypeVar('TLocation')


@dataclass
class LineNumberLocation:
    """Commonly used location type which tracks the line number of a log line with respect to a given source."""
    line_number: int


@dataclass
class RawLogLine(Generic[TLocation]):
    """
    A :class:`RawLogLine` is a log line that has not been parsed. It contains the raw text of the line and a
    location, when that can be meaningfully established by the input source.
    """
    location: TLocation
    raw: str


TLogLine = TypeVar('TLogLine', bound=RawLogLine)


@dataclass
class TimestampedLogLine(RawLogLine[TLocation]):
    """
    A :class:`TimestampedLogLine` is a log line with a known timestamp.
    """
    timestamp: datetime


class LogSource(ABC, Generic[TLogLine]):
    @abc.abstractmethod
    def __iter__(self) -> Iterator[TLogLine]:
        ...
