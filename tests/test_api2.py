#!/usr/bin/env python
# -*- coding: utf-8 -*-
# date: 2020.12.25
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
from pyautocad.api import Autocad
from pyautocad.types import APoint
import unittest


class ApiTest2(unittest.TestCase):
    def setUp(self):
        self.cad = Autocad(True)

    def test_create_block(self):
        acad = self.cad
        p1 = APoint(100, 0)
        block = acad.create_block(p1, 'create')
        block.AddCircle(p1, 10)
        acad.model.InsertBlock(p1, 'create', 1, 1, 1, 0)


if __name__ == '__main__':
    unittest.main()
