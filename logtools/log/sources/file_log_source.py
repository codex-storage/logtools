import sys
from dataclasses import dataclass
from pathlib import Path

from logtools.log.sources.log_source import TrackedLogLine, LogSource


@dataclass
class FileLineLocation:
    path: Path
    line_number: int


class FileLogSource(LogSource[TrackedLogLine[FileLineLocation]]):
    def __init__(self, path: Path, parse_datetime=True):
        self.path = path
        self.parse_datetime = parse_datetime

    def __iter__(self):
        with self.path.open(encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                try:
                    parsed = TrackedLogLine.from_str(line, parse_datetime=True)
                    parsed.location = FileLineLocation(self.path, line_number)

                    yield parsed
                except ValueError:
                    # FIXME we should probably relax parsing restrictions and output
                    #   these too but for now just skip it.
                    print(f'Skip unparseable line: {line}', file=sys.stderr)
