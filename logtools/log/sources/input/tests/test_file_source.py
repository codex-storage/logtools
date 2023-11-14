from pathlib import Path

from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource
from logtools.log.sources.input.file_log_source import FileLogSource

SAMPLE_LOG = Path(__file__).parent / 'sample.log'


def test_should_read_lines_from_file():
    log = ChroniclesRawSource(FileLogSource(SAMPLE_LOG))
    assert [line.count for line in log] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def test_should_provide_location_context_for_lines():
    log = iter(ChroniclesRawSource(FileLogSource(SAMPLE_LOG)))
    line1 = next(log)
    line2 = next(log)

    assert line1.location.path == SAMPLE_LOG
    assert line2.location.path == SAMPLE_LOG

    assert line1.location.line_number == 1
    assert line2.location.line_number == 2
