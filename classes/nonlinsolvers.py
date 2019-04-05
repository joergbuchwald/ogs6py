import numpy as np
class NONLINSOLVERS(object):
	def __init__(self,**args):
		self.nonlin_solvers=np.array([['name','type','max_iter','linear_solver','damping']])
	def addNonlinear_solver(self,**args):
		if "name" in args:
			if "type" in args:
				if "max_iter" in args:
					if "linear_solver" in args:
						if "damping" in args:
							self.nonlin_solvers=np.append(self.nonlin_solvers,[[args['name'], args['type'],args['max_iter'],args['linear_solver'],args['damping']]],axis=0)
						else:
							self.nonlin_solvers=np.append(self.nonlin_solvers,[[args['name'], args['type'],args['max_iter'],args['linear_solver'],'']],axis=0)

