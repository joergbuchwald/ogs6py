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
    """
    Class containing the geometry file.
    """
    def __init__(self):
        self.tree = {
            'geometry': {
                'tag': 'geometry',
                'text': "",
                'attr': {},
                'children': {}
            }
        }

    def addGeom(self, filename):
        """
        Adds a geometry file.

        Parameters
        ----------
        filename : `str`
        """
        self.tree['geometry']['text'] = filename
