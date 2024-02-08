import dataclasses
import os
from argparse import ArgumentParser
from datetime import timedelta, datetime
from enum import Enum
from json import JSONEncoder
from typing import List, Iterable, Any

import rich
from colored import Style
from dateutil import parser as tsparser
from elasticsearch import Elasticsearch
from rich import json
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from logtools.cli.palettes import ColorMap
from logtools.log.sources.input.elastic_search_source import ElasticSearchSource
from logtools.resource.elastic_search_log_repo import ElasticSearchLogRepo


class ResourceType(Enum):
    pods = 'pods'
    namespaces = 'namespaces'
    runs = 'runs'


GETTERS = {
    ResourceType.pods: lambda repo, args: repo.pods(prefix=args.prefix, run_id=args.run_id),
    ResourceType.namespaces: lambda repo, args: repo.namespaces(prefix=args.prefix),
    ResourceType.runs: lambda repo, args: repo.test_runs(run_id=args.run_id, failed_only=args.failed_only),
}

DESCRIBERS = {
    ResourceType.runs: lambda repo, args: repo.describe_test_run(test_run_id=args.test_run_id),
}


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


def get_object(args, client: Elasticsearch):
    repo = ElasticSearchLogRepo(client=client)
    Console().print(format_table(GETTERS[ResourceType[args.resource_type]](repo, args)))


def describe_object(args, client: Elasticsearch):
    repo = ElasticSearchLogRepo(client=client)
    Console().print(format_json([DESCRIBERS[ResourceType[args.resource_type]](repo, args)]))


def get_logs(args, client: Elasticsearch):
    colors = ColorMap()
    for line in ElasticSearchSource(
            pods=args.pods,
            client=client,
            start_date=args.from_,
            end_date=args.to,
    ):
        output = f'[{line.location.pod_name}]: {line.raw}'
        if not args.no_color:
            output = f'{colors[line.location.pod_name]}{output}{Style.reset}'
        print(output)


def main():
    parser = ArgumentParser()
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


def _add_get_cli(subparsers):
    get = subparsers.add_parser('get', help='Display existing resources')
    get.add_argument('--from', type=tsparser.parse,
                     help='Show resources present in log messages starting at the given date '
                          '(MM-DD-YYYY, or MM-DD-YYYY HH:MM:SS.mmmmmm). Defaults to 7 days ago.',
                     default=(datetime.today() - timedelta(days=7)).date())
    get.set_defaults(main=get_object)

    get_subparsers = get.add_subparsers(title='Resource type', dest='resource_type', required=True)
    get_pods = get_subparsers.add_parser('pods', help='Display existing pods')
    get_pods.add_argument('--prefix', help='Filter pods by prefix')
    get_pods.add_argument('--run-id', help='Show pods for a given run', required=True)

    get_namespaces = get_subparsers.add_parser('namespaces', help='Display existing namespaces')
    get_namespaces.add_argument('--prefix', help='Filter namespaces by prefix')

    get_namespaces = get_subparsers.add_parser('runs', help='Display current test runs')
    get_namespaces.add_argument('--run-id', help='Show test runs for the given run id', required=True)
    get_namespaces.add_argument('--failed-only', action='store_true', help='Show only failed test runs')
    get_namespaces.add_argument('--from', type=tsparser.parse,
                                help='Show test runs starting at the given date '
                                     '(MM-DD-YYYY, or MM-DD-YYYY HH:MM:SS.mmmmmm). Defaults to 7 days ago.',
                                default=(datetime.today() - timedelta(days=7)).date())


def _add_describe_cli(subparsers):
    describe = subparsers.add_parser('describe', help='Describe a resource')
    describe.set_defaults(main=describe_object)

    describe_subparsers = describe.add_subparsers(title='Resource type', dest='resource_type', required=True)
    describe_runs = describe_subparsers.add_parser('runs', help='Describe a test run')
    describe_runs.add_argument('test_run_id', help='Show test run details')
    describe_runs.set_defaults(main=describe_object)


def _add_logs_cli(subparsers):
    logs = subparsers.add_parser('logs', help='Fetch pod logs')
    logs.set_defaults(main=get_logs)

    logs.add_argument('--pods', nargs='+', help='Pods to fetch logs for', required=True)
    logs.add_argument('--from', dest='from_', type=tsparser.parse,
                      help='Show entries from date/time (MM-DD-YYYY, or MM-DD-YYYY HH:MM:SS.mmmmmm), '
                           'treated as UTC if no timezone given', default=None)
    logs.add_argument('--to', dest='to', type=tsparser.parse,
                      help='Show entries until date/time (MM-DD-YYYY, or MM-DD-YYYY HH:MM:SS.mmmmmm), '
                           'treated as UTC if no timezone given', default=None)
    logs.add_argument('--no-color', dest='no_color', action='store_true', help='Disable colored output')


if __name__ == '__main__':
    main()
