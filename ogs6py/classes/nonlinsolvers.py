"""
Copyright (c) 2012-2024, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from typing import Any

from lxml import etree as ET

from ogs6py.classes import build_tree


class NonLinSolvers(build_tree.BuildTree):
    """
    Adds a non-linearsolver section in the project file.
    """

    def __init__(self, tree: ET.ElementTree) -> None:
        self.tree = tree
        self.root = self._get_root()
        self.nlss = self.populate_tree(
            self.root, "nonlinear_solvers", overwrite=True
        )

    def add_non_lin_solver(self, **args: Any) -> None:
        """
        add a nonlinear solver.

        Parameters
        ----------
        name : `str`
            name
        type : `str`
            one of `Picard`, `Newton` or `PETScSNES`
        max_iter : `int` or `str`
            maximum iteraterion
        linear_solver : `str`
            linear solver configuration to chose
        damping : `float` or `str`
            damping for newton step
        """
        self._convertargs(args)
        if "name" not in args:
            msg = "Missing name of the nonlinear solver."
            raise KeyError(msg)
        if "type" not in args:
            msg = "Please specify the type of the nonlinear solver."
            raise KeyError(msg)
        if "max_iter" not in args:
            msg = "Please provide the maximum number of iterations (max_iter)."
            raise KeyError(msg)
        if "linear_solver" not in args:
            msg = "No linear_solver specified."
            raise KeyError(msg)
        nls = self.populate_tree(self.nlss, "nonlinear_solver")
        self.populate_tree(nls, "name", text=args["name"])
        self.populate_tree(nls, "type", text=args["type"])
        self.populate_tree(nls, "max_iter", text=args["max_iter"])
        self.populate_tree(nls, "linear_solver", text=args["linear_solver"])
        if "damping" in args:
            self.populate_tree(nls, "damping", text=args["damping"])
