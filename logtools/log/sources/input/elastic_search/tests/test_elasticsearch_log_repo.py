import pytest
from dateutil import parser

from logtools.log.sources.input.elastic_search.elastic_search_log_repo import ElasticSearchLogRepo, Namespace, Pod


# XXX these are not good quality tests as they are overly complex and either tightly coupled to specific data or very
#   weak in terms of what they assert. They will be a pain to maintain. Ideally we should build simpler fixtures and
#   test smaller bits at a time, but that requires a lot of setup, so for now we go with this.

@pytest.mark.vcr
def test_should_retrieve_existing_namespaces():
    repo = ElasticSearchLogRepo()
    namespaces = repo.namespaces('codex-continuous-tests-profiling')

    assert set(namespaces) == {
        Namespace(
            name='codex-continuous-tests-profiling-two-client-tests-0',
            run_id=(
                '20231107-064223',
                '20231107-065930',
                '20231107-074743',
                '20231109-043100',
                '20231109-055106',
                '20231109-085853',
                '20231114-045924',
                '20231114-051016',
                '20231114-051742',
            ),
            indices=(
                'continuous-tests-pods-2023.11.07',
                'continuous-tests-pods-2023.11.09',
                'continuous-tests-pods-2023.11.10',
                'continuous-tests-pods-2023.11.14',
            ),
        ),
        Namespace(
            name='codex-continuous-tests-profiling-two-client-tests-sched-0',
            run_id=('20231109-101554',),
            indices=(
                'continuous-tests-pods-2023.11.09',
                'continuous-tests-pods-2023.11.10',
            ),
        )
    }


@pytest.mark.vcr
def test_should_retrieve_existing_pods_for_namespace():
    repo = ElasticSearchLogRepo()
    pods = set(repo.pods(run_id='20231109-101554'))

    assert {pod.name for pod in pods} == {'bootstrap-2-58b69484bc-88msf',
                                          'codex1-3-b558568cf-tvcsc',
                                          'geth-0-7d8bc9dd5b-8wx95',
                                          'ctnr4-d8f8d6d8-rtqrp',
                                          'codex-contracts-1-b98d98877-bqd5x'}

    assert Pod(
        name='bootstrap-2-58b69484bc-88msf',
        namespace='codex-continuous-tests-profiling-two-client-tests-sched-0',
        run_id='20231109-101554',
        indices=(
            'continuous-tests-pods-2023.11.09',
            'continuous-tests-pods-2023.11.10',
        )
    ) in pods


@pytest.mark.vcr
def test_should_respect_time_horizon_for_retrieving_resources():
    repo = ElasticSearchLogRepo(since=parser.parse('2023-11-14T18:00:00.000Z'))
    namespaces = repo.namespaces('codex-continuous-tests-profiling')

    assert len(list(namespaces)) == 0

    repo = ElasticSearchLogRepo(since=parser.parse('2023-11-07T18:00:00.000Z'))
    namespaces = repo.namespaces('codex-continuous-tests-profiling')

    assert len(list(namespaces)) == 2


@pytest.mark.vcr
def test_should_retrieve_test_runs_over_a_single_run_id():
    repo = ElasticSearchLogRepo()
    runs = list(repo.test_runs('20240206-093136'))

    assert len(runs) == 14


@pytest.mark.vcr
def test_should_retrieve_failing_test_runs_over_a_single_run_id():
    repo = ElasticSearchLogRepo()
    runs = list(repo.test_runs('20240206-093136', failed_only=True))

    assert len(runs) == 1
    assert runs[0].error.strip() == (
        "data/zDvZRwzm5UemKDPMvadCu999HrqUnCJGzvKnsF7eiy2XV3TzoW7V/network' timed out after "
        "3 tries over 10 mins, 1 secs."
    )
