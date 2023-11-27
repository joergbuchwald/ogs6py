# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class NonLinSolvers(build_tree.BuildTree):
    """
    Adds a non-linearsolver section in the project file.
    """
    def __init__(self, tree):
        self.tree = tree
        self.root = self._get_root()
        self.nlss = self.populate_tree(self.root, 'nonlinear_solvers', overwrite=True)

    def add_non_lin_solver(self, **args):
        """
        add a nonlinear solver.

        Parameters
        ----------
        name : `str`
        type : `str`
                one of `Picard` or `Newton`
        max_iter : `int` or `str`
        linear_solver : `str`
        damping : `float` or `str`
        """
        self._convertargs(args)
        if "name" not in args:
            raise KeyError("Missing name of the nonlinear solver.")
        if "type" not in args:
            raise KeyError("Please specify the type of the nonlinear solver.")
        if "max_iter" not in args:
            raise KeyError("Please provide the maximum number of iterations (max_iter).")
        if "linear_solver" not in args:
            raise KeyError("No linear_solver specified.")
        nls = self.populate_tree(self.nlss, "nonlinear_solver")
        self.populate_tree(nls, "name", text=args['name'])
        self.populate_tree(nls, "type", text=args['type'])
        self.populate_tree(nls, "max_iter", text=args['max_iter'])
        self.populate_tree(nls, "linear_solver", text=args['linear_solver'])
        if "damping" in args:
            self.populate_tree(nls, "damping", text=args['damping'])
