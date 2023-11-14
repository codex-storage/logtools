from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource
from logtools.log.sources.transform.collating_source import CollatingSource
from logtools.log.sources.input.string_log_source import StringLogSource


def test_should_collate_lines_from_log_sources():
    log1 = ChroniclesRawSource(StringLogSource(
        name='log1',
        lines="""TRC 2023-10-16 20:29:24.595+00:00 Advertising block           topics="codex discoveryengine" count=1
        TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
        TRC 2023-10-16 20:29:24.597+00:00 Advertised block            topics="codex discoveryengine" count=3
        TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=4
        TRC 2023-10-16 20:29:24.646+00:00 Providing block             topics="codex discovery" count=5"""
    ))

    log2 = ChroniclesRawSource(StringLogSource(
        name='log2',
        lines="""TRC 2023-10-16 20:29:24.595+00:00 Advertising block           topics="codex discoveryengine" count=6
        TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=7
        TRC 2023-10-16 20:29:24.597+00:00 Advertised block            topics="codex discoveryengine" count=8
        TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=9
        TRC 2023-10-16 20:29:24.646+00:00 Providing block             topics="codex discovery" count=10"""
    ))

    collated = CollatingSource(log1, log2)
    entries = [(line.location.name, line.location.line_number, line.count) for line in collated]
    assert entries == [
        ('log1', 1, 1),
        ('log1', 2, 2),
        ('log1', 3, 3),
        ('log1', 4, 4),
        ('log1', 5, 5),
        ('log2', 1, 6),
        ('log2', 2, 7),
        ('log2', 3, 8),
        ('log2', 4, 9),
        ('log2', 5, 10),
    ]
