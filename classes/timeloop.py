class TIMELOOP(object):
	def __init__(self,**args):
		self.nonlinear_solver="basic_newton"
		self.time_discretization="BackwardEuler"
		self.time_stepping="SingleStep"
		self.t_initial="0"
		self.t_end="1"
		self.t_repeat="5"
		self.t_deltat="0.1"
		self.convergence_type="DeltaX"
		self.norm_type="NORM2"
		self.abstol=""
		self.reltol=""
		self.outputtype=""
		self.outputprefix=""
		self.outputvariables=[]
	def addProcess(self,**args):
		if "nonlinear_solver_name" in args:
			self.nonlinear_solver=args["nonlinear_solver_name"]
			if "convergence_type" in args:
				if args["convergence_type"]=="DeltaX":
					if "norm_type" in args:
						self.convergencetype=args["convergence_type"]
						self.norm_type=args["norm_type"]
						if "abstol" in args:
							self.abstol=args["abstol"]	
						if "reltol" in args:
							self.reltol=args["reltol"]
				if args["convergence_type"]=="PerComponenDeltaX":
					if "norm_type" in args:
						self.convergencetype=args["convergence_type"]
						self.norm_type=args["norm_type"]
						if "abstols" in args:
							self.abstol=args["abstols"]
						if "reltols" in args:
							self.reltol=args["reltols"]
				if args["convergence_type"]=="PercpomponentResidual":
					pass
				if args["convergence_type"]=="Residual":
					pass
			if "time_discretization" in args:
				self.time_discretization=args["time_discretization"]
	def setStepping(self,**args):
		if "type" in args:
			if args["type"]=="FixedTimeStepping":
				self.time_stepping="FixedTimeStepping"
				self.t_initial=args["t_initial"]
				self.t_end=args["t_end"]
				if "repeat" in args and "delta_t" in args:
					self.t_repeat=args["repeat"]
					self.t_deltat=args["delta_t"]
			if args["type"]=="SingleStep":
				self.timestepping="SingleStep"
	def addOutput(self,**args):
		if "type" in args:
			if "prefix" in args:
				if "variables" in args:
					self.outputtype=args["type"]
					self.outputprefix=args["prefix"]
					self.outputvariables=args["variables"]


