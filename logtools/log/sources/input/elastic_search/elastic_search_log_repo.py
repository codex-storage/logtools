import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Iterator, Dict, Any

from dateutil import parser
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Namespace:
    name: str
    run_id: tuple[str, ...]
    indices: tuple[str, ...]


@dataclass(frozen=True)
class Pod:
    name: str
    namespace: str
    run_id: str
    indices: tuple[str, ...]


class TestStatus(Enum):
    passed = 'passed'
    failed = 'failed'


@dataclass(frozen=True)
class TestRun:
    id: str
    run_id: str
    test_name: str
    pods: str
    start: datetime
    end: datetime
    duration: float
    status: TestStatus
    error: Optional[str]
    stacktrace: Optional[str]


MAX_AGGREGATION_BUCKETS = 1000

POD_LOGS_INDEX_SET = 'continuous-tests-pods-*'
TEST_STATUS_INDEX_SET = 'continuous-tests-status-*'


class ElasticSearchLogRepo:
    def __init__(
            self,
            client: Optional[Elasticsearch] = None,
            since: Optional[datetime] = None,
    ):
        if client is None:
            logger.warning('No client provided, defaulting to localhost')
            client = Elasticsearch(hosts='http://localhost:9200', request_timeout=60)

        self.client = client
        self.since = since

    def namespaces(self, prefix: Optional[str] = None) -> Iterator[Namespace]:
        query = self._time_limited({
            'size': 0,
            'aggs': {
                'distinct_namespaces': {
                    'terms': {'field': 'pod_namespace.keyword', 'size': MAX_AGGREGATION_BUCKETS},
                    'aggs': {
                        'indices': {'terms': {'field': '_index'}},
                        'runid': {'terms': {'field': 'pod_labels.runid.keyword'}},
                    }
                }
            }
        })

        if prefix is not None:
            query['aggs']['distinct_namespaces']['terms']['include'] = f'{prefix}.*'  # type: ignore

        result = self.client.search(index=POD_LOGS_INDEX_SET, body=query)  # type: ignore

        for namespace in result['aggregations']['distinct_namespaces']['buckets']:
            yield Namespace(
                name=namespace['key'],
                run_id=tuple(sorted(run_id['key'] for run_id in namespace['runid']['buckets'])),
                indices=tuple(sorted(index['key'] for index in namespace['indices']['buckets']))
            )

    def pods(self, prefix: Optional[str] = None, run_id: Optional[str] = None):
        query = self._time_limited({
            'size': 0,
            'aggs': {
                'distinct_pods': {
                    'terms': {'field': 'pod_name.keyword', 'size': MAX_AGGREGATION_BUCKETS},
                    'aggs': {
                        'indices': {'terms': {'field': '_index'}},
                        'namespace': {'terms': {'field': 'pod_namespace.keyword'}},
                        'runid': {'terms': {'field': 'pod_labels.runid.keyword', 'size': MAX_AGGREGATION_BUCKETS}},
                    }
                }
            }
        })

        if prefix is not None:
            query['aggs']['distinct_pods']['terms']['include'] = f'{prefix}.*'  # type: ignore

        if run_id is not None:
            query['query'] = {
                'bool': {
                    'filter': [{'term': {'pod_labels.runid.keyword': run_id}}]
                }
            }

        for pod in self.client.search(index=POD_LOGS_INDEX_SET,
                                      body=query)['aggregations']['distinct_pods']['buckets']:  # type: ignore
            assert len(pod['namespace']['buckets']) == 1, 'Pods should only have one namespace'
            assert len(pod['runid']['buckets']) == 1, 'Pods should only have one run_id'

            yield Pod(
                name=pod['key'],
                namespace=pod['namespace']['buckets'][0]['key'],
                run_id=pod['runid']['buckets'][0]['key'],
                indices=tuple(sorted(index['key'] for index in pod['indices']['buckets']))
            )

    def test_runs(self, run_id: str, failed_only=False) -> Iterator[TestRun]:
        query = self._time_limited({
            'query': {
                'bool': {
                    'filter': [{'term': {'runid.keyword': run_id}}]
                }
            },
            'sort': [{'@timestamp': 'desc'}],
            'size': 10000,
        })

        if failed_only:
            query['query']['bool']['filter'].append({'term': {'status.keyword': 'Failed'}})

        for document in self.client.search(index=TEST_STATUS_INDEX_SET, body=query)['hits']['hits']:  # type: ignore
            content = document['_source']
            start = parser.parse(content['teststart'])
            duration = float(content['testduration'])
            yield TestRun(
                id=document['_id'],
                run_id=content['runid'],
                test_name=content['testname'],
                start=start,
                end=start + timedelta(seconds=duration),
                duration=duration,
                status=TestStatus(content['status'].lower()),
                pods=content['involvedpods'],
                error=content.get('error'),
                stacktrace=content.get('message')
            )

    def _time_limited(self, query: Dict[str, Any]) -> Dict[str, Any]:
        if self.since is not None:
            query['query'] = {
                'bool': {
                    'filter': [{'range': {'@timestamp': {'gte': self.since.isoformat()}}}]
                }
            }

        return query
