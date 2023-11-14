import os
from argparse import ArgumentParser
from enum import Enum
from typing import List, Iterable

from colored import Style
from dateutil import parser as tsparser
from elasticsearch import Elasticsearch
from prettytable import PrettyTable

from logtools.cli.palettes import ColorMap
from logtools.log.sources.input.elastic_search.elastic_search_log_repo import ElasticSearchLogRepo
from logtools.log.sources.input.elastic_search.elastic_search_source import ElasticSearchSource


class ResourceType(Enum):
    pods = 'pods'
    namespaces = 'namespaces'


GETTERS = {
    ResourceType.pods: lambda repo, args: repo.pods(prefix=args.prefix, run_id=args.run_id),
    ResourceType.namespaces: lambda repo, args: repo.namespaces(prefix=args.prefix)
}


def format_table(objects: List) -> str:
    tbl = PrettyTable()

    for obj in objects:
        if not tbl.field_names:
            tbl.field_names = obj.__annotations__.keys()
        tbl.add_row([_format_field(getattr(obj, field)) for field in tbl.field_names])

    return tbl.get_string()


def _format_field(field: str | Iterable[object]):
    if isinstance(field, str):
        return field
    return ', '.join([str(item) for item in field])


def get_object(args, client: Elasticsearch):
    repo = ElasticSearchLogRepo(client=client)
    print(format_table(GETTERS[ResourceType[args.resource_type]](repo, args)))


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

    get = subparsers.add_parser('get', help='Display existing resources')
    get.set_defaults(main=get_object)

    get_subparsers = get.add_subparsers(title='Resource type', dest='resource_type', required=True)
    get_pods = get_subparsers.add_parser('pods', help='Display existing pods')
    get_pods.add_argument('--prefix', help='Filter pods by prefix')
    get_pods.add_argument('--run-id', help='Show pods for a given run', required=True)

    get_namespaces = get_subparsers.add_parser('namespaces', help='Display existing namespaces')
    get_namespaces.add_argument('--prefix', help='Filter namespaces by prefix')

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

    args = parser.parse_args()

    client = Elasticsearch(args.es_host, request_timeout=60)

    args.main(args, client)


if __name__ == '__main__':
    main()
