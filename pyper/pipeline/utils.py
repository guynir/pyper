from typing import Union, Set, List, Optional, Tuple

__all__ = ['to_set']


def to_set(values: Optional[Union[Set, List, Tuple, object]]) -> Set:
    """
    Convert a given value(s) into a set.

    :param values: Values to convert (can be a single object, a set, a list or a tuple).
    :return: A set of values.
    """
    result: Set
    if values is None:
        result = set()
    elif isinstance(values, set):
        result = values
    elif isinstance(values, list) or isinstance(values, tuple):
        result = set(values)
    else:
        result = {values}

    return result
