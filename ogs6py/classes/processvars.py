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
    def __init__(self):
        self.tree = {
            'process_variables': {
                'tag': 'process_variables',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

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
        self.tree['process_variables']['children'][
                args['process_variable_name']] = self.populate_tree(
                                'process_variable', children={})
        processvar = self.tree['process_variables']['children'][args['process_variable_name']]
        processvar['children']['name'] = self.populate_tree('name',
                text=args['process_variable_name'], children={})
        processvar['children']['components'] = self.populate_tree('components',
                text=args['components'], children={})
        processvar['children']['order'] = self.populate_tree('order', text=args['order'],
                children={})
        processvar['children']['initial_condition'] = self.populate_tree(
                'initial_condition', text=args['initial_condition'], children={})

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
        if args['process_variable_name'] not in self.tree['process_variables']['children']:
            raise KeyError("You need to set initial condition for that process variable first.")
        if "boundary_conditions" not in self.tree['process_variables']['children'][
                args['process_variable_name']]['children']:
            self.tree['process_variables']['children'][args['process_variable_name']]['children'][
                    'boundary_conditions'] = self.populate_tree('boundary_conditions', children={})
        boundary_conditions = self.tree['process_variables'][
                    'children'][args['process_variable_name']]['children']['boundary_conditions']
        if "geometrical_set" in args:
            if "geometry" not in args:
                raise KeyError("You need to provide a geometry.")
            cpnts = args.get('component','0')
            boundary_conditions['children'][args['geometrical_set']+args['geometry'] +
                    cpnts] = self.populate_tree('boundary_condition', children={})
            boundary_condition = boundary_conditions['children'][
                    args['geometrical_set'] + args['geometry'] + cpnts]
            boundary_condition['children']['type'] = self.populate_tree('type',
                    text=args['type'], children={})
            boundary_condition['children']['geometrical_set'] = self.populate_tree(
                    'geometrical_set', text=args['geometrical_set'], children={})
            boundary_condition['children']['geometry'] = self.populate_tree(
                                'geometry', text=args['geometry'], children={})
            if "parameter" in args:
                if "component" in args:
                    boundary_condition['children']['component'] = self.populate_tree(
                            'component', text=args['component'], children={})
                boundary_condition['children']['parameter'] = self.populate_tree(
                        'parameter', text=args['parameter'], children={})
            elif "bc_object" in args:
                if "component" in args:
                    boundary_condition['children']['component'] = self.populate_tree(
                            'component', text=args['component'], children={})
                boundary_condition['children']['bc_object'] = self.populate_tree(
                        'bc_object', text=args['bc_object'], children={})
            elif "u_0" in args:
                if "alpha" in args:
                    boundary_condition['children']['alpha'] = self.populate_tree(
                            'alpha', text=args['alpha'], children={})
                boundary_condition['children']['u_0'] = self.populate_tree(
                        'u_0', text=args['u_0'], children={})
            else:
                raise KeyError("Please provide the parameter for Dirichlet \
                                        or Neumann BC/bc_object for Python BC")
        elif "mesh" in args:
            cpnts = args.get('component','0')
            boundary_conditions['children'][args['mesh']+cpnts] = self.populate_tree(
                    'boundary_condition', children={})
            boundary_condition = boundary_conditions['children'][args['mesh']+cpnts]
            boundary_condition['children']['type'] = self.populate_tree('type',
                    text=args['type'], children={})
            boundary_condition['children']['mesh'] = self.populate_tree(
                        'mesh', text=args['mesh'], children={})
            if "parameter" in args:
                if "component" in args:
                    boundary_condition['children']['component'] = self.populate_tree(
                            'component', text=args['component'], children={})
                boundary_condition['children']['parameter'] = self.populate_tree(
                        'parameter', text=args['parameter'], children={})
            elif "bc_object" in args:
                if "component" in args:
                    boundary_condition['children']['component'] = self.populate_tree(
                            'component', text=args['component'], children={})
                boundary_condition['children']['bc_object'] = self.populate_tree(
                        'bc_object', text=args['bc_object'], children={})
            elif "u_0" in args:
                if "alpha" in args:
                    boundary_condition['children']['alpha'] = self.populate_tree(
                            'alpha', text=args['alpha'], children={})
                boundary_condition['children']['u_0'] = self.populate_tree(
                        'u_0', text=args['u_0'], children={})
            else:
                raise KeyError("Please provide the parameter for Dirichlet \
                                    or Neumann BC/bc_object for Python BC")
        else:
            raise KeyError("You should provide either a geometrical set \
                                or a mesh to define BC for.")

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
        if args['process_variable_name'] not in self.tree['process_variables']['children']:
            raise KeyError(
                    "You need to set initial condition for that process variable first.")
        self.tree['process_variables']['children'][args['process_variable_name']]['children'][
                'source_terms'] = self.populate_tree('source_terms', children={})
        source_terms = self.tree['process_variables']['children'][args['process_variable_name']][
                'children']['source_terms']
        if "geometrical_set" in args:
            if "geometry" in args:
                source_terms['children'][args['geometrical_set'] +
                        args['geometry']] = self.populate_tree('source_term', children={})
                source_term = source_terms['children'][args['geometrical_set'] + args['geometry']]
                source_term['children']['type'] = self.populate_tree('type', text=args['type'],
                        children={})
                source_term['children']['geometrical_set'] = self.populate_tree(
                        'geometrical_set', text=args['geometrical_set'], children={})
                source_term['children']['geometry'] = self.populate_tree(
                                'geometry', text=args['geometry'], children={})
                if "parameter" in args:
                    if "component" in args:
                        source_term['children']['component'] = self.populate_tree(
                                'component', text=args['component'], children={})
                    source_term['children']['parameter'] = self.populate_tree(
                            'parameter', text=args['parameter'], children={})
                elif "source_term_object" in args:
                    if "component" in args:
                        source_term['children']['component'] = self.populate_tree(
                                'component', text=args['component'], children={})
                    source_term['children']['source_term_object'] = self.populate_tree(
                            'source_term_object', text=args['source_term_object'], children={})
                else:
                    raise KeyError("Please provide the parameter for Dirichlet \
                                        or Neumann BC/bc_object for Python BC")
            else:
                raise KeyError("You need to provide a geometry.")
        elif "mesh" in args:
            source_terms['children'][args['mesh']] = self.populate_tree(
                    'source_term', children={})
            source_term = source_terms['children'][args['mesh']]
            source_term['children']['type'] = self.populate_tree(
                        'type', text=args['type'], children={})
            source_term['children']['mesh'] = self.populate_tree(
                        'mesh', text=args['mesh'], children={})
            if "parameter" in args:
                if "component" in args:
                    source_term['children']['component'] = self.populate_tree(
                            'component', text=args['component'], children={})
                source_term['children']['parameter'] = self.populate_tree(
                                    'parameter', text=args['parameter'], children={})
            elif "source_term_object" in args:
                if "component" in args:
                    source_term['children']['component'] = self.populate_tree(
                                    'component', text=args['component'], children={})
                source_term['children']['source_term_object'] = self.populate_tree(
                            'source_term_object', text=args['source_term_object'], children={})
            else:
                raise KeyError("Please provide the parameter for the source term\
                            /source term_object for Python BC")
        else:
            raise KeyError("You should provide either a geometrical set \
                        or a mesh to define the source terms for.")
