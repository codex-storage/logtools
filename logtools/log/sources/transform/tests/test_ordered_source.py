import pytest

from logtools.log.sources.input.string_log_source import StringLogSource
from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource
from logtools.log.sources.transform.ordered_source import OrderedSource


def test_should_order_sources_by_lookahead_timestamp():
    lines = """TRC 2023-10-16 20:29:24.595+00:00 Advertising block        topics="codex discoveryengine" count=1
              TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
              TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=3"""

    log1 = OrderedSource(ChroniclesRawSource(StringLogSource(name='log1', lines=lines)))
    log2 = OrderedSource(ChroniclesRawSource(StringLogSource(name='log2', lines=lines)))

    next(log1)
    assert log2 < log1
    next(log2)
    assert (log2 <= log1) and (log2 <= log1)
    next(log2)
    assert log1 <= log2


def test_should_raise_error_if_comparing_empty_sources():
    lines = """TRC 2023-10-16 20:29:24.595+00:00 Advertising block        topics="codex discoveryengine" count=1
              TRC 2023-10-16 20:29:24.597+00:00 Provided to nodes           topics="codex discovery" tid=1 count=2
              TRC 2023-10-16 20:29:24.646+00:00 Retrieved record from repo  topics="codex repostore" count=3"""

    log1 = OrderedSource(ChroniclesRawSource(StringLogSource(name='log1', lines=lines)))
    log2 = OrderedSource(ChroniclesRawSource(StringLogSource(name='log2', lines=lines)))

    for _ in log1:
        ...

    with pytest.raises(ValueError):
        _ = log1 < log2
