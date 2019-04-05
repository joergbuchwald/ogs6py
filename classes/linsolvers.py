import numpy as np
class LINSOLVERS(object):
	def __init__(self,**args):
		self.lin_solver_name=""
		self.lin_solvers=np.array([['kind','type','preconditioner','max_iter','tol']])
	def addLinear_solver(self,**args):
		if "name" in args:
			self.lin_solver_name=args['name']
		if "kind" in args:
			if "solver_type" in args:
				if "precon_type" in args:
					if "max_iteration_step" in args:
						if "error_tolerance" in args:
							self.lin_solvers=np.append(self.lin_solvers,[[args['kind'], args['solver_type'], args['precon_type'], args['max_iteration_step'], args['error_tolerance']]],axis=0)
