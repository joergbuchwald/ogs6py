# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class NONLINSOLVERS(build_tree.BUILD_TREE):
    """
    Adds a non-linearsolver section in the project file.
    """
    def __init__(self):
        self.tree = {
            'nonlinear_solvers': {
                'tag': 'nonlinear_solvers',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def addNonlinSolver(self, **args):
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
        self.tree['nonlinear_solvers']['children'][
                args['name']] = self.populateTree('nonlinear_solver', children={})
        nonlin_solver = self.tree['nonlinear_solvers']['children'][args['name']]['children']
        nonlin_solver['name'] = self.populateTree('name', text=args['name'], children={})
        nonlin_solver['type'] = self.populateTree('type', text=args['type'], children={})
        nonlin_solver['max_iter'] = self.populateTree('max_iter', text=args['max_iter'],
                children={})
        nonlin_solver['linear_solver'] = self.populateTree('linear_solver',
                text=args['linear_solver'], children={})
        if "damping" in args:
            nonlin_solver['damping'] = self.populateTree('damping', text=args['damping'],
                    children={})
