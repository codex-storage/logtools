from collections import defaultdict

from typing import Dict

Tree = Dict[str, 'Tree']


def tree() -> Tree:
    return defaultdict(tree)
