from enum import IntEnum

PageSize = 12


class Size(IntEnum):
    B = 1
    KB = 1024
    MB = 1024 ** 2
    GB = 1024 ** 3


def page_index(x: int) -> int:
    return x >> PageSize
