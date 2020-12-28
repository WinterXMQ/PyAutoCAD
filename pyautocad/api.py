#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    pyautocad.api
    ~~~~~~~~~~~~~~~

    Main AutoCAD automation object.

    :copyright: (c) 2012 by Roman Haritonov.
    :license: BSD, see LICENSE.txt for more details.
"""

__all__ = ['Autocad', 'ACAD']

import logging
import comtypes
import glob
import os
try:
    import comtypes.client
    # generate modules for work with ACAD constants
    for pattern in ("acax*enu.tlb", "axdb*enu.tlb"):
        pattern = os.path.join(
            r"C:\Program Files\Common Files\Autodesk Shared",
            pattern
        )
        tlib = glob.glob(pattern)[0]
        comtypes.client.GetModule(tlib)
    import comtypes.gen.AutoCAD as ACAD
except Exception:
    # we are under readthedocs.org and need to mock this
    ACAD = None

import pyautocad.types
from pyautocad.compat import basestring, xrange
from pyautocad.entities import *

logger = logging.getLogger(__name__)


class Autocad(object):
    """Main AutoCAD Automation object
    """

    def __init__(self, create_if_not_exists=False, visible=True):
        """
        :param create_if_not_exists: if AutoCAD doesn't run, then
                                     new instanse will be crated
        :param visible: new AutoCAD instance will be visible if True (default)
        """
        self._create_if_not_exists = create_if_not_exists
        self._visible = visible
        self._app = None

    @property
    def app(self):
        """Returns active :class:`AutoCAD.Application`

        if :class:`Autocad` was created with :data:`create_if_not_exists=True`,
        it will create :class:`AutoCAD.Application` if there is no active one
        """
        if self._app is None:
            try:
                self._app = comtypes.client.GetActiveObject('AutoCAD.Application', dynamic=True)
            except WindowsError:
                if not self._create_if_not_exists:
                    raise
                self._app = comtypes.client.CreateObject('AutoCAD.Application', dynamic=True)
                self._app.Visible = self._visible
        return self._app

    @property
    def doc(self):
        """ Returns `ActiveDocument` of current :attr:`Application`"""
        return self.app.ActiveDocument

    #: Same as :attr:`doc`
    ActiveDocument = doc

    #: Same as :attr:`app`
    Application = app

    @property
    def model(self):
        """ `ModelSpace` from active document """
        return self.doc.ModelSpace

    def iter_layouts(self, doc=None, skip_model=True):
        """Iterate layouts from *doc*

        :param doc: document to iterate layouts from if `doc=None` (default), :attr:`ActiveDocument` is used
        :param skip_model: don't include :class:`ModelSpace` if `True`
        """
        if doc is None:
            doc = self.doc
        for layout in sorted(doc.Layouts, key=lambda x: x.TabOrder):
            if skip_model and not layout.TabOrder:
                continue
            yield layout

    def iter_objects(self, object_name_or_list=None, block=None,
                     limit=None, dont_cast=False):
        """Iterate objects from `block`

        :param object_name_or_list: part of object type name, or list of it
        :param block: Autocad block, default - :class:`ActiveDocument.ActiveLayout.Block`
        :param limit: max number of objects to return, default infinite
        :param dont_cast: don't retrieve best interface for object, may speedup
                          iteration. Returned objects should be casted by caller
        """
        if block is None:
            block = self.doc.ActiveLayout.Block
        object_names = object_name_or_list
        if object_names:
            if isinstance(object_names, basestring):
                object_names = [object_names]
            object_names = [n.lower() for n in object_names]

        count = block.Count
        for i in xrange(count):
            item = block.Item(i)  # it's faster than `for item in block`
            if limit and i >= limit:
                return
            if object_names:
                object_name = item.ObjectName.lower()
                if not any(possible_name in object_name for possible_name in object_names):
                    continue
            if not dont_cast:
                item = self.best_interface(item)
            yield item

    def iter_objects_fast(self, object_name_or_list=None, container=None, limit=None):
        """Shortcut for `iter_objects(dont_cast=True)`

        Shouldn't be used in normal situations
        """
        return self.iter_objects(object_name_or_list, container, limit, dont_cast=True)

    def find_one(self, object_name_or_list, container=None, predicate=None):
        """Returns first occurance of object which match `predicate`

        :param object_name_or_list: like in :meth:`iter_objects`
        :param container: like in :meth:`iter_objects`
        :param predicate: callable, which accepts object as argument
                          and returns `True` or `False`
        :returns: Object if found, else `None`
        """
        if predicate is None:
            predicate = bool
        for obj in self.iter_objects(object_name_or_list, container):
            if predicate(obj):
                return obj
        return None

    def best_interface(self, obj):
        """ Retrieve best interface for object """
        return comtypes.client.GetBestInterface(obj)

    def prompt(self, text):
        """ Prints text in console and in `AutoCAD` prompt
        """
        print(text)
        self.doc.Utility.Prompt(u"%s\n" % text)

    def get_selection(self, text="Select objects"):
        """ Asks user to select objects

        :param text: prompt for selection
        """
        self.prompt(text)
        try:
            self.doc.SelectionSets.Item("SS1").Delete()
        except Exception:
            logger.debug('Delete selection failed')

        selection = self.doc.SelectionSets.Add('SS1')
        selection.SelectOnScreen()
        return selection

    def create_block(self, insert_pnt, block_name):
        """Create an empty Block

        :param insert_pnt: Block insert point :class: `APoint`
        :param block_name: Block's name :class: `str`
        :returns: Block object :class: `ActiveDocument.ActiveLayout.Block`
        """
        return self.doc.Blocks.Add(insert_pnt, block_name)

    def insert_block(self, insert_pnt, block_name, scale_x=1, scale_y=1, scale_z=1, rotation=0, layout=None):
        """Insert a block reference into layout(Including `Model`)

        :param insert_pnt:Block insert point :class: `APoint`
        :param block_name: Block's name :class: `str`
        :param scale_x: X coordination of the block scale rate :class: `double`
        :param scale_y: Y coordination of the block scale rate :class: `double`
        :param scale_z: Z coordination of the block scale rate :class: `double`
        :param rotation: Angle of the block's rotation
        :param layout: Working layout :class: `str`
        :returns: True/False, Operation successful or not :class: `bool`
        """
        # TODO: [insert_block]Layout need to be improved
        if layout is None or layout in ('Model', '模型'):
            self.model.InsertBlock(insert_pnt, block_name, scale_x, scale_y, scale_z, rotation)
            return True
        elif layout.startswith('Space'):
            # layout <= 'Space', 'Space_0', 'Space_name'
            if layout is 'Space':
                # TODO: [insert_block]Get Space Layout
                return False
            else:
                if not layout.startswith('Space_'):
                    return False
                index_or_name = layout[6:]
                # TODO: [insert_block]Convert str to int
                return False

    def add_entities(self, items, doc=None):
        """Add entities into Model,Space or Block

        :param items: The package of entities :class: `list`, `tuple`
        :param doc: The document where the entities draw on :class: `ModelSpace` or `PaperSpace` or `Block`
        :returns: The number of entities draw on :class: `int`
        """
        if doc is None:
            doc = self.model
        elif doc is str:
            # TODO: Get PaperSpace by str, like `Space_1` or `Space_name`
            doc = None

        if doc is None:
            return 0

        _rs = 0
        for item in items:
            if isinstance(item, ALine):
                if self.add_line(item.start, item.end) is not None:
                    _rs = _rs + 1
            elif isinstance(item, ACircle):
                if self.add_circle(item.center, item.radius) is not None:
                    _rs = _rs + 1
            # TODO: [add_entities]Add other entity

        return _rs

    def add_line(self, pnt_start, pnt_end, doc=None):
        """Add 3D line into Model, Space or Block

        :param pnt_start: Start point of line :class: `APoint`
        :param pnt_end: End point of line :class: `APoint`
        :param doc: Document, need to be com's object or None :class: `ModelSpace`, `PaperSpace` or `Block`
        :returns: AutoCAD's Line object or None
        """
        if pnt_start is None or pnt_end is None:
            return None

        if doc is None:
            doc = self.model

        return doc.AddLine(pnt_start, pnt_end)

    def add_circle(self, pnt_center, radius, doc=None):
        """Add 2D Circle into Model, Space or Block

        :param pnt_center: Center point of circle :class: `APoint`
        :param radius: Radius of circle, radius need be positive :class: `float`
        :param doc: Document, need to be com's object or None :class: `ModelSpace`, `PaperSpace` or `Block`
        :returns: AutoCAD's Line object or None
        """
        if pnt_center is None or radius <= 0:
            return None
        if doc is None:
            doc = self.model

        return doc.AddCircle(pnt_center, radius)

    #: shortcut for :func:`pyautocad.types.aDouble`
    aDouble = staticmethod(pyautocad.types.aDouble)
    #: shortcut for :func:`pyautocad.types.aInt`
    aInt = staticmethod(pyautocad.types.aInt)
    #: shortcut for :func:`pyautocad.types.aShort`
    aShort = staticmethod(pyautocad.types.aShort)

