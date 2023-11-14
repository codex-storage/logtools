from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from logtools.log.base import LogSource, RawLogLine, LineNumberLocation


@dataclass
class FileLineLocation(LineNumberLocation):
    path: Path


class FileLogSource(LogSource[RawLogLine[FileLineLocation]]):
    def __init__(self, path: Path):
        self.path = path

    def __iter__(self) -> Iterator[RawLogLine[FileLineLocation]]:
        with self.path.open(encoding='utf-8') as infile:
            for i, raw_string in enumerate(infile, start=1):
                yield RawLogLine(
                    location=FileLineLocation(path=self.path, line_number=i),
                    raw=raw_string
                )
