# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class GEO(build_tree.BUILD_TREE):
    def __init__(self, **args):
        self.tree = {
            'geometry': {
                'tag': 'geometry',
                'text': "",
                'attr': {},
                'children': {}
            }
        }

    def addGeom(self, **args):
        self._convertargs(args)
        if "filename" in args:
            self.tree['geometry']['text'] = args['filename']
        else:
            raise KeyError("No filename given")
