from datetime import datetime

import pytz

from logtools.log.log_line import LogLine, LogLevel


def test_should_parse_logline_from_string():
    line = LogLine.from_str('TRC 2023-10-16 17:28:46.579+00:00 Sending want list to peer                  '
                            'topics="codex blockexcnetwork" tid=1 peer=16U*7mogoM '
                            'type=WantBlock items=1 count=870781', parse_datetime=True)

    assert line.level == LogLevel.trace
    assert line.timestamp == datetime(2023, 10, 16, 17, 28, 46,
                                      579000, tzinfo=pytz.utc)
    assert line.count == 870781
