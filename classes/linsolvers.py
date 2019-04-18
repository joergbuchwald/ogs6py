import numpy as np
class LINSOLVERS(object):
    def __init__(self,**args):
        self.lin_solver_name=""
        self.lin_solvers=np.array([['kind','type','preconditioner','max_iter','tol','scaling']])
    def addLinSolver(self,**args):
        if "name" in args:
            self.lin_solver_name=args['name']
        else:
            raise KeyError("You need to provide a name for the linear solver.")
        if "kind" in args:
            if "solver_type" in args:
                if "precon_type" in args:
                    if "max_iteration_step" in args:
                        if "error_tolerance" in args:
                            if "scaling" in args:
                                self.lin_solvers=np.append(self.lin_solvers,[[args['kind'], args['solver_type'], args['precon_type'], args['max_iteration_step'], args['error_tolerance'],args['scaling']]],axis=0)
                            else:
                                self.lin_solvers=np.append(self.lin_solvers,[[args['kind'], args['solver_type'], args['precon_type'], args['max_iteration_step'], args['error_tolerance'],"0"]],axis=0)
                        else:
                            raise KeyError("No error_tolerance given.")
                    else:
                        raise KeyError("No max_iteration_step given.")
                else:
                    raise KeyError("No precon_type given.")
            else:
                raise KeyError("No solver_type given.")
        else:
            raise KeyError("No kind given. Please specify the linear solver library (e.g.: eigen, petsc, lis).")

