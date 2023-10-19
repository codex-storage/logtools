from dataclasses import dataclass
from pathlib import Path

from logtools.log.sources.log_parsers import LineNumberLocation
from logtools.log.sources.stream_log_source import StreamLogSource


@dataclass
class FileLineLocation(LineNumberLocation):
    path: Path


class FileLogSource(StreamLogSource):
    def __init__(self, path: Path, parse_datetime=True):
        self.path = path
        super().__init__(self.path.open(encoding='utf-8'), parse_datetime=parse_datetime)

    def __iter__(self):
        try:
            yield from super().__iter__()
        finally:
            self.stream.close()

    def _location(self, line_number: int) -> LineNumberLocation:
        return FileLineLocation(path=self.path, line_number=line_number)
