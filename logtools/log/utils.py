from collections import defaultdict

from typing import Dict, Any

Tree = Dict[str, 'Tree'] | Any


def tree() -> Tree:
    return defaultdict(tree)
