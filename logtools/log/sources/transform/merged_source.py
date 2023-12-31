from heapq import heapify, heappop, heappush
from typing import Iterator

from logtools.log.base import LogSource, TimestampedLogLine, TLocation
from logtools.log.sources.transform.ordered_source import OrderedSource


class MergedSource(LogSource[TimestampedLogLine[TLocation]]):
    def __init__(self, *sources: OrderedSource[TLocation]):
        self.sources = [source for source in sources if source.peek is not None]
        heapify(self.sources)

    def __iter__(self) -> Iterator[TimestampedLogLine[TLocation]]:
        return self

    def __next__(self) -> TimestampedLogLine[TLocation]:
        if not self.sources:
            raise StopIteration()

        # by construction, we can't have any empty iterators at this point, so the call to next always succeeds.
        log = heappop(self.sources)
        value = next(log)

        # if the iterator still has stuff in it...
        if log.peek is not None:
            heappush(self.sources, log)

        return value
