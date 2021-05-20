# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class LinSolvers(build_tree.BuildTree):
    """
    Class for defining a linear solvers in the project file"
    """
    def __init__(self):
        self.tree = {
            'linear_solvers': {
                'tag': 'linear_solvers',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def add_lin_solver(self, **args):
        """
        Adds a linear solver

        Parameters
        ----------
        name : `str`
        kind : `str`
                one of `petsc`, `eigen` or `lis`
        solver_type : `str`
        precon_type : `str`, optional
        max_iteration_step : `int`, optional
        scaling : `str`, optional
                  1 or 0
        prefix : `str`, optional
                 required for petsc solver
        """
        self._convertargs(args)
        if not "name" in args:
            raise KeyError("You need to provide a name for the linear solver.")
        if not args['name'] in self.tree['linear_solvers']['children']:
            self.tree['linear_solvers']['children'][
                args['name']] = self.populate_tree('linear_solver', children={})
        linear_solver = self.tree['linear_solvers']['children'][
            args['name']]['children']
        if not 'name' in linear_solver:
            linear_solver['name'] = self.populate_tree('name', text=args['name'],children={})
        if not "kind" in args:
            raise KeyError("No kind given. Please specify the linear \
                        solver library (e.g.: eigen, petsc, lis).")
        if not "solver_type" in args:
            raise KeyError("No solver_type given.")
        if args['kind'] == "eigen":
            linear_solver['eigen'] = self.populate_tree('eigen', children={})
            linear_solver['eigen']['children']['solver_type'] = self.populate_tree(
                    'solver_type', text=args['solver_type'], children={})
            if "precon_type" in args:
                linear_solver['eigen']['children']['precon_type'] = self.populate_tree(
                    'precon_type', text=args['precon_type'], children={})
            if "max_iteration_step" in args:
                linear_solver['eigen']['children']['max_iteration_step'] = self.populate_tree(
                    'max_iteration_step', text=args['max_iteration_step'], children={})
            if "error_tolerance" in args:
                linear_solver['eigen']['children']['error_tolerance'] = self.populate_tree(
                    'error_tolerance', text=args['error_tolerance'], children={})
            if "scaling" in args:
                linear_solver['eigen']['children']['scaling'] = self.populate_tree(
                        'scaling', text=args['scaling'], children={})
        elif args['kind'] == "lis":
            string = (f"-i {args['solver_type']} -p {args['precon_type']}"
                    f" -tol {args['error_tolerance']}"
                    f" -maxiter {args['max_iteration_step']}")
            linear_solver['lis'] = self.populate_tree('lis', text=string, children={})
        elif args['kind'] == "petsc":
            if 'prefix' not in args:
                KeyError("No prefix given.")
            prefix = args['prefix']
            linear_solver['petsc'] = self.populate_tree('petsc', children={})
            linear_solver['petsc']['children'][
                'prefix'] = self.populate_tree('prefix', text=prefix, children={})
            string = (f"-{prefix}_ksp_type {args['solver_type']}  -{prefix}_pc_type"
                    f" {args['precon_type']} -{prefix}_ksp_rtol {args['error_tolerance']}"
                    f" -{prefix}_ksp_max_it {args['max_iteration_step']}")
            linear_solver['petsc']['children'][
            'parameters'] = self.populate_tree('parameters', text=string, children={})
