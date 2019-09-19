import numpy as np


class PROCESSVARS(object):
    def __init__(self, **args):
        self.initial_conditions = np.array(
            [['variable_name', 'components', 'order', 'initial_condition']])
        self.boundary_conditions = np.array([[
            'variable_name', 'geometrical_set', 'geometry', 'mesh', 'type',
            'component', 'parameter', 'bc_object'
        ]])
        self.source_terms = np.array([[
            'variable_name', 'geometrical_set', 'geometry', 'mesh', 'type',
            'component', 'parameter', 'source_term_object'
        ]])

    def setIC(self, **args):
        if "process_variable_name" in args:
            if "components" in args:
                if "order" in args:
                    if "initial_condition" in args:
                        self.initial_conditions = np.append(
                            self.initial_conditions, [[
                                args['process_variable_name'],
                                args['components'], args['order'],
                                args['initial_condition']
                            ]],
                            axis=0)
                    else:
                        raise KeyError("No initial_condition specified.")
                else:
                    raise KeyError(
                        "Out of order. Please specify the polynomial order \
                                of the process variable's shape functions.")
            else:
                raise KeyError("Please provide the number of components \
                            of the given process variable.")
        else:
            raise KeyError("No process_variable_name given")

    def addBC(self, **args):
        if "process_variable_name" in args:
            if "type" in args:
                if "geometrical_set" in args:
                    if "geometry" in args:
                        if "parameter" in args:
                            if "component" in args:
                                self.boundary_conditions = np.append(
                                    self.boundary_conditions, [[
                                        args['process_variable_name'],
                                        args['geometrical_set'],
                                        args['geometry'], '', args['type'],
                                        args['component'], args['parameter'],
                                        ''
                                    ]],
                                    axis=0)
                            else:
                                self.boundary_conditions = np.append(
                                    self.boundary_conditions, [[
                                        args['process_variable_name'],
                                        args['geometrical_set'],
                                        args['geometry'], '', args['type'], '',
                                        args['parameter'], ''
                                    ]],
                                    axis=0)
                        elif "bc_object" in args:
                            if "component" in args:
                                self.boundary_conditions = np.append(
                                    self.boundary_conditions, [[
                                        args['process_variable_name'],
                                        args['geometrical_set'],
                                        args['geometry'], '', args['type'],
                                        args['component'], '',
                                        args['bc_object']
                                    ]],
                                    axis=0)
                            else:
                                self.boundary_conditions = np.append(
                                    self.boundary_conditions, [[
                                        args['process_variable_name'],
                                        args['geometrical_set'],
                                        args['geometry'], '', args['type'], '',
                                        '', args['bc_object']
                                    ]],
                                    axis=0)
                        else:
                            raise KeyError(
                                "Please provide the parameter for Dirichlet \
                                        or Neumann BC/bc_object for Python BC")
                    else:
                        raise KeyError("You need to provide a geometry.")
                elif "mesh" in args:
                    if "parameter" in args:
                        if "component" in args:
                            self.boundary_conditions = np.append(
                                self.boundary_conditions, [[
                                    args['process_variable_name'], '', '',
                                    args['mesh'], args['type'],
                                    args['component'], args['parameter'], ''
                                ]],
                                axis=0)
                        else:
                            self.boundary_conditions = np.append(
                                self.boundary_conditions, [[
                                    args['process_variable_name'], '', '',
                                    args['mesh'], args['type'], '',
                                    args['parameter'], ''
                                ]],
                                axis=0)
                    elif "bc_object" in args:
                        if "component" in args:
                            self.boundary_conditions = np.append(
                                self.boundary_conditions, [[
                                    args['process_variable_name'], '', '',
                                    args['mesh'], args['type'],
                                    args['component'], '', args['bc_object']
                                ]],
                                axis=0)
                        else:
                            self.boundary_conditions = np.append(
                                self.boundary_conditions, [[
                                    args['process_variable_name'], '', '',
                                    args['mesh'], args['type'], '', '',
                                    args['bc_object']
                                ]],
                                axis=0)
                    else:
                        raise KeyError(
                            "Please provide the parameter for Dirichlet \
                                    or Neumann BC/bc_object for Python BC")
                else:
                    raise KeyError(
                        "You should provide either a geometrical set \
                                or a mesh to define BC for.")
            else:
                raise KeyError("No type given.")
        else:
            raise KeyError("No process variable name specified.")

    def addST(self, **args):
        if "process_variable_name" in args:
            if "type" in args:
                if "geometrical_set" in args:
                    if "geometry" in args:
                        if "parameter" in args:
                            if "component" in args:
                                self.source_terms = np.append(
                                    self.source_terms, [[
                                        args['process_variable_name'],
                                        args['geometrical_set'],
                                        args['geometry'], '', args['type'],
                                        args['component'], args['parameter'],
                                        ''
                                    ]],
                                    axis=0)
                            else:
                                self.source_terms = np.append(
                                    self.source_terms, [[
                                        args['process_variable_name'],
                                        args['geometrical_set'],
                                        args['geometry'], '', args['type'], '',
                                        args['parameter'], ''
                                    ]],
                                    axis=0)
                        elif "source_term_object" in args:
                            if "component" in args:
                                self.source_terms = np.append(
                                    self.source_terms, [[
                                        args['process_variable_name'],
                                        args['geometrical_set'],
                                        args['geometry'], '', args['type'],
                                        args['component'], '',
                                        args['source_term_object']
                                    ]],
                                    axis=0)
                            else:
                                self.source_terms = np.append(
                                    self.source_terms, [[
                                        args['process_variable_name'],
                                        args['geometrical_set'],
                                        args['geometry'], '', args['type'], '',
                                        '', args['source_term_object']
                                    ]],
                                    axis=0)
                        else:
                            raise KeyError("Please provide the parameter for \
                                        Nodal/Volumetric STs/\
                                        source_term_object for Python STs")
                    else:
                        raise KeyError("You need to provide a geometry.")
                elif "mesh" in args:
                    if "parameter" in args:
                        if "component" in args:
                            self.source_terms = np.append(self.source_terms, [[
                                args['process_variable_name'], '', '',
                                args['mesh'], args['type'], args['component'],
                                args['parameter'], ''
                            ]],
                                                          axis=0)
                        else:
                            self.source_terms = np.append(self.source_terms, [[
                                args['process_variable_name'], '', '',
                                args['mesh'], args['type'], '',
                                args['parameter'], ''
                            ]],
                                                          axis=0)
                    elif "source_term_object" in args:
                        if "component" in args:
                            self.source_terms = np.append(self.source_terms, [[
                                args['process_variable_name'], '', '',
                                args['mesh'], args['type'], args['component'],
                                '', args['source_term_object']
                            ]],
                                                          axis=0)
                        else:
                            self.source_terms = np.append(self.source_terms, [[
                                args['process_variable_name'], '', '',
                                args['mesh'], args['type'], '', '',
                                args['source_term_object']
                            ]],
                                                          axis=0)
                    else:
                        raise KeyError("Please provide the parameter for \
                                    Nodal/Volumetric STs/\
                                    source_term_object for Python STs")
                else:
                    raise KeyError("You should provide either a geometrical \
                                set or a mesh to define BC for.")
            else:
                raise KeyError("No type given.")
        else:
            raise KeyError("No process variable name specified.")
