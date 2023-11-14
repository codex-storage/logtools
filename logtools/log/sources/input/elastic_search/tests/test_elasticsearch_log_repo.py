import pytest

from logtools.log.sources.input.elastic_search.elastic_search_log_repo import ElasticSearchLogRepo, Namespace, Pod


# XXX these are not good quality tests as they are overly complex and either tightly coupled to specific data or very
#   weak in terms of what they assert. Ideally we should build simpler fixtures and test smaller bits at a time, but
#   that requires a lot of setup, so we go with this.

@pytest.mark.vcr
def test_should_retrieve_existing_namespaces():
    repo = ElasticSearchLogRepo()
    namespaces = repo.namespaces('codex-continuous-tests-profiling')

    assert set(namespaces) == {
        Namespace(
            name='codex-continuous-tests-profiling-two-client-tests-0',
            run_id=frozenset({
                '20231109-085853',
                '20231107-074743',
                '20231109-043100',
                '20231107-065930',
                '20231107-064223',
                '20231109-055106'
            }),
            indices=frozenset({
                'continuous-tests-pods-2023.11.07',
                'continuous-tests-pods-2023.11.09',
                'continuous-tests-pods-2023.11.10',
            }),
        ),
        Namespace(
            name='codex-continuous-tests-profiling-two-client-tests-sched-0',
            run_id=frozenset({'20231109-101554'}),
            indices=frozenset({
                'continuous-tests-pods-2023.11.09',
                'continuous-tests-pods-2023.11.10'
            }),
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
        indices=frozenset({
            'continuous-tests-pods-2023.11.09',
            'continuous-tests-pods-2023.11.10'
        })
    ) in pods


