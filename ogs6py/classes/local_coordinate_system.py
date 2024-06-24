# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class LocalCoordinateSystem(build_tree.BuildTree):
    """
    Class for defining a local coordinate system in the project file"
    """
    def __init__(self, tree):
        self.tree = tree
        self.root = self._get_root()
        self.lcs = None

    def add_basis_vec(self, **args):
        """
        Adds a basis

        Parameters
        ----------
        basis_vector_0 : `str`
                         name of the parameter containing the basis vector
        basis_vector_1 : `str`
                         name of the parameter containing the basis vector
        basis_vector_2 : `str`
                         name of the parameter containing the basis vector
        """
        self._convertargs(args)
        self.lcs = self.populate_tree(self.root, "local_coordinate_system", overwrite=True)
        if "basis_vector_0" not in args:
            raise KeyError("no vector given")
        self.populate_tree(self.lcs, "basis_vector_0", text=args["basis_vector_0"])
        if "basis_vector_1" in args:
            self.populate_tree(self.lcs, "basis_vector_1", text=args["basis_vector_1"])
        if "basis_vector_2" in args:
            self.populate_tree(self.lcs, "basis_vector_2", text=args["basis_vector_2"])
