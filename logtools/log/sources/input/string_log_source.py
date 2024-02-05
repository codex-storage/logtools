from dataclasses import dataclass
from io import StringIO
from typing import Iterator

from logtools.log.base import LogSource, RawLogLine, LineNumberLocation
from logtools.log.sources.input.textio_log_source import TextIOLogSource


@dataclass
class ParseLocation(LineNumberLocation):
    name: str


class StringLogSource(TextIOLogSource[ParseLocation]):
    def __init__(self, lines: str, name: str = 'unnamed'):
        super().__init__(StringIO(lines))
        self.name = name

    def _location(self, line_no: int):
        return ParseLocation(name=self.name, line_number=line_no)
