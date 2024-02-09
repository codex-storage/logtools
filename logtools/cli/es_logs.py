import dataclasses
import os
from argparse import ArgumentParser
from datetime import timedelta, datetime
from enum import Enum
from json import JSONEncoder
from typing import List, Iterable, Any, Optional, Set

from colored import Style
from dateutil import parser as tsparser
from elasticsearch import Elasticsearch
from rich import json
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from logtools import version_string
from logtools.cli.palettes import ColorMap
from logtools.log.sources.input.elastic_search_source import ElasticSearchSource
from logtools.resource.elastic_search_log_repo import ElasticSearchLogRepo


class ResourceType(Enum):
    pods = 'pods'
    namespaces = 'namespaces'
    runs = 'runs'


RESOURCE_GETTERS = {
    ResourceType.pods: lambda repo, args: repo.pods(prefix=args.prefix, run_id=args.run_id),
    ResourceType.namespaces: lambda repo, args: repo.namespaces(prefix=args.prefix),
    ResourceType.runs: lambda repo, args: repo.test_runs(run_id=args.run_id, failed_only=args.failed_only),
}

RESOURCE_DESCRIBERS = {
    ResourceType.runs: lambda repo, args: repo.test_run(test_run_id=args.test_run_id),
}


def main():
    parser = ArgumentParser()
    parser.add_argument('--version', action='version', version=version_string)
    parser.add_argument(
        '--es-host',
        help='ElasticSearch URL (defaults to http://localhost:9200)',
        default=os.environ.get('ES_HOST', 'http://localhost:9200')
    )

    subparsers = parser.add_subparsers(title='Command', required=True)
    _add_get_cli(subparsers)
    _add_describe_cli(subparsers)
    _add_logs_cli(subparsers)

    args = parser.parse_args()
    client = Elasticsearch(args.es_host, request_timeout=60)
    args.main(args, client)


def get_object(args, client: Elasticsearch):
    repo = ElasticSearchLogRepo(client=client)
    Console().print(format_table(RESOURCE_GETTERS[ResourceType[args.resource_type]](repo, args)))


def describe_object(args, client: Elasticsearch):
    repo = ElasticSearchLogRepo(client=client)
    Console().print(format_json([RESOURCE_DESCRIBERS[ResourceType[args.resource_type]](repo, args)]))


# FIXME this is starting to get too complex to be here.
def get_logs(args, client: Elasticsearch):
    resource = ResourceType[args.resource_type]
    if resource == ResourceType.pods:
        get_pod_logs(
            pods=args.pods,
            client=client,
            colored_output=not args.no_color,
            start_date=args.from_,
            end_date=args.to,
        )
    elif resource == ResourceType.runs:
        run = ElasticSearchLogRepo(client=client).test_run(test_run_id=args.test_run_id).test_run
        get_pod_logs(set(run.pods), client, limit=args.limit, start_date=run.start, end_date=run.end)


def get_pod_logs(pods: Set[str],
                 client: Elasticsearch,
                 colored_output: bool = True,
                 limit: Optional[int] = None,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None):
    colors = ColorMap()
    for i, line in enumerate(ElasticSearchSource(
            pods=pods,
            client=client,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
    )):
        output = f'[{line.location.pod_name}]: {line.raw}'
        if colored_output:
            output = f'{colors[line.location.pod_name]}{output}{Style.reset}'
        print(output)


def format_table(objects: List, title: str = 'Results') -> Table:
    tbl = Table(title=title)
    field_names = None

    for obj in objects:
        if field_names is None:
            field_names = obj.__annotations__.keys()
            for field_name in field_names:
                tbl.add_column(field_name, justify='left')

        tbl.add_row(*[_format_field(getattr(obj, field)) for field in field_names])

    return tbl


def format_json(obj: Any) -> JSON:
    # For now, this is rather rudimentary.
    class DataclassEncoder(JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            elif isinstance(o, datetime):
                return o.isoformat()
            elif isinstance(o, Enum):
                return o.value
            return super().default(o)

    return JSON(json.dumps(obj, cls=DataclassEncoder))


def _format_field(field: Any):
    if isinstance(field, str):
        return field
    elif isinstance(field, Iterable):
        return ', '.join([_format_field(item) for item in field])
    return str(field)


def _add_get_cli(subparsers):
    get = subparsers.add_parser('get', help='display existing resources')
    get.add_argument('--from', type=tsparser.parse,
                     help='show resources present in log messages starting at the given date '
                          '(mm-dd-yyyy, or mm-dd-yyyy hh:mm:ss.mmmmmm). defaults to 7 days ago.',
                     default=(datetime.today() - timedelta(days=7)).date())
    get.set_defaults(main=get_object)

    get_subparsers = get.add_subparsers(title='resource type', dest='resource_type', required=True)
    get_pods = get_subparsers.add_parser('pods', help='display existing pods')
    get_pods.add_argument('--prefix', help='filter pods by prefix')
    get_pods.add_argument('run_id', help='show pods for a given run')

    get_namespaces = get_subparsers.add_parser('namespaces', help='display existing namespaces')
    get_namespaces.add_argument('--prefix', help='filter namespaces by prefix')

    get_namespaces = get_subparsers.add_parser('runs', help='display current test runs')
    get_namespaces.add_argument('run_id', help='show test runs for the given run id')
    get_namespaces.add_argument('--failed-only', action='store_true', help='show only failed test runs')
    get_namespaces.add_argument('--from', type=tsparser.parse,
                                help='show test runs starting at the given date '
                                     '(mm-dd-yyyy, or mm-dd-yyyy hh:mm:ss.mmmmmm). defaults to 7 days ago.',
                                default=(datetime.today() - timedelta(days=7)).date())


def _add_describe_cli(subparsers):
    describe = subparsers.add_parser('describe', help='describe a resource')
    describe.set_defaults(main=describe_object)

    describe_subparsers = describe.add_subparsers(title='resource type', dest='resource_type', required=True)
    describe_runs = describe_subparsers.add_parser('runs', help='describe a test run')
    describe_runs.add_argument('test_run_id', help='show test run details')
    describe_runs.set_defaults(main=describe_object)


def _add_logs_cli(subparsers):
    logs = subparsers.add_parser('logs', help='fetch pod logs')
    logs.set_defaults(main=get_logs)
    logs.add_argument('--limit', type=int, help='limit the number of log entries to fetch')

    log_subparsers = logs.add_subparsers(title='resource type', dest='resource_type', required=True)

    logs.add_argument('--no-color', dest='no_color', action='store_true', help='disable colored output')

    pod_logs = log_subparsers.add_parser('pods', help='fetch logs for a pod')
    pod_logs.add_argument('pods', nargs='+', help='pod names to fetch logs from')
    pod_logs.add_argument('--from', dest='from_', type=tsparser.parse,
                          help='show entries from date/time (MM-DD-YYYY, or MM-DD-YYYY HH:MM:SS.mmmmmm), '
                               'treated as UTC if no timezone given', default=None)
    pod_logs.add_argument('--to', dest='to', type=tsparser.parse,
                          help='show entries until date/time (MM-DD-YYYY, or MM-DD-YYYY HH:MM:SS.mmmmmm), '
                               'treated as UTC if no timezone given', default=None)

    run_logs = log_subparsers.add_parser('runs', help='fetch logs for a test run')
    run_logs.add_argument('test_run_id', help='run ID to fetch logs from')


if __name__ == '__main__':
    main()
