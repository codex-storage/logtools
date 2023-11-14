from dateutil import parser

from logtools.log.sources.input.string_log_source import StringLogSource
from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource
from logtools.log.sources.transform.filtered_source import FilteredSource, timestamp_range


def test_should_filter_by_matching_predicate():
    log1 = ChroniclesRawSource(StringLogSource(
        name='log1',
        lines="""TRC 2023-10-16 20:29:24.595+00:00 Advertising block           topics="codex discoveryengine" count=1
        TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
        TRC 2023-10-16 20:29:24.597+00:00 Advertised block            topics="codex discoveryengine" count=3
        TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=4
        TRC 2023-10-16 20:29:24.646+00:00 Providing block             topics="codex discovery" count=5"""
    ))

    def predicate(line):
        return line.count % 2 == 0

    assert [line.count for line in FilteredSource(log1, predicate)] == [2, 4]


def test_should_generate_correct_datetime_range_predicate():
    log1 = ChroniclesRawSource(StringLogSource(
        """TRC 2023-10-16 20:29:24.595+00:00 one                  topics="codex discoveryengine" count=1
        TRC 2023-10-17 20:29:24.597+00:00 two                  topics="codex discoveryengine" count=2
        TRC 2023-10-18 20:29:24.597+00:00 three                topics="codex discoveryengine" count=3
        TRC 2023-10-18 21:29:24.597+00:00 four little indians  topics="codex discoveryengine" count=4"""
    ))

    line_numbers = [
        line.location.line_number for line in FilteredSource(
            log1, timestamp_range(start=parser.parse('2023-10-17 20:29:24.597+00:00'),
                                  end=parser.parse('2023-10-18 20:29:24.597+00:00'))
        )
    ]

    assert line_numbers == [2, 3]
