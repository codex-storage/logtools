from datetime import datetime

import pytest
import pytz

from logtools.log.sources.input.string_log_source import StringLogSource
from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource, ChroniclesLogLine, LogLevel


def test_should_parse_raw_chronicles_logs():
    source = ChroniclesRawSource(
        StringLogSource(
            lines='TRC 2023-10-16 17:28:46.579+00:00 Sending want list to peer                  '
                  'topics="codex blockexcnetwork" tid=1 peer=16U*7mogoM type=WantBlock items=1 count=870781'
        )
    ).__iter__()

    line = next(source)

    assert line.level == LogLevel.trace
    assert line.timestamp == datetime(2023, 10, 16, 17, 28, 46,
                                      579000, tzinfo=pytz.utc)
    assert line.message == 'Sending want list to peer'
    assert line.topics == 'topics="codex blockexcnetwork" tid=1 peer=16U*7mogoM type=WantBlock items=1'
    assert line.count == 870781


def test_should_skip_unparseable_lines():
    source = ChroniclesRawSource(StringLogSource(lines='This is not a log line')).__iter__()
    with pytest.raises(StopIteration):
        next(source)


def test_should_parse_chronicles_fields():
    line = ChroniclesLogLine(
        location=None,
        message='Sending want list to peer',
        topics='topics="codex blockexcnetwork" tid=1 peer=16U*7mogoM '
               'type=WantBlock items=1',
        timestamp=datetime(2020, 1, 1, 0, 0, 0, 0),
        count=0,
        raw='',
        level=LogLevel.trace
    )

    assert line.fields == {
        'topics': '"codex blockexcnetwork"',
        'tid': '1',
        'peer': '16U*7mogoM',
        'type': 'WantBlock',
        'items': '1',
    }


def test_should_parse_topics_with_non_alphanumeric_character_values():
    source = ChroniclesRawSource(
        StringLogSource(
            lines='WRN 2024-02-02 20:38:47.316+00:00 a message topics="codex pendingblocks" address="cid: zDx*QP4zx9" '
                  'count=10641'
        )
    ).__iter__()

    line = next(source)

    assert line.message == "a message"
    assert line.count == 10641
    assert line.fields == {
        'topics': '"codex pendingblocks"',
        'address': '"cid: zDx*QP4zx9"',
    }


def test_should_parse_topics_with_escaped_quotes_in_values():
    source = ChroniclesRawSource(
        StringLogSource(
            lines='WRN 2024-02-02 20:38:47.316+00:00 a message topics="codex pendingblocks" '
                  'address="cid: \\"zDx*QP4zx9\\"" count=10641'
        )
    ).__iter__()

    line = next(source)

    assert line.message == "a message"
    assert line.count == 10641
    assert line.fields == {
        'topics': '"codex pendingblocks"',
        'address': '"cid: \\"zDx*QP4zx9\\""',
    }
