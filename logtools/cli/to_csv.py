"""Parses a log stream, possibly pre-filtered and/or merged, into a CSV file. Allows Chronicles topics to be
extracted into their own columns."""
import sys
from argparse import ArgumentParser
from csv import DictWriter
from pathlib import Path

from logtools import version_string
from logtools.cli.utils import kv_pair
from logtools.log.sources.input.file_log_source import FileLogSource
from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource


def to_csv(args):
    fields = args.extract_fields
    constant_columns = dict(args.constant_column) if args.constant_column else {}
    writer = DictWriter(
        sys.stdout,
        fieldnames=['timestamp', 'line_number',
                    'level', 'fields', 'count', 'message'] + fields + list(constant_columns.keys())
    )

    writer.writeheader()
    # FIXME '/dev/stdin' is a non-portable hack.
    for line in ChroniclesRawSource(FileLogSource(Path('/dev/stdin'))):
        line_fields = {field: line.fields.get(field, 'NA') for field in fields}
        writer.writerow({
            'timestamp': line.timestamp.isoformat(),
            'line_number': line.location.line_number,
            'level': line.level.value,
            'fields': line.topics,
            'count': line.count,
            'message': line.message,
            **line_fields,
            **constant_columns,
        })


def main():
    argparse = ArgumentParser()
    parser.add_argument('--version', action='version', version=version_string)
    argparse.add_argument('--extract-fields', nargs='+', default=[],
                          help='Extract chronicles topics into CSV columns')
    argparse.add_argument('--constant-column', metavar='KEY=VALUE', nargs='+', type=kv_pair,
                          help='Adds a column with key KEY and constant value VALUE to the CSV')

    to_csv(argparse.parse_args())


if __name__ == '__main__':
    main()
