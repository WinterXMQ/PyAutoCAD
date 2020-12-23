#!/usr/bin/env python
# -*- coding: utf-8 -*-
# date: 2020.12.24
from pyautocad.entities import ALine
import unittest


class EntitiesTestCase(unittest.TestCase):
    def test_ALine(self):
        l1 = ALine([10, 10], [20, 20])
        self.assertEqual(str(l1), 'Aline(APoint(10.00, 10.00, 0.00), APoint(20.00, 20.00, 0.00))')


if __name__ == '__main__':
    unittest.main()
