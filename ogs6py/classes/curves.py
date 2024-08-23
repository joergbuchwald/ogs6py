"""
Copyright (c) 2012-2024, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from typing import Any

from lxml import etree as ET

from ogstools.ogs6py import build_tree


class Curves(build_tree.BuildTree):
    """
    Class to create the curve section of the project file.
    """

    def __init__(self, tree: ET.ElementTree) -> None:
        self.tree = tree
        self.root = self._get_root()
        self.curves = self.populate_tree(self.root, "curves", overwrite=True)

    def add_curve(self, **args: Any) -> None:
        """
        Adds a new curve.

        Parameters
        ----------
        name : `str`
        coords : `list`
        values : `list`
        """
        if "name" not in args:
            msg = "No curve name given."
            raise KeyError(msg)
        if "coords" not in args:
            msg = "No coordinates given."
            raise KeyError(msg)
        if "values" not in args:
            msg = "No values given."
            raise KeyError(msg)
        if len(args["coords"]) != len(args["values"]):
            msg = """Number of time coordinate points differs \
                     from number of values"""
            raise ValueError(msg)
        curve = self.populate_tree(self.curves, "curve")
        self.populate_tree(curve, "name", args["name"])
        coord_str = ""
        value_str = ""
        for i, coord in enumerate(args["coords"]):
            if i < (len(args["coords"]) - 1):
                coord_str = coord_str + str(coord) + " "
                value_str = value_str + str(args["values"][i]) + " "
            if i == (len(args["coords"]) - 1):
                coord_str = coord_str + str(coord)
                value_str = value_str + str(args["values"][i])
        self.populate_tree(curve, "coords", text=coord_str)
        self.populate_tree(curve, "values", text=value_str)
