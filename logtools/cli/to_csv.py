"""Parses a log stream, possibly pre-filtered and/or merged, into a CSV file. Allows chronicles topics to be
extracted into their own columns."""
import sys
from argparse import ArgumentParser
from csv import DictWriter

from logtools.log.sources.stream_log_source import StreamLogSource


def to_csv(args):
    fields = args.extract_fields
    writer = DictWriter(sys.stdout,
                        fieldnames=['timestamp', 'line_number', 'level', 'fields', 'count', 'message'] + fields)
    writer.writeheader()
    for line in StreamLogSource(sys.stdin):
        line_fields = {field: line.fields.get(field, 'NA') for field in fields}
        writer.writerow({
            'timestamp': line.timestamp.isoformat(),
            'line_number': line.location.line_number,
            'level': line.level.value,
            'fields': line.topics,
            'count': line.count,
            'message': line.message,
            **line_fields,
        })


def main():
    argparse = ArgumentParser()
    argparse.add_argument('--extract-fields', nargs='+', default=[],
                          help='Extract chronicles topics into CSV columns')

    to_csv(argparse.parse_args())


if __name__ == '__main__':
    main()
