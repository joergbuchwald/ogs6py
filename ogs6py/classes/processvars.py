# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class PROCESSVARS(build_tree.BUILD_TREE):
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

    def setIC(self, **args):
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
                args['process_variable_name']] = self.populateTree(
                                'process_variable', children={})
        processvar = self.tree['process_variables']['children'][args['process_variable_name']]
        processvar['children']['name'] = self.populateTree('name',
                text=args['process_variable_name'], children={})
        processvar['children']['components'] = self.populateTree('components',
                text=args['components'], children={})
        processvar['children']['order'] = self.populateTree('order', text=args['order'],
                children={})
        processvar['children']['initial_condition'] = self.populateTree(
                'initial_condition', text=args['initial_condition'], children={})

    def addBC(self, **args):
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
                    'boundary_conditions'] = self.populateTree('boundary_conditions', children={})
        boundary_conditions = self.tree['process_variables'][
                    'children'][args['process_variable_name']]['children']['boundary_conditions']
        if "geometrical_set" in args:
            if "geometry" not in args:
                raise KeyError("You need to provide a geometry.")
            cpnts = args.get('component','0')
            boundary_conditions['children'][args['geometrical_set']+args['geometry'] +
                    cpnts] = self.populateTree('boundary_condition', children={})
            boundary_condition = boundary_conditions['children'][
                    args['geometrical_set'] + args['geometry'] + cpnts]
            boundary_condition['children']['type'] = self.populateTree('type',
                    text=args['type'], children={})
            boundary_condition['children']['geometrical_set'] = self.populateTree(
                    'geometrical_set', text=args['geometrical_set'], children={})
            boundary_condition['children']['geometry'] = self.populateTree(
                                'geometry', text=args['geometry'], children={})
            if "parameter" in args:
                if "component" in args:
                    boundary_condition['children']['component'] = self.populateTree(
                            'component', text=args['component'], children={})
                boundary_condition['children']['parameter'] = self.populateTree(
                        'parameter', text=args['parameter'], children={})
            elif "bc_object" in args:
                if "component" in args:
                    boundary_condition['children']['component'] = self.populateTree(
                            'component', text=args['component'], children={})
                boundary_condition['children']['bc_object'] = self.populateTree(
                        'bc_object', text=args['bc_object'], children={})
            else:
                raise KeyError("Please provide the parameter for Dirichlet \
                                        or Neumann BC/bc_object for Python BC")
        elif "mesh" in args:
            cpnts = args.get('component','0')
            boundary_conditions['children'][args['mesh']+cpnts] = self.populateTree(
                    'boundary_condition', children={})
            boundary_condition = boundary_conditions['children'][args['mesh']+cpnts]
            boundary_condition['children']['type'] = self.populateTree('type',
                    text=args['type'], children={})
            boundary_condition['children']['mesh'] = self.populateTree(
                        'mesh', text=args['mesh'], children={})
            if "parameter" in args:
                if "component" in args:
                    boundary_condition['children']['component'] = self.populateTree(
                            'component', text=args['component'], children={})
                boundary_condition['children']['parameter'] = self.populateTree(
                        'parameter', text=args['parameter'], children={})
            elif "bc_object" in args:
                if "component" in args:
                    boundary_condition['children']['component'] = self.populateTree(
                            'component', text=args['component'], children={})
                boundary_condition['children']['bc_object'] = self.populateTree(
                        'bc_object', text=args['bc_object'], children={})
            else:
                raise KeyError("Please provide the parameter for Dirichlet \
                                    or Neumann BC/bc_object for Python BC")
        else:
            raise KeyError("You should provide either a geometrical set \
                                or a mesh to define BC for.")
    def addST(self, **args):
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
                'source_terms'] = self.populateTree('source_terms', children={})
        source_terms = self.tree['process_variables']['children'][args['process_variable_name']][
                'children']['source_terms']
        if "geometrical_set" in args:
            if "geometry" in args:
                source_terms['children'][args['geometrical_set'] +
                        args['geometry']] = self.populateTree('source_term', children={})
                source_term = source_terms['children'][args['geometrical_set'] + args['geometry']]
                source_term['children']['type'] = self.populateTree('type', text=args['type'],
                        children={})
                source_term['children']['geometrical_set'] = self.populateTree(
                        'geometrical_set', text=args['geometrical_set'], children={})
                source_term['children']['geometry'] = self.populateTree(
                                'geometry', text=args['geometry'], children={})
                if "parameter" in args:
                    if "component" in args:
                        source_term['children']['component'] = self.populateTree(
                                'component', text=args['component'], children={})
                    source_term['children']['parameter'] = self.populateTree(
                            'parameter', text=args['parameter'], children={})
                elif "source_term_object" in args:
                    if "component" in args:
                        source_term['children']['component'] = self.populateTree(
                                'component', text=args['component'], children={})
                    source_term['children']['source_term_object'] = self.populateTree(
                            'source_term_object', text=args['source_term_object'], children={})
                else:
                    raise KeyError("Please provide the parameter for Dirichlet \
                                        or Neumann BC/bc_object for Python BC")
            else:
                raise KeyError("You need to provide a geometry.")
        elif "mesh" in args:
            source_terms['children'][args['mesh']] = self.populateTree(
                    'source_term', children={})
            source_term = source_terms['children'][args['mesh']]
            source_term['children']['type'] = self.populateTree(
                        'type', text=args['type'], children={})
            source_term['children']['mesh'] = self.populateTree(
                        'mesh', text=args['mesh'], children={})
            if "parameter" in args:
                if "component" in args:
                    source_term['children']['component'] = self.populateTree(
                            'component', text=args['component'], children={})
                source_term['children']['parameter'] = self.populateTree(
                                    'parameter', text=args['parameter'], children={})
            elif "source_term_object" in args:
                if "component" in args:
                    source_term['children']['component'] = self.populateTree(
                                    'component', text=args['component'], children={})
                source_term['children']['source_term_object'] = self.populateTree(
                            'source_term_object', text=args['source_term_object'], children={})
            else:
                raise KeyError("Please provide the parameter for the source term\
                            /source term_object for Python BC")
        else:
            raise KeyError("You should provide either a geometrical set \
                        or a mesh to define the source terms for.")
