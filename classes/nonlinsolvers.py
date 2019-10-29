class NONLINSOLVERS(object):
    def __init__(self, **args):
        self.tree = {
            'nonlinear_solvers': {
                'tag': 'nonlinear_solvers',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def populateTree(self, tag, text='', attr={}, children={}):
        return {'tag': tag, 'text': text, 'attr': attr, 'children': children}

    def addNonlinSolver(self, **args):
        if "name" in args:
            if "type" in args:
                if "max_iter" in args:
                    if "linear_solver" in args:
                        self.tree['nonlinear_solvers']['children'][
                            args['name']] = self.populateTree(
                                'nonlinear_solver', children={})
                        nonlin_solver = self.tree['nonlinear_solvers'][
                            'children'][args['name']]['children']
                        nonlin_solver['name'] = self.populateTree(
                            'name', text=args['name'], children={})
                        nonlin_solver['type'] = self.populateTree(
                            'type', text=args['type'], children={})
                        nonlin_solver['max_iter'] = self.populateTree(
                            'max_iter', text=args['max_iter'], children={})
                        nonlin_solver['linear_solver'] = self.populateTree(
                            'linear_solver', text=args['linear_solver'], children={})
                        if "damping" in args:
                            nonlin_solver['damping'] = self.populateTree(
                                'damping', text=args['damping'], children={})
                    else:
                        raise KeyError("No linear_solver specified.")
                else:
                    raise KeyError("Please provide the maximum number \
                                of iterations (max_iter).")
            else:
                raise KeyError(
                    "Please specify the type of the nonlinear solver.")
        else:
            raise KeyError("Missing name of the nonlinear solver.")
