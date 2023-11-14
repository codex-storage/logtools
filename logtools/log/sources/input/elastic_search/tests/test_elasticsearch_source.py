from datetime import timedelta

import pytest
from dateutil import parser

from logtools.log.sources.input.elastic_search.elastic_search_source import ElasticSearchSource


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
