from dataclasses import dataclass
from io import StringIO

from logtools.log.sources.log_parsers import LogParser
from logtools.log.sources.stream_log_source import StreamLogSource, LineNumberLocation, raw_parser


@dataclass
class ParseLocation(LineNumberLocation):
    name: str


class StringLogSource(StreamLogSource):
    def __init__(self, name: str, lines: str, log_format: LogParser = raw_parser):
        self.name = name
        super().__init__(stream=StringIO(lines), log_format=log_format)

    def _location(self, line_number: int) -> LineNumberLocation:
        return ParseLocation(name=self.name, line_number=line_number)
