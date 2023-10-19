import argparse
from typing import Tuple


def kv_pair(raw: str) -> Tuple[str, str]:
    """
    Parse a string of the form 'key=value' and return a tuple (key, value).
    """
    if '=' not in raw:
        msg = f'{raw} is not a valid key=value pair'
        raise argparse.ArgumentTypeError(msg)

    key, value = raw.split("=", 1)
    return key, value
