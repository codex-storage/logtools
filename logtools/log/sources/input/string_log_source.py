from dataclasses import dataclass
from io import StringIO
from typing import Iterator

from logtools.log.base import LogSource, RawLogLine, LineNumberLocation


@dataclass
class ParseLocation(LineNumberLocation):
    name: str


class StringLogSource(LogSource[RawLogLine[ParseLocation]]):
    def __init__(self, lines: str, name: str = 'unnamed'):
        self.name = name
        self.stream = StringIO(lines)

    def __iter__(self) -> Iterator[RawLogLine[ParseLocation]]:
        for line_number, line in enumerate(self.stream, start=1):
            yield RawLogLine(
                location=ParseLocation(name=self.name, line_number=line_number),
                raw=line
            )
