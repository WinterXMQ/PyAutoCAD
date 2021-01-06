#!/usr/bin/env python
# -*- coding: utf-8 -*-
# date: 2020.12.24
from pyautocad.entities import ALine
from pyautocad.types import APoint, Vector
import unittest


class EntitiesTestCase(unittest.TestCase):
    def test_ALine(self):
        l1 = ALine([10, 10], [20, 20])
        self.assertEqual(str(l1), 'Aline(APoint(10.00, 10.00, 0.00), APoint(20.00, 20.00, 0.00))')

        # create Line by Point and Vector
        p1 = APoint(1, 0, 0)
        l2 = ALine.create_from_vector(Vector([3, 4, 0]), p1)
        l3 = ALine(p1, p1 + [0.6, 0.8, 0])
        self.assertEqual(l2, l3)


if __name__ == '__main__':
    unittest.main()
