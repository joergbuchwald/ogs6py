"""
Copyright (c) 2012-2024, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from lxml import etree as ET

from ogs6py.classes import build_tree


class Geo(build_tree.BuildTree):
    """
    Class containing the geometry file.
    """

    def __init__(self, tree: ET.ElementTree) -> None:
        self.tree = tree
        self.root = self._get_root()
        self.populate_tree(self.root, "geometry", overwrite=True)

    def add_geometry(self, filename: str) -> None:
        """
        Adds a geometry file.

        Parameters
        ----------
        filename : `str`
        """
        self.populate_tree(self.root, "geometry", text=filename, overwrite=True)
