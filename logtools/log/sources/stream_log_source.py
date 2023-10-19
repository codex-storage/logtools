from typing import TextIO

from logtools.log.sources.log_parsers import raw_parser, LineNumberLocation, LogParser
from logtools.log.sources.log_source import LogSource, TrackedLogLine


class StreamLogSource(LogSource[TrackedLogLine[LineNumberLocation]]):
    def __init__(self, stream: TextIO, parse_datetime=True, log_format: LogParser = raw_parser):
        self.stream = stream
        self.format = log_format
        self.parse_datetime = parse_datetime

    def __iter__(self):
        for line_number, line in enumerate(self.format(self.stream), start=1):
            line.location = self._location(line_number)
            yield line

    def _location(self, line_number: int) -> LineNumberLocation:
        return LineNumberLocation(line_number)
