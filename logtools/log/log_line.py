import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Union, Optional

TOPICS = re.compile(r'(?P<key>\w+)=(?P<value>"[\w\s]+"|\S+)')


class LogLevel(Enum):
    trace = 'TRC'
    debug = 'DBG'
    info = 'INF'
    error = 'ERR'
    warning = 'WRN'
    note = 'NOT'


@dataclass
class LogLine:
    raw: str
    level: LogLevel
    timestamp: Union[str, datetime]
    message: str
    topics: str
    count: Optional[int]

    @property
    def fields(self):
        fields = TOPICS.findall(self.topics)
        return {key: value for key, value in fields} if fields else {}
