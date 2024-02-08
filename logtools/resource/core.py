import abc
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Iterator, Optional


@dataclass(frozen=True)
class Namespace:
    name: str
    run_id: tuple[str, ...]
    indices: tuple[str, ...]


@dataclass(frozen=True)
class Pod:
    name: str
    namespace: str
    run_id: str
    indices: tuple[str, ...]


class TestStatus(Enum):
    passed = 'passed'
    failed = 'failed'


@dataclass(frozen=True)
class TestRun:
    id: str
    run_id: str
    test_name: str
    pods: str
    start: datetime
    end: datetime
    duration: float
    status: TestStatus


@dataclass(frozen=True)
class TestRunDescription:
    test_run: TestRun
    error: Optional[str]
    stacktrace: Optional[str]


class Repository(abc.ABC):
    @abc.abstractmethod
    def namespaces(self, prefix: Optional[str] = None) -> Iterator[Namespace]:
        ...

    @abc.abstractmethod
    def pods(self, prefix: Optional[str] = None, run_id: Optional[str] = None):
        ...

    @abc.abstractmethod
    def test_runs(self, run_id: str, failed_only=False) -> Iterator[TestRun]:
        ...

    @abc.abstractmethod
    def describe_test_run(self, test_run_id: str) -> TestRunDescription:
        ...
