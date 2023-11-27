# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class Curves(build_tree.BuildTree):
    """
    Class to create the curve section of the project file.
    """
    def __init__(self, tree):
        self.tree = tree
        self.root = self._get_root()
        self.curves = self.populate_tree(self.root, "curves", overwrite=True)

    def add_curve(self, **args):
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
        curve = self.populate_tree(self.curves, "curve")
        self.populate_tree(curve, "name", args['name'])
        coord_str = ""
        value_str = ""
        for i, coord in enumerate(args["coords"]):
            if i < (len(args["coords"])-1):
                coord_str = coord_str + str(coord) + " "
                value_str = value_str + str(args["values"][i]) + " "
            if i == (len(args["coords"])-1):
                coord_str = coord_str + str(coord)
                value_str = value_str + str(args["values"][i])
        self.populate_tree(curve, 'coords', text=coord_str)
        self.populate_tree(curve, 'values', text=value_str)
