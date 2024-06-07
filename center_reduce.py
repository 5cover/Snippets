#!/bin/env python3

from sys import argv
from statistics import mean, stdev
from typing import Iterable, TypeVar
from math import sqrt

T = TypeVar('T')
def stddev(data: Iterable[T], avg: T) -> T:
    # Koenig's variance formula
    return sqrt(mean(x ** 2 for x in data) - avg ** 2)

if __name__ == '__main__':
    numbers = [float(n) for n in argv[1:]]

    moyenne = mean(numbers)
    ecartype = stddev(numbers, moyenne)
    print(moyenne, ecartype)

    print(*[(n - moyenne) / ecartype for n in numbers])
