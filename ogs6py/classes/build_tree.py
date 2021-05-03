# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""

# pylint: disable=C0103, R0902, R0914, R0913
class BUILD_TREE(object):
    def __init__(self, **args):
        self.tree = {}

    def _convertargs(self, args):
        for item, value in args.items():
            if not ((type(value) is list) or (type(value) is dict)):
                args[item] = str(value)

    def populateTree(self, tag, text='', attr=None, children=None):
        if attr is None:
            attr = {}
        if children is None:
            children = {}
        return {'tag': tag, 'text': text, 'attr': attr, 'children': children}

