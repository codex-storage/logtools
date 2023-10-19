from logtools.log.log_line import LogLine, LogLevel


def test_should_parse_chronicles_fields():
    line = LogLine(message='Sending want list to peer',
                   topics='topics="codex blockexcnetwork" tid=1 peer=16U*7mogoM '
                          'type=WantBlock items=1',
                   timestamp='',
                   count=0,
                   raw='',
                   level=LogLevel.trace)

    assert line.fields == {
        'topics': '"codex blockexcnetwork"',
        'tid': '1',
        'peer': '16U*7mogoM',
        'type': 'WantBlock',
        'items': '1',
    }
