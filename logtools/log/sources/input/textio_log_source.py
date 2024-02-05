from typing import TypeVar, TextIO, Iterator

from logtools.log.base import LineNumberLocation, RawLogLine, LogSource

TTextIOLineLocation = TypeVar('TTextIOLineLocation', bound=LineNumberLocation)


class TextIOLogSource(LogSource[RawLogLine[TTextIOLineLocation]]):
    def __init__(self, source: TextIO):
        self.source = source

    def __iter__(self) -> Iterator[RawLogLine[TTextIOLineLocation]]:
        try:
            for i, raw_string in enumerate(self.source, start=1):
                yield RawLogLine(
                    location=self._location(i),
                    raw=raw_string
                )
        finally:
            self._done()

    def _location(self, line_no: int):
        return LineNumberLocation(line_number=line_no)

    def _done(self):
        pass
