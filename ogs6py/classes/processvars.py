# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class ProcessVars(build_tree.BuildTree):
    """
    Managing the process variables section in the project file.
    """
    def __init__(self, tree):
        self.tree = tree
        self.root = self._get_root()
        self.pvs = self.populate_tree(self.root, 'process_variables', overwrite=True)

    def set_ic(self, **args):
        """
        Set initial conditions.

        Parameters
        ----------
        process_variable_name : `str`
        components : `int` or `str`
        order : `int` or `str`
        initial_condition` : `str`
        """
        self._convertargs(args)
        if "process_variable_name" not in args:
            raise KeyError("No process_variable_name given")
        if "components" not in args:
            raise KeyError("Please provide the number of components \
                            of the given process variable.")
        if "order" not in args:
            raise KeyError("Out of order. Please specify the polynomial order \
                                of the process variable's shape functions.")
        if "initial_condition" not in args:
            raise KeyError("No initial_condition specified.")
        pv = self.populate_tree(self.pvs, 'process_variable')
        self.populate_tree(pv, 'name', text=args['process_variable_name'])
        self.populate_tree(pv, 'components', text=args['components'])
        self.populate_tree(pv, 'order', text=args['order'])
        self.populate_tree(pv, 'initial_condition', text=args['initial_condition'])

    def add_bc(self, **args):
        """
        Adds a boundary condition.

        Parameters
        ----------
        process_variable_name : `str`
        type : `str`
        geometrical_set : `str`
        geometry : `str`
        component : `int` or `str`
        parameter : `str`
        bc_object : `str`
        mesh : `str`
        """
        self._convertargs(args)
        if "process_variable_name" not in args:
            raise KeyError("No process variable name specified.")
        if "type" not in args:
            raise KeyError("No type given.")
        process_variable_name = args['process_variable_name']
        pv = self.root.find(f"./process_variables/process_variable[name=\'{process_variable_name}\']")
        if pv is None:
            raise KeyError("You need to set initial condition for that process variable first.")
        boundary_conditions = pv.find("./boundary_conditions")
        if boundary_conditions is None:
            boundary_conditions = self.populate_tree(pv, 'boundary_conditions')
        boundary_condition = self.populate_tree(boundary_conditions, 'boundary_condition')
        self.populate_tree(boundary_condition, 'type', text=args['type'])
        if "geometrical_set" in args:
            if "geometry" not in args:
                raise KeyError("You need to provide a geometry.")
            self.populate_tree(boundary_condition, 'geometrical_set', text=args['geometrical_set'])
            self.populate_tree(boundary_condition, 'geometry', text=args['geometry'])
        elif "mesh" in args:
            self.populate_tree(boundary_condition, 'mesh', text=args['mesh'])
        else:
            raise KeyError("You should provide either a geometrical set \
                                or a mesh to define BC for.")
        if "parameter" in args:
            if "component" in args:
                self.populate_tree(boundary_condition, 'component', text=args['component'])
            self.populate_tree(boundary_condition, 'parameter', text=args['parameter'])
        elif "bc_object" in args:
            if "component" in args:
                self.populate_tree(boundary_condition, 'component', text=args['component'])
            self.populate_tree(boundary_condition, 'bc_object', text=args['bc_object'])
        elif "u_0" in args:
            if "alpha" in args:
                self.populate_tree(boundary_condition, 'alpha', text=args['alpha'])
            self.populate_tree(boundary_condition, 'u_0', text=args['u_0'])
        else:
            raise KeyError("Please provide the parameter for Dirichlet \
                                        or Neumann BCs/bc_object for Python BCs")

    def add_st(self, **args):
        """
        add a source term

        Parameters
        ----------
        process_variable_name : `str`
        type : `str`
        geometrical_set : `str`
        geometry : `str`
        component : `int` or `str`
        parameter : `str`
        source_term_object : `str`
        mesh : `str`
        """
        self._convertargs(args)
        if "process_variable_name" not in args:
            raise KeyError("No process variable name specified.")
        if "type" not in args:
            raise KeyError("No type given.")
        process_variable_name = args['process_variable_name']
        pv = self.root.find(f"./process_variables/process_variable[name=\'{process_variable_name}\']")
        if pv is None:
            raise KeyError("You need to set initial condition for that process variable first.")
        source_terms = pv.find("./source_terms")
        if source_terms is None:
            source_terms = self.populate_tree(pv, 'source_terms')
        source_term = self.populate_tree(source_terms, 'source_term')
        self.populate_tree(source_term, 'type', text=args['type'])
        if "geometrical_set" in args:
            if "geometry" not in args:
                raise KeyError("You need to provide a geometry.")
            self.populate_tree(source_term, 'geometrical_set', text=args['geometrical_set'])
            self.populate_tree(source_term, 'geometry', text=args['geometry'])
        elif "mesh" in args:
            self.populate_tree(source_term, 'mesh', text=args['mesh'])
        else:
            raise KeyError("You should provide either a geometrical set \
                                or a mesh to define STs for.")
        if "parameter" in args:
            if "component" in args:
                self.populate_tree(source_term, 'component', text=args['component'])
            self.populate_tree(source_term, 'parameter', text=args['parameter'])
        elif "source_term_object" in args:
            if "component" in args:
                self.populate_tree(source_term, 'component', text=args['component'])
            self.populate_tree(source_term, 'source_term_object', text=args['source_term_object'])
        elif "u_0" in args:
            if "alpha" in args:
                self.populate_tree(source_term, 'alpha', text=args['alpha'])
            self.populate_tree(source_term, 'u_0', text=args['u_0'])
        else:
            raise KeyError("Please provide the parameter for Dirichlet \
                                        or Neumann ST/source_term_object for Python STs")
