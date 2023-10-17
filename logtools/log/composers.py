# import abc
# import re
# from abc import abstractmethod
# from datetime import datetime
# from heapq import heapify, heappop, heappush
# from pathlib import Path
# from typing import TypedDict, Iterable, Union, Generator, Optional, Iterator, List
#
# from parse.utils import group_match
#
# class LogIterator(abc.ABC, Iterator[LogLine]):
#     @abstractmethod
#     def peek(self) -> Optional[LogLine]:
#         ...
#
#     def context(self) -> str:
#         ...
#
#
# class SingleLogIterator(LogIterator):
#
#     def __init__(
#             self,
#             path: Path,
#             alias: str,
#             from_ts: Optional[datetime] = None,
#             to_ts: Optional[datetime] = None,
#             parse_datetime=False
#     ):
#         self.path = path
#         self.line_number = 0
#         self.parse_datetime = parse_datetime
#         self.alias = alias
#
#         # If from_ts or to_ts is specified, then timestamp parsing is mandatory.
#         self.parse_datetime = self.parse_datetime or (from_ts is not None or to_ts is not None)
#         self.from_ts = from_ts
#         self.to_ts = to_ts
#
#         self.inner_iterator = self._iterator()
#         self.look_ahead = next(self.inner_iterator, None)
#
#     def __next__(self) -> LogLine:
#         next_element = self.look_ahead if self.look_ahead is not None else next(self.inner_iterator)
#         self.look_ahead = next(self.inner_iterator, None)
#         return next_element
#
#     def __iter__(self):
#         return self
#
#     def __lt__(self, other):
#         return self.latest_timestamp() < other.latest_timestamp()
#
#     def __le__(self, other):
#         return self.latest_timestamp() <= other.latest_timestamp()
#
#     def _iterator(self) -> Generator[LogLine, None, None]:
#         with self.path.open() as f:
#             for line in f:
#                 self.line_number += 1
#                 contents = group_match(line, LOG_LINE)
#                 if not contents:
#                     continue
#
#                 line = LogLine(
#                     parent=self,
#                     log=self.alias,
#                     raw=line,
#                     line_number=self.line_number,
#                     timestamp=(datetime.fromisoformat(contents['timestamp']) if self.parse_datetime
#                                else contents['timestamp']),
#                     message=contents['message'],
#                 )
#
#                 if self.should_accept(line):
#                     yield line
#
#     def should_accept(self, line: LogLine) -> bool:
#         timestamp = line['timestamp']
#         if self.from_ts is not None and timestamp <= self.from_ts:
#             return False
#
#         if self.to_ts is not None and timestamp >= self.to_ts:
#             return False
#
#         return True
#
#     def peek(self) -> Optional[LogLine]:
#         return self.look_ahead
#
#     def latest_timestamp(self) -> Optional[datetime]:
#         return self.peek()['timestamp'] if self.peek() is not None else None
#
#     def context(self) -> str:
#         return f'{self.path}:{self.line_number}'
#
#
# def _exclude_empty(logs: Iterable[LogIterator]):
#     return [log for log in logs if log.peek() is not None]
#
#
# class CollatingLogIterator(LogIterator):
#
#     def __init__(self, logs: List[SingleLogIterator]):
#         self.logs = _exclude_empty(logs)
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         if not self.logs:
#             raise StopIteration()
#
#         log = self.logs[0]
#         value = next(log)
#         if log.peek() is None:
#             self.logs.pop(0)
#         return value
#
#     def peek(self) -> Optional[LogLine]:
#         if not self.logs:
#             return None
#
#         return self.logs[0].peek()
#
#     def context(self) -> str:
#         if not self.logs:
#             raise Exception('Undefined context.')
#
#         return self.logs[0].context()
#
#
# class MergingLogIterator(LogIterator):
#     def __init__(self, logs: List[SingleLogIterator]):
#         self.logs = _exclude_empty(logs)
#         heapify(self.logs)
#
#     def __iter__(self):
#         return self
#
#     def __next__(self) -> LogLine:
#         if not self.logs:
#             raise StopIteration()
#
#         # by construction, we can't have any empty iterators at this point, so the call to next always succeeds.
#         log = heappop(self.logs)
#         value = next(log)
#
#         # if the iterator still has stuff in it...
#         if log.peek() is not None:
#             heappush(self.logs, log)
#
#         return value
#
#     def peek(self) -> Optional[LogLine]:
#         if not self.logs:
#             return None
#
#         return self.logs[0].peek()
#
#     def context(self) -> str:
#         if not self.logs:
#             raise Exception('Undefined context.')
#
#         return self.logs[0].context()
