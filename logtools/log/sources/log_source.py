from collections.abc import Iterable
from typing import TypeVar, Generic

from logtools.log.log_line import LogLine

TLocation = TypeVar('TLocation')


class TrackedLogLine(LogLine, Generic[TLocation]):
    location: TLocation


LogSource = Iterable[TrackedLogLine[TLocation]]
