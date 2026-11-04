"""An exact lower bound on every finite source/terrain column gap.

Any point of a triangle, including a collapsed triangle, lies between its
vertices' minimum and maximum heights. Binary input heights are converted to
exact fractions before subtraction. This certifies only that a pair cannot have
a gap strictly below the existing -1/2m threshold; it supplies no contact/root.
"""
from fractions import Fraction
import math


def height_fraction(value):
    value = float(value)
    assert math.isfinite(value)
    return Fraction(value)


def cannot_have_negative_gap(source_minimum, ground_maximum):
    assert isinstance(source_minimum, Fraction)
    assert isinstance(ground_maximum, Fraction)
    return source_minimum - ground_maximum >= Fraction(-1, 2)
