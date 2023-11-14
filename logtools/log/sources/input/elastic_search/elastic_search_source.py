import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Iterator, Set

from elasticsearch import Elasticsearch

from logtools.log.base import TimestampedLogLine, LogSource

logger = logging.getLogger(__name__)

INDEX_PREFIX = 'continuous-tests-pods'


@dataclass
class ElasticSearchLocation:
    index: str
    result_number: int
    pod_name: str
    run_id: str


class ElasticSearchSource(LogSource[TimestampedLogLine[ElasticSearchLocation]]):
    def __init__(
            self,
            pods: Optional[Set[str]] = None,
            run_id: Optional[str] = None,
            client: Optional[Elasticsearch] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
    ):
        if client is None:
            logger.warning('No client provided, defaulting to localhost')
            client = Elasticsearch(hosts='http://localhost:9200')

        self.run_id = run_id
        self.pods = pods

        self.client = client
        self.start_date = start_date
        self.end_date = end_date

    def __iter__(self) -> Iterator[TimestampedLogLine[ElasticSearchLocation]]:
        for index in self._indices():
            for i, document in enumerate(self._run_scan(self._build_query(), index)):
                yield self._format_log_line(i, index, document)

    def _indices(self) -> Iterator[str]:
        # FIXME this is a VERY INEFFICIENT fallback
        if self.start_date is None:
            return [f'{INDEX_PREFIX}-*']

        start_day = self.start_date.date()
        end_day = self.end_date.date() if self.end_date else datetime.now().date()
        increment = timedelta(days=1)

        while start_day <= end_day:
            index = f'{INDEX_PREFIX}-{start_day:%Y.%m.%d}'
            if self.client.indices.exists(index=index):
                yield index
            start_day += increment

    def _build_query(self) -> Dict[str, Any]:
        query: Dict[str, Any] = {
            'sort': [{'@timestamp': 'asc'}]
        }

        if self.start_date is not None or self.end_date is not None:
            time_range = {}
            if self.start_date is not None:
                time_range['gte'] = self.start_date.isoformat()
            if self.end_date is not None:
                time_range['lte'] = self.end_date.isoformat()
            query['query'] = {'bool': {'filter': [{'range': {'@timestamp': time_range}}]}}

        if self.pods is not None:
            query['query']['bool']['filter'].append({"terms": {"pod_name.keyword": list(self.pods)}})

        if self.run_id is not None:
            query['query']['bool']['filter'].append({"term": {"pod_labels.runid.keyword": self.run_id}})

        if 'query' not in query:
            query['query'] = {'match_all': {}}

        return query

    def _run_scan(self, query: Dict[str, Any], index: str):
        # the search type stub does not contain the body argument for some reason so we disable typing here.
        initial = self.client.search(index=index, body=query, size=5_000, scroll='2m')  # type: ignore
        scroll_id = initial['_scroll_id']
        results = initial

        try:
            while True:
                documents = results['hits']['hits']
                if not documents:
                    break

                for doc in documents:
                    yield doc

                results = self.client.scroll(scroll_id=scroll_id, scroll='2m')
        finally:
            self.client.clear_scroll(scroll_id=scroll_id)

    def _format_log_line(self, result_number: int, index: str, document: Dict[str, Any]):
        contents = document['_source']

        return TimestampedLogLine(
            location=ElasticSearchLocation(index=index, result_number=result_number,
                                           run_id=contents['pod_labels']['runid'],
                                           pod_name=contents['pod_name']),
            timestamp=datetime.fromisoformat(contents['@timestamp']),
            raw=contents['message'],
        )
