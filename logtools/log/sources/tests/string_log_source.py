from dataclasses import dataclass

from logtools.log.sources.log_source import LogSource, TrackedLogLine


@dataclass
class ParseLocation:
    name: str
    number: int


class StringLogSource(LogSource[TrackedLogLine[ParseLocation]]):
    def __init__(self, name: str, lines: str):
        self.name = name
        self.lines = lines

    def __iter__(self):
        for line_number, line in enumerate(self.lines.splitlines(), start=1):
            parsed = TrackedLogLine.from_str(line, parse_datetime=True)
            parsed.location = ParseLocation(self.name, line_number)

            yield parsed
