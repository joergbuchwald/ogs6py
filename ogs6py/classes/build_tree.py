# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
from lxml import etree as ET

# pylint: disable=C0103, R0902, R0914, R0913
class BuildTree:
    """ helper class to create a nested dictionary
    representing the xml structure
    """
    def __init__(self, tree):
        self.tree = tree

    def _get_root(self):
        root = self.tree.getroot()
        return root

    @classmethod
    def _convertargs(cls, args):
        """
        convert arguments that are not lists or dictionaries to strings
        """
        for item, value in args.items():
            if not isinstance(value, (list, dict)):
                args[item] = str(value)

    @classmethod
    def populate_tree(cls, parent, tag, text='', attr=None, overwrite=False):
        """
        method to create dictionary from an xml entity
        """
        q = None
        if not tag is None:
            if overwrite is True:
                for child in parent:
                    if child.tag == tag:
                        q = child
            if q is None:
                q = ET.SubElement(parent, tag)
            if not text is None:
                q.text = str(text)
            if not attr is None:
                for key, val in attr.items():
                    q.set(key, str(val))
        return q

    @classmethod
    def get_child_tag(cls, parent, tag, attr=None, attr_val=None):
        """
        search for child tag based on tag and possible attributes
        """
        q = None
        for child in parent:
            if child.tag == tag:
                if not ((attr is None) and (attr_val is None)):
                    if child.get(attr) == attr_val:
                        q = child
                else:
                    q = child
        return q

    @classmethod
    def get_child_tag_for_type(cls, parent, tag, subtagval, subtag="type"):
        """
        search for child tag based on subtag type
        """
        q = None
        for child in parent:
            if child.tag == tag:
                for subchild in child:
                    if subchild.tag == subtag:
                        if subchild.text == subtagval:
                            q = child
        return q
