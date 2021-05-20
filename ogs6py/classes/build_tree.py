# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""

# pylint: disable=C0103, R0902, R0914, R0913
class BuildTree:
    """ helper class to create a nested dictionary
    representing the xml structure
    """
    def __init__(self):
        self.tree = {}

    @classmethod
    def _convertargs(cls, args):
        """
        convert arguments that are not lists or dictionaries to strings
        """
        for item, value in args.items():
            if not isinstance(value, (list, dict)):
                args[item] = str(value)

    @classmethod
    def populate_tree(cls, tag, text='', attr=None, children=None):
        """
        method to create dictionary from an xml entity
        """
        if attr is None:
            attr = {}
        if children is None:
            children = {}
        return {'tag': tag, 'text': text, 'attr': attr, 'children': children}
