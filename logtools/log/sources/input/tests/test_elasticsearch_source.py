from datetime import timedelta

import pytest
from dateutil import parser

from logtools.log.sources.input.elastic_search_source import ElasticSearchSource


@pytest.mark.vcr
def test_should_fetch_logs_by_date():
    start_date = parser.parse('2023-11-10T05:14:46.9842511Z')
    end_date = parser.parse('2023-11-10T05:15:47.0842511Z')

    log = ElasticSearchSource(
        start_date=start_date,
        end_date=end_date,
        run_id='20231109-101554',
        pods={'codex1-3-b558568cf-tvcsc', 'bootstrap-2-58b69484bc-88msf'}
    )

    lines = list(log)

    assert len(lines) > 0
    # ES resolution is 1ms, so we may get some results that are off up to 1ms
    assert all((start_date - timedelta(milliseconds=1)) <=
               line.timestamp <= (end_date + timedelta(milliseconds=1)) for line in lines)

    assert {line.location.pod_name for line in lines} == {'codex1-3-b558568cf-tvcsc', 'bootstrap-2-58b69484bc-88msf'}
    assert {line.location.run_id for line in lines} == {'20231109-101554'}


@pytest.mark.vcr
def test_should_fetch_logs_when_no_dates_are_specified():
    log = ElasticSearchSource(
        run_id='20231109-101554',
        pods={'codex1-3-b558568cf-tvcsc'}
    )

    try:
        next(log.__iter__())
    except StopIteration:
        assert False, "Should have returned at least one log line"


@pytest.mark.vcr
def test_should_respect_fetching_limits_when_limit_smaller_than_batch_size():
    log = ElasticSearchSource(
        run_id='20240208-115030',
        pods={'codex1-3-6c565dbd66-wxg49'},
        limit=10
    )

    lines = list(log)
    assert len(lines) == 10
    assert log.page_fetch_counter == 1


@pytest.mark.vcr
def test_should_respect_fetching_limits_when_limit_larger_than_batch_size():
    log = ElasticSearchSource(
        run_id='20240208-115030',
        pods={'codex1-3-6c565dbd66-wxg49'},
        es_batch_size=7,
        limit=10
    )

    lines = list(log)
    assert len(lines) == 10
    assert log.page_fetch_counter == 2
