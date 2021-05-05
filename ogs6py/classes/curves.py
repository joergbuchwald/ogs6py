# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class CURVES(build_tree.BUILD_TREE):
    """
    Class to create the curve section of the project file.
    """
    def __init__(self):
        self.tree = {
            'curves': {
                'tag': 'curves',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def addCurve(self, **args):
        """
        Adds a new curve.

        Parameters
        ----------
        name : `str`
        coords : `list`
        values : `list`
        """
        if "name" not in args:
            raise KeyError("No curve name given.")
        if "coords" not in args:
            raise KeyError("No coordinates given.")
        if "values" not in args:
            raise KeyError("No values given.")
        if len(args["coords"]) != len(args["values"]):
            raise ValueError("Number of time coordinate points differs from number of values")
        entries = len(self.tree['curves']['children'])
        self.tree['curves']['children']['curve' + str(entries)] = self.populateTree('curve',
                children={})
        parameter = self.tree['curves']['children']['curve' + str(entries)]
        parameter['children']['name'] = self.populateTree('name', text=args['name'], children={})
        coord_str = ""
        value_str = ""
        for i, coord in enumerate(args["coords"]):
            if i < (len(args["coords"])-1):
                coord_str = coord_str + str(coord) + " "
                value_str = value_str + str(args["values"][i]) + " "
            if i == (len(args["coords"])-1):
                coord_str = coord_str + str(coord)
                value_str = value_str + str(args["values"][i])
        parameter['children']['coords'] = self.populateTree('coords', text=coord_str, children={})
        parameter['children']['values'] = self.populateTree('values', text=value_str, children={})
