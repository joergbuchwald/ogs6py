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


class LinSolvers(build_tree.BuildTree):
    """
    Class for defining a linear solvers in the project file"
    """

    def __init__(self, tree: ET.ElementTree) -> None:
        self.tree = tree
        self.root = self._get_root()
        self.lss = self.populate_tree(
            self.root, "linear_solvers", overwrite=True
        )

    def add_lin_solver(self, **args: Any) -> None:
        """
        Adds a linear solver

        Parameters
        ----------
        name : `str`
            linear solver name
        kind : `str`
            one of `petsc`, `eigen` or `lis`
        solver_type : `str`
            Eigen solver type
        precon_type : `str`, optional
            Eigen preconditioner type
        max_iteration_step : `int`, optional
            max. iteration step
        scaling : `str`, optional
            scaling of diagonal
        error_tolerance : `float`
            error tolerance
        prefix : `str`, optional
            prefix for petsc solver
        parameters : `str`
            petsc parameter configuration
        lis : `str` for lis only
            lis parameter configuration
        """
        self._convertargs(args)
        if "name" not in args:
            msg = "You need to provide a name for the linear solver."
            raise KeyError(msg)
        ls = self.populate_tree(self.lss, "linear_solver", overwrite=True)
        self.populate_tree(ls, "name", text=args["name"], overwrite=True)
        if "kind" not in args:
            msg = """No kind given. Please specify the linear \
                        solver library (e.g.: eigen, petsc, lis)."""

            raise KeyError(msg)
        if args["kind"] == "eigen":
            eigen = self.populate_tree(ls, "eigen", overwrite=True)
            self.populate_tree(
                eigen, "solver_type", text=args["solver_type"], overwrite=True
            )
            if "precon_type" in args:
                self.populate_tree(
                    eigen,
                    "precon_type",
                    text=args["precon_type"],
                    overwrite=True,
                )
            if "max_iteration_step" in args:
                self.populate_tree(
                    eigen,
                    "max_iteration_step",
                    text=args["max_iteration_step"],
                    overwrite=True,
                )
            if "error_tolerance" in args:
                self.populate_tree(
                    eigen,
                    "error_tolerance",
                    text=args["error_tolerance"],
                    overwrite=True,
                )
            if "scaling" in args:
                self.populate_tree(
                    eigen, "scaling", text=args["scaling"], overwrite=True
                )
        elif args["kind"] == "lis":
            if "lis" in args:
                lis_string = args["lis"]
            else:
                lis_string = (
                    f"-i {args['solver_type']} -p {args['precon_type']}"
                    f" -tol {args['error_tolerance']}"
                    f" -maxiter {args['max_iteration_step']}"
                )
            self.populate_tree(ls, "lis", text=lis_string, overwrite=True)
        elif args["kind"] == "petsc":
            petsc = self.populate_tree(ls, "petsc", overwrite=True)
            prefix = ""
            if "prefix" in args:
                self.populate_tree(
                    petsc, "prefix", args["prefix"], overwrite=True
                )
                prefix = args["prefix"]
            if "parameters" in args:
                self.populate_tree(
                    petsc, "parameters", args["parameters"], overwrite=True
                )
            else:
                petsc_string = (
                    f"-{prefix}_ksp_type {args['solver_type']}  -{prefix}_pc_type"
                    f" {args['precon_type']} -{prefix}_ksp_rtol {args['error_tolerance']}"
                    f" -{prefix}_ksp_max_it {args['max_iteration_step']}"
                )
                self.populate_tree(
                    petsc, "parameters", petsc_string, overwrite=True
                )
