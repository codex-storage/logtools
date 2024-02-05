from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from logtools.log.base import LogSource, RawLogLine, LineNumberLocation
from logtools.log.sources.input.textio_log_source import TextIOLogSource


@dataclass
class FileLineLocation(LineNumberLocation):
    path: Path


class FileLogSource(TextIOLogSource[FileLineLocation]):
    def __init__(self, path: Path):
        super().__init__(path.open(encoding='utf-8'))
        self.path = path

    def _location(self, line_no: int):
        return FileLineLocation(path=self.path, line_number=line_no)

    def _done(self):
        self.source.close()
