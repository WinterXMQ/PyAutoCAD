#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    pyautocad.types
    ~~~~~~~~~~~~~~~

    3D Points and and other AutoCAD data types.

    :copyright: (c) 2012 by Roman Haritonov.
    :license: BSD, see LICENSE.txt for more details.
"""
import array
import operator
import math
from decimal import Decimal
from math import sqrt

from pyautocad.compat import IS_PY3


class APoint(array.array):
    """ 3D point with basic geometric operations and support for passing as a
        parameter for `AutoCAD` Automation functions

    Usage::

        >>> p1 = APoint(10, 10)
        >>> p2 = APoint(20, 20)
        >>> p1 + p2
        APoint(30.00, 30.00, 0.00)

    Also it supports iterable as parameter::

        >>> APoint([10, 20, 30])
        APoint(10.00, 20.00, 30.00)
        >>> APoint(range(3))
        APoint(0.00, 1.00, 2.00)

    Supported math operations: `+`, `-`, `*`, `/`, `+=`, `-=`, `*=`, `/=`::

        >>> p = APoint(10, 10)
        >>> p + p
        APoint(20.00, 20.00, 0.00)
        >>> p + [10, 10, 10]
        APoint(20.00, 20.00, 10.00)
        >>> p * 2
        APoint(20.00, 20.00, 0.00)
        >>> p -= [1, 1, 1]
        >>> p
        APoint(9.00, 9.00, -1.00)

    It can be converted to `tuple` or `list`::

        >>> tuple(APoint(1, 1, 1))
        (1.0, 1.0, 1.0)

    """

    def __new__(cls, x_or_seq, y=0.0, z=0.0):
        return super(APoint, cls).__new__(cls, 'd', x_or_seq) if APoint.type_check(x_or_seq)\
            else super(APoint, cls).__new__(cls, 'd', (x_or_seq, y, z))

    @staticmethod
    def type_check(t):
        """ Check the type of data is identified to APoint
        :return: bool
        """
        return isinstance(t, (array.array, list, tuple)) and len(t) == 3

    @property
    def x(self):
        """ x coordinate of 3D point"""
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        """ y coordinate of 3D point"""
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        """ z coordinate of 3D point"""
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value

    def distance_to(self, other):
        """ Returns distance to `other` point

        :param other: :class:`APoint` instance or any sequence of 3 coordinates
        """
        return distance(self, other)

    def __add__(self, other):
        if APoint.type_check(other):
            return self.__left_op(self, other, operator.add)
        return NotImplemented

    def __sub__(self, other):
        if APoint.type_check(other):
            return self.__left_op(self, other, operator.sub)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.__left_op(self, other, operator.mul)
        return NotImplemented

    if IS_PY3:
        def __div__(self, other):
            if isinstance(other, (int, float)):
                return self.__left_op(self, other, operator.truediv)
            return NotImplemented
    else:
        def __div__(self, other):
            if isinstance(other, (int, float)):
                return self.__left_op(self, other, operator.div)
            return NotImplemented

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __floordiv__ = __div__
    __truediv__ = __div__

    def __neg__(self):
        return self.__left_op(self, -1, operator.mul)

    def __left_op(self, p1, p2, op):
        if isinstance(p2, (float, int)):
            return APoint(op(p1[0], p2), op(p1[1], p2), op(p1[2], p2))
        return APoint(op(p1[0], p2[0]), op(p1[1], p2[1]), op(p1[2], p2[2]))

    def __iadd__(self, p2):
        if APoint.type_check(p2):
            return self.__iop(p2, operator.add)
        return NotImplemented

    def __isub__(self, p2):
        if APoint.type_check(p2):
            return self.__iop(p2, operator.sub)
        return NotImplemented

    def __imul__(self, p2):
        if isinstance(p2, (float, int)):
            return self.__iop(p2, operator.mul)
        return NotImplemented

    def __idiv__(self, p2):
        if isinstance(p2, (float, int)):
            return self.__iop(p2, operator.div)
        return NotImplemented

    def __iop(self, p2, op):
        if isinstance(p2, (float, int)):
            self[0] = op(self[0], p2)
            self[1] = op(self[1], p2)
            self[2] = op(self[2], p2)
        else:
            self[0] = op(self[0], p2[0])
            self[1] = op(self[1], p2[1])
            self[2] = op(self[2], p2[2])
        return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'APoint(%.2f, %.2f, %.2f)' % tuple(self)

    def __eq__(self, other):
        if not isinstance(other, (array.array, list, tuple)):
            return False
        return tuple(self) == tuple(other)


def distance(p1, p2):
    """ Returns distance between two points `p1` and `p2`
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 +
                     (p1[1] - p2[1]) ** 2 +
                     (p1[2] - p2[2]) ** 2)


# next functions can accept parameters as aDouble(1, 2, 3)
# or as list or tuple aDouble([1, 2, 3])
def aDouble(*seq):
    """ Returns :class:`array.array` of doubles ('d' code) for passing to AutoCAD

    For 3D points use :class:`APoint` instead.
    """
    return _sequence_to_comtypes('d', *seq)


def aInt(*seq):
    """ Returns :class:`array.array` of ints ('l' code) for passing to AutoCAD
    """
    return _sequence_to_comtypes('l', *seq)


def aShort(*seq):
    """ Returns :class:`array.array` of shorts ('h' code) for passing to AutoCAD
    """
    return _sequence_to_comtypes('h', *seq)


def _sequence_to_comtypes(typecode='d', *sequence):
    if len(sequence) == 1:
        return array.array(typecode, sequence[0])
    return array.array(typecode, sequence)


class Vector(object):
    """Vector with basic geometric operations

    """

    def __init__(self, coordinates, error=1e10):
        try:
            if not coordinates:
                raise ValueError
            self.coordinates = tuple([Decimal(x) for x in coordinates])
            self.dimension = len(self.coordinates)
        except ValueError:
            raise ValueError('The coordinates must be nonempty')
        except TypeError:
            raise TypeError('The coordinates must be an iterable')

        self.error = error

    def __str__(self):
        return 'Vector({})'.format(self.coordinates)

    def __eq__(self, v):
        if not isinstance(v, Vector) or v.dimension != self.dimension:
            return False
        for x, y in zip(v.coordinates, self.coordinates):
            if abs(x - y) > self.error:
                return False
        return True

    def __add__(self, v):
        if isinstance(v, Vector) and v.dimension == self.dimension:
            return Vector([x + y for x, y in zip(self.coordinates, v.coordinates)])
        if isinstance(v, (array.array, list, tuple)) and len(v) == self.dimension:
            return Vector([x + y for x, y in zip(self.coordinates, v)])
        return NotImplemented

    def __sub__(self, v):
        if isinstance(v, Vector) and v.dimension == self.dimension:
            return Vector([x - y for x, y in zip(self.coordinates, v.coordinates)])
        if isinstance(v, (array.array, list, tuple)) and len(v) == self.dimension:
            return Vector([x - y for x, y in zip(self.coordinates, v)])
        return NotImplemented

    def __mul__(self, v):
        if isinstance(v, (float, int)):
            return Vector([x * Decimal(v) for x in self.coordinates])
        return NotImplemented

    def __truediv__(self, v):
        return self.__mul__(1.0 / v)

    def __getitem__(self, index):
        return self.coordinates[index]

    def __abs__(self):
        """Norm of vector
        """
        return sqrt(sum([x ** 2 for x in self.coordinates]))

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__

    def magnitude(self):
        return abs(self)

    def normalized(self):
        try:
            _magnitude = abs(self)
            return self / _magnitude
        except ZeroDivisionError:
            return Vector([0, 0, 0])
