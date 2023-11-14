from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource
from logtools.log.sources.transform.merged_source import MergedSource
from logtools.log.sources.transform.ordered_source import OrderedSource
from logtools.log.sources.input.string_log_source import StringLogSource


def test_should_merge_logs_by_timestamp():
    log1 = OrderedSource(ChroniclesRawSource(StringLogSource(
        name='log1',
        lines="""TRC 2023-10-16 20:29:24.594+00:00 Advertising block    topics="codex discoveryengine" count=1
          TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
          TRC 2023-10-16 20:29:24.597+00:00 Advertised block            topics="codex discoveryengine" count=3
          TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=4
          TRC 2023-10-16 20:29:24.647+00:00 Providing block             topics="codex discovery" count=5"""
    )))

    log2 = OrderedSource(ChroniclesRawSource(StringLogSource(
        name='log2',
        lines="""TRC 2023-10-16 20:29:24.595+00:00 Advertising block    topics="codex discoveryengine" count=6
          TRC 2023-10-16 20:29:24.596+00:00 Provided to nodes           topics="codex discovery" tid=1 count=7
          TRC 2023-10-16 20:29:24.596+00:00 Advertised block            topics="codex discoveryengine" count=8
          TRC 2023-10-16 20:29:24.645+00:00 Retrieved record from repo  topics="codex repostore" count=9
          TRC 2023-10-16 20:29:24.649+00:00 Providing block             topics="codex discovery" count=10"""
    )))

    merged = MergedSource(log1, log2)
    assert [line.count for line in merged] == [1, 6, 7, 8, 2, 3, 9, 4, 5, 10]
