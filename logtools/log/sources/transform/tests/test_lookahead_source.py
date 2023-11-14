from logtools.log.sources.input.string_log_source import StringLogSource
from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource
from logtools.log.sources.transform.lookahead_source import LookAheadSource


def test_should_allow_peeking_at_the_head_of_log():
    log1 = LookAheadSource(ChroniclesRawSource(StringLogSource(
        name='log1',
        lines="""TRC 2023-10-16 20:29:24.595+00:00 Advertising block           topics="codex discoveryengine" count=1
          TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
          TRC 2023-10-16 20:29:24.597+00:00 Advertised block            topics="codex discoveryengine" count=3
          TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=4
          TRC 2023-10-16 20:29:24.646+00:00 Providing block             topics="codex discovery" count=5"""
    )))

    assert log1.peek.count == 1
    assert next(log1).count == 1
    assert log1.peek.count == 2


def test_should_return_all_elements():
    log1 = LookAheadSource(ChroniclesRawSource(StringLogSource(
        name='log1',
        lines="""TRC 2023-10-16 20:29:24.595+00:00 Advertising block    topics="codex discoveryengine" count=1
          TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
          TRC 2023-10-16 20:29:24.597+00:00 Advertised block            topics="codex discoveryengine" count=3
          TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=4
          TRC 2023-10-16 20:29:24.646+00:00 Providing block             topics="codex discovery" count=5"""
    )))

    assert [entry.count for entry in log1] == [1, 2, 3, 4, 5]


def test_should_raise_exception_when_nothing_to_peek():
    log1 = LookAheadSource(ChroniclesRawSource(StringLogSource(
        name='log1',
        lines="""TRC 2023-10-16 20:29:24.595+00:00 Advertising block    topics="codex discoveryengine" count=1
             TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
             TRC 2023-10-16 20:29:24.597+00:00 Advertised block            topics="codex discoveryengine" count=3
             TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=4
             TRC 2023-10-16 20:29:24.646+00:00 Providing block             topics="codex discovery" count=5"""
    )))

    for _ in log1:
        ...

    assert log1.peek is None
