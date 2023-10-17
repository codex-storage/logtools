from heapq import heapify, heappop, heappush

from logtools.log.sources.log_source import LogSource, TLocation
from logtools.log.sources.ordered_source import OrderedSource


class MergedSource(LogSource[TLocation]):
    def __init__(self, *sources: OrderedSource[TLocation]):
        self.sources = [source for source in sources if source.peek is not None]
        heapify(self.sources)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.sources:
            raise StopIteration()

        # by construction, we can't have any empty iterators at this point, so the call to next always succeeds.
        log = heappop(self.sources)
        value = next(log)

        # if the iterator still has stuff in it...
        if log.peek is not None:
            heappush(self.sources, log)

        return value
