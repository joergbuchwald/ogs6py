class PROCESSVARS(object):
    def __init__(self, **args):
        self.tree = { 'process_variables': { 'tag': 'process_variables', 'text': '', 'attr': {}, 'children': {} } }
    def populateTree(self, tag, text='', attr={}, children={}):
        return { 'tag': tag, 'text': text, 'attr': attr, 'children': children }
    def setIC(self, **args):
        if "process_variable_name" in args:
            if "components" in args:
                if "order" in args:
                    if "initial_condition" in args:
                        self.tree['process_variables']['children'][args['process_variable_name']] = self.populateTree('process_variable', children={})
                        processvar=self.tree['process_variables']['children'][args['process_variable_name']]
                        processvar['children']['name'] =  self.populateTree('name', text=args['process_variable_name'], children={})
                        processvar['children']['components'] = self.populateTree('components', text=args['components'], children={})
                        processvar['children']['order'] = self.populateTree('order', text=args['order'], children={})
                        processvar['children']['initial_condition'] = self.populateTree('initial_condition', text=args['initial_condition'], children={})
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
                if args['process_variable_name'] in self.tree['process_variables']['children']:
                    self.tree['process_variables']['children'][args['process_variable_name']]['children']['boundary_conditions'] = self.populateTree('boundary_conditions', children={})
                    boundary_conditions = self.tree['process_variables']['children'][args['process_variable_name']]['children']['boundary_conditions']
                else:
                    raise KeyError("You need to set initial condition for that process variable first.")
                if "geometrical_set" in args:
                    if "geometry" in args:
                        boundary_conditions['children'][args['geometrical_set']+args['geometry']] = self.populateTree('boundary_condition', children={})
                        boundary_condition = boundary_conditions['children'][args['geometrical_set']+args['geometry']]
                        boundary_condition['children']['type'] = self.populateTree('type', text=args['type'], children={})
                        boundary_condition['children']['geometrical_set'] = self.populateTree('geometrical_set', text=args['geometrical_set'], children={})
                        boundary_condition['children']['geometry'] =  self.populateTree('geometry', text=args['geometry'], children={})
                        if "parameter" in args:
                            if "component" in args:
                                boundary_condition['children']['component'] = self.populateTree('component', text=args['component'], children={})
                            boundary_condition['children']['parameter'] = self.populateTree('parameter', text=args['parameter'], children={})
                        elif "bc_object" in args:
                            if "component" in args:
                                boundary_condition['children']['component'] = self.populateTree('component', text=args['component'], children={})
                            boundary_condition['children']['bc_object'] = self.populateTree('bc_object', text=args['bc_object'], children={})
                        else:
                            raise KeyError(
                                "Please provide the parameter for Dirichlet \
                                        or Neumann BC/bc_object for Python BC")
                    else:
                        raise KeyError("You need to provide a geometry.")
                elif "mesh" in args:
                    boundary_conditions['children'][args['mesh']] = self.populateTree('boundary_condition', children={})
                    boundary_condition = boundary_conditions['children'][args['mesh']]
                    boundary_condition['children']['type'] = self.populateTree('type', text=args['type'], children={})
                    boundary_condition['children']['mesh'] = self.populateTree('mesh', text=args['mesh'], children={})
                    if "parameter" in args:
                        if "component" in args:
                            boundary_condition['children']['component'] = self.populateTree('component', text=args['component'], children={})
                        boundary_condition['children']['parameter'] = self.populateTree('parameter', text=args['parameter'], children={})
                    elif "bc_object" in args:
                        if "component" in args:
                            boundary_condition['children']['component'] = self.populateTree('component', text=args['component'], children={})
                        boundary_condition['children']['bc_object'] = self.populateTree('bc_object', text=args['bc_object'], children={})
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
                if args['process_variable_name'] in self.tree['process_variables']['children']:
                    self.tree['process_variables']['children'][args['process_variable_name']]['children']['source_terms'] = self.populateTree('source_terms', children={})
                    source_terms = self.tree['process_variables']['children'][args['process_variable_name']]['children']['source_terms']
                else:
                    raise KeyError("You need to set initial condition for that process variable first.")
                if "geometrical_set" in args:
                    if "geometry" in args:
                        source_terms['children'][args['geometrical_set']+args['geometry']] = self.populateTree('source_term', children={})
                        source_term = source_terms['children'][args['geometrical_set']+args['geometry']]
                        source_term['children']['type'] = self.populateTree('type', text=args['type'], children={})
                        source_term['children']['geometrical_set'] = self.populateTree('geometrical_set', text=args['geometrical_set'], children={})
                        source_term['children']['geometry'] =  self.populateTree('geometry', text=args['geometry'], children={})
                        if "parameter" in args:
                            if "component" in args:
                                source_term['children']['component'] = self.populateTree('component', text=args['component'], children={})
                            source_term['children']['parameter'] = self.populateTree('parameter', text=args['parameter'], children={})
                        elif "bc_object" in args:
                            if "component" in args:
                                source_term['children']['component'] = self.populateTree('component', text=args['component'], children={})
                            source_term['children']['source_term_object'] = self.populateTree('source_term_object', text=args['source_term_object'], children={})
                        else:
                            raise KeyError(
                                "Please provide the parameter for Dirichlet \
                                        or Neumann BC/bc_object for Python BC")
                    else:
                        raise KeyError("You need to provide a geometry.")
                elif "mesh" in args:
                    source_term['children'][args['mesh']] = self.populateTree('source_term', children={})
                    source_term = boundary_conditions['children'][args['mesh']]
                    source_term['children']['type'] = self.populateTree('type', text=args['type'], children={})
                    source_term['children']['mesh'] = self.populateTree('mesh', text=args['mesh'], children={})
                    if "parameter" in args:
                        if "component" in args:
                            source_term['children']['component'] = self.populateTree('component', text=args['component'], children={})
                        source_term['children']['parameter'] = self.populateTree('parameter', text=args['parameter'], children={})
                    elif "bc_object" in args:
                        if "component" in args:
                            source_term['children']['component'] = self.populateTree('component', text=args['component'], children={})
                        source_term['children']['source_term_object'] = self.populateTree('source_term_object', text=args['source_term_object'], children={})
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

