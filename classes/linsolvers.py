from classes import build_tree

class LINSOLVERS(build_tree.BUILD_TREE):
    def __init__(self, **args):
        self.tree = {
            'linear_solvers': {
                'tag': 'linear_solvers',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def addLinSolver(self, **args):
        self._convertargs(args)
        if not "name" in args:
            raise KeyError("You need to provide a name for the linear solver.")
        else:
            if not args['name'] in self.tree['linear_solvers']['children']:
                self.tree['linear_solvers']['children'][
                    args['name']] = self.populateTree('linear_solver',
                                                      children={})
            linear_solver = self.tree['linear_solvers']['children'][
                args['name']]['children']
            if not 'name' in linear_solver:
                linear_solver['name'] = self.populateTree('name',
                                                          text=args['name'],
                                                          children={})
            if not "kind" in args:
                raise KeyError("No kind given. Please specify the linear \
                            solver library (e.g.: eigen, petsc, lis).")
            else:
                if not "solver_type" in args:
                    raise KeyError("No solver_type given.")
                else:
                    if not "precon_type" in args:
                        raise KeyError("No precon_type given.")
                    else:
                        if not "max_iteration_step" in args:
                            raise KeyError("No max_iteration_step given.")
                        else:
                            if not "error_tolerance" in args:
                                raise KeyError("No error_tolerance given.")
                            else:
                                if args['kind'] == "eigen":
                                    linear_solver['eigen'] = self.populateTree(
                                        'eigen', children={})
                                    linear_solver['eigen']['children'][
                                        'solver_type'] = self.populateTree(
                                            'solver_type',
                                            text=args['solver_type'],
                                            children={})
                                    linear_solver['eigen']['children'][
                                        'precon_type'] = self.populateTree(
                                            'precon_type',
                                            text=args['precon_type'],
                                            children={})
                                    linear_solver['eigen']['children'][
                                        'max_iteration_step'] = self.populateTree(
                                            'max_iteration_step',
                                            text=args['max_iteration_step'],
                                            children={})
                                    linear_solver['eigen']['children'][
                                        'error_tolerance'] = self.populateTree(
                                            'error_tolerance',
                                            text=args['error_tolerance'],
                                            children={})
                                    if "scaling" in args:
                                        linear_solver['eigen']['children'][
                                            'scaling'] = self.populateTree(
                                                'scaling',
                                                text=args['scaling'],
                                                children={})
                                elif args['kind'] == "lis":
                                    string = ('-i ' + args['solver_type']
                                            + ' -p ' + args['precon_type']
                                            + ' -tol ' + args['error_tolerance']
                                            + ' -maxiter ' + args['max_iteration_step'])
                                    linear_solver['lis'] = self.populateTree(
                                        'lis', text=string, children={})

                                elif args['kind'] == "petsc":
                                    prefix = 'sd'
                                    linear_solver['petsc'] = self.populateTree(
                                        'petsc', children={})
                                    linear_solver['petsc']['children'][
                                        'prefix'] = self.populateTree(
                                            'prefix', text=prefix, children={})
                                    string = ('-' + prefix + '_ksp_type '
                                            + args['solver_type'] + ' -' + prefix
                                            + '_pc_type ' + args['precon_type']
                                            + ' -' + prefix + '_ksp_rtol '
                                            + args['error_tolerance']
                                            + ' -' + prefix + '_ksp_max_it '
                                            + args['max_iteration_step'])
                                    linear_solver['petsc']['children'][
                                        'parameters'] = self.populateTree(
                                            'parameters',
                                            text=string,
                                            children={})

