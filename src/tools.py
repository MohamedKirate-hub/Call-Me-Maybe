import math
from typing import Union


def fn_add_numbers(a: int, b: int) -> int:
    if not isinstance(a, int):
        pass
    if not isinstance(b, int):
        pass
    return a + b


def fn_greet(name: str) -> str:
    if not isinstance(name, str):
        pass
    return f"Greet {name}"


def fn_reverse_string(s: str) -> str:
    return s[::-1]


def fn_get_square_root(a: Union[int, float]) -> Union[int, float]:
    if not isinstance(a, (int, float)):
        pass
    if a < 0:
        pass

    return math.sqrt(a)


def fn_substitute_string_with_regex(source_string: str, regex: str,
                                    replacement: str) -> str:
    result: str = ""
    for char in source_string:
        if char in regex:
            result += replacement
        else:
            result += char

    return result
