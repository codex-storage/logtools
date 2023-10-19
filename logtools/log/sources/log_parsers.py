import re
import sys
from csv import DictReader
from dataclasses import dataclass

from typing import Callable, TextIO, Optional, cast

from dateutil import parser as tsparser

from logtools.log.log_line import LogLevel
from logtools.log.sources.log_source import TrackedLogLine, LogSource


@dataclass
class LineNumberLocation:
    line_number: int


"""A :class:`LogParser` is a function that takes a raw text stream and returns a :class:`LogSource`, which in turn
is an iterable of parsed lines."""
LogParser = Callable[[TextIO], LogSource[LineNumberLocation]]

LOG_LINE = re.compile(
    r'(?P<line_type>\w{3}) (?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}\+\d{2}:\d{2}) (?P<message>.*) '
    r'count=(?P<count>\d+)$'
)

TOPICS = re.compile(r'((\w+=("[\w\s]+"|\S+) )+)?\w+=("[\w\s]+"|\S+)$')


def parse_raw(line: str, parse_datetime: bool = True) -> Optional[TrackedLogLine[LineNumberLocation]]:
    parsed = LOG_LINE.search(line)
    topics = TOPICS.search(parsed['message'])
    if not parsed or not topics:
        return None

    return TrackedLogLine(
        raw=line,
        level=LogLevel(parsed['line_type'].upper()),
        timestamp=(tsparser.parse(parsed['timestamp']) if parse_datetime
                   else parsed['timestamp']),
        message=parsed['message'][:topics.start() - 1].strip(),
        count=int(parsed['count']) if parsed['count'] else None,
        topics=topics.group()
    )


def raw_parser(stream: TextIO, parse_datetime=True) -> LogSource:
    for line_number, line in enumerate(stream, start=1):
        parsed = parse_raw(line, parse_datetime=parse_datetime)
        if not parsed:
            # FIXME we should probably relax parsing restrictions and output
            #   these too but for now just skip it.
            print(f'Skip unparseable line: {line}', file=sys.stderr)
            continue

        yield parsed


def csv_parser(stream: TextIO, parse_datetime=True) -> LogSource:
    for line_number, line in enumerate(DictReader(stream), start=1):
        try:
            line = TrackedLogLine(
                raw=line['message'],  # FIXME this is NOT the raw line...
                timestamp=line['timestamp'],
                message=line['message'],
                count=int(line['count']) if line['count'] else None,
                topics=line['topics'],
                level=LogLevel[line['level']],
            )

            if parse_datetime:
                line.timestamp = tsparser.parse(cast(str, line.timestamp))
            yield line
        except ValueError:
            print(f'Skip unparseable line: {line}', file=sys.stderr)
