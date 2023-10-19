from dateutil import parser

from logtools.log.log_line import LogLine
from logtools.log.sources.filtered_source import FilteredSource, timestamp_range
from logtools.log.sources.log_parsers import parse_raw
from logtools.log.sources.tests.string_log_source import StringLogSource


def test_should_filter_by_matching_predicate():
    log1 = StringLogSource(
        name='log1',
        lines="""TRC 2023-10-16 20:29:24.595+00:00 Advertising block           topics="codex discoveryengine" count=1
        TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
        TRC 2023-10-16 20:29:24.597+00:00 Advertised block            topics="codex discoveryengine" count=3
        TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=4
        TRC 2023-10-16 20:29:24.646+00:00 Providing block             topics="codex discovery" count=5"""
    )

    def predicate(line):
        return line.count % 2 == 0

    assert [line.count for line in FilteredSource(log1, predicate)] == [2, 4]


def test_should_generate_correct_datetime_range_predicate():
    raw_lines = [
        'TRC 2023-10-16 20:29:24.595+00:00 one                  topics="codex discoveryengine" count=1',
        'TRC 2023-10-17 20:29:24.597+00:00 two                  topics="codex discoveryengine" count=2',
        'TRC 2023-10-18 20:29:24.597+00:00 three                topics="codex discoveryengine" count=3',
        'TRC 2023-10-18 21:29:24.597+00:00 four little indians  topics="codex discoveryengine" count=4',
    ]

    matches = timestamp_range(start=parser.parse('2023-10-16 22:29:24.597+00:00'),
                              end=parser.parse('2023-10-18 20:29:25.597+00:00'))

    lines = [parse_raw(line, parse_datetime=True) for line in raw_lines]
    filtered = [line.count for line in lines if matches(line)]

    assert filtered == [2, 3]
