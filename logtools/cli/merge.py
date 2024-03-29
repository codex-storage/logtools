"""Merges two log files by timestamp. Accepts aliases for log files. Can filter by timestamp."""
import argparse
import random
from datetime import datetime
from pathlib import Path
from random import shuffle
from typing import Dict

import pytz
from colored import Fore, Style
from dateutil import parser as tsparser

from logtools import version_string
from logtools.log.sources.input.file_log_source import FileLogSource
from logtools.log.sources.parse.chronicles_raw_source import ChroniclesRawSource
from logtools.log.sources.transform.filtered_source import FilteredSource, timestamp_range
from logtools.log.sources.transform.merged_source import MergedSource
from logtools.log.sources.transform.ordered_source import OrderedSource


def merge(args):
    names = _assign_aliases(args)
    palette = _assign_colors(names)

    parts = [
        OrderedSource(
            FilteredSource(
                ChroniclesRawSource(
                    FileLogSource(path)
                ),
                predicate=_filtering_predicate(args)
            )
        )
        for path in args.files
    ]

    # If we only have one source, then no need to actually do a merge.
    logs = MergedSource(*parts) if len(parts) > 1 else parts[0]

    for line in logs:
        log_id = names[line.location.path.name]
        print(f'{getattr(Fore, palette[log_id])}{log_id}: {line.raw}{Style.reset}', end='')


def _assign_aliases(args):
    names = {path.name: path.name for path in args.files}
    for i, alias in enumerate(args.aliases):
        if i >= len(args.files):  # excess aliases are just ignored
            break
        names[args.files[i].name] = alias

    max_len = max([len(alias) for alias in names.values()])

    return {name: alias.rjust(max_len) for name, alias in names.items()}


def _assign_colors(names: Dict[str, str]) -> Dict[str, str]:
    random.seed(4)
    colors = list(Fore._COLORS.keys())
    shuffle(colors)
    return {names[key]: colors[i] for i, key in enumerate(names.keys())}


def _filtering_predicate(args):
    if args.from_ or args.to:
        return timestamp_range(
            _ensure_utc(args.from_) if args.from_ is not None else datetime(
                year=1980, month=1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.UTC),
            _ensure_utc(args.to) if args.to is not None else datetime.utcnow().replace(tzinfo=pytz.UTC)
        )

    return lambda x: True


def _ensure_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=pytz.UTC)
    return ts.replace(tzinfo=pytz.UTC)


def main():
    parser = argparse.ArgumentParser(
        description='Merges Chronicles logs chronologically and outputs colored, interleaved content.')
    parser.add_argument('--version', action='version', version=version_string)

    parser.add_argument("files", nargs="+", help='Log files to merge.', type=Path)
    parser.add_argument('--aliases', nargs="*",
                        help='Optional aliases to print instead of the log file name in merged output',
                        type=str, default=[])
    parser.add_argument('--from', dest='from_', type=tsparser.parse,
                        help='Show entries from date/time (multiple formats accepted)')
    parser.add_argument('--to', type=tsparser.parse,
                        help='Show entries to date/time (multiple formats accepted)')

    merge(parser.parse_args())


if __name__ == '__main__':
    main()
