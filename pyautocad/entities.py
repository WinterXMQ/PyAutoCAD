#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyautocad.types import APoint


class ALine(object):
    """3D Line work with APoint and support in draw in `AutoCAD`

    Usage::

    >>> l1 = ALine([10, 10], [20, 20])
    Aline(APoint(10.00, 10.00, 0.00), APoint(20.00, 20.00, 0.00))
    """

    def __init__(self, start_point, end_point):
        if isinstance(start_point, APoint):
            self.start = start_point
        else:
            self.start = APoint(*start_point)
        if isinstance(end_point, APoint):
            self.end = end_point
        else:
            self.end = APoint(*end_point)

    @property
    def length(self):
        """The length of 3D line"""
        return self.start.distance_to(self.end)

    @property
    def middle(self):
        """The middle point of 3D line"""
        return APoint((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2, (self.start.z + self.end.z) / 2)

    def __str__(self):
        return 'Aline(%s, %s)' % (self.start, self.end)


class ACircle(object):
    """2D Circle

    """

    def __init__(self, pnt_center, radius):
        """Circle initial func

        :param pnt_center: Center point of circle :class: `APoint`
        :param radius: Radius of circle :class: `float`
        """
        if pnt_center is None or radius <= 0:
            raise ValueError('Center point is None or radius is negative')
        self.center = pnt_center
        self.radius = radius

    def diameter(self):
        return self.radius * 2

    def __str__(self):
        return 'ACircle(Center=%s, radius=%.2f)' % (self.center, self.radius)


class APolyline(object):
    """Polyline

    """
    def __init__(self, pnts=None):
        """Polyline initial func

        :param pnts: Point list(item need to be APoint or coordinate tuple) :class: `list` or `tuple`
        """
        self.points = []        # type: list[APoint]
        if pnts is not None and (isinstance(pnts, pnts) or isinstance(pnts, tuple)):
            for pnt in pnts:
                self.append(pnt)

    def append(self, pnt_or_list):
        """Add node into polyline, node need to be `APoint` or (x, y)/(x, y, z) `OCS` coordinate
        (z coordinate will be ignored)

        :param pnt_or_list: Node :class: `APoint`, `list` or `tuple`
        """
        if pnt_or_list is None:
            return
        if isinstance(pnt_or_list, APoint):
            self.points.append(pnt_or_list)
        if (isinstance(pnt_or_list, list) or isinstance(pnt_or_list, tuple)) \
                and len(pnt_or_list) >= 2:
            self.points.append(APoint(pnt_or_list))

    def __str__(self):
        rs = ""
        for pnt in self.points:
            rs += ',(%.2f, %.2f, %.2f)' % (pnt.x, pnt.y, pnt.z)
        return 'APolyline(%s)' % rs[1:]
