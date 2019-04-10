class TIMELOOP(object):
    def __init__(self,**args):
        self.nonlinear_solver=""
        self.time_discretization=""
        self.time_stepping=""
        self.t_initial=""
        self.t_end=""
        self.t_repeat=[]
        self.t_deltat=[]
        self.convergence_type=""
        self.norm_type=""
        self.abstol=""
        self.reltol=""
        self.outputtype=""
        self.outputprefix=""
        self.outputvariables=[]
        self.output_repeat=[]
        self.output_each_steps=[]
    def addProcess(self,**args):
        if "nonlinear_solver_name" in args:
            self.nonlinear_solver=args["nonlinear_solver_name"]
            if "convergence_type" in args:
                if args["convergence_type"]=="DeltaX":
                    print("CONVERGENCE_TYPE:",args["convergence_type"])
                    if "norm_type" in args:
                        self.convergence_type=args["convergence_type"]
                        self.norm_type=args["norm_type"]
                        if "abstol" in args:
                            self.abstol=args["abstol"]
                        if "reltol" in args:
                            self.reltol=args["reltol"]
                    else:
                        raise KeyError("No norm_type given.")
                elif args["convergence_type"]=="PerComponentDeltaX":
                    if "norm_type" in args:
                        self.convergence_type=args["convergence_type"]
                        self.norm_type=args["norm_type"]
                        if "abstols" in args:
                            self.abstol=args["abstols"]
                        if "reltols" in args:
                            self.reltol=args["reltols"]
                        if ("abstol" in args) or ("reltol" in args):
                            raise KeyError("Convergence type PerComponentDeltaX requires plural s for the tolerances.")
                    else:
                        raise KeyError("No norm_type given")
                elif args["convergence_type"]=="PercpomponentResidual":
                    pass
                elif args["convergence_type"]=="Residual":
                    pass
                else:
                    raise KeyError("Invalid convergence_type.")
            else:
                raise KeyError("No convergence criterion given. Specify convergence_type.")
            if "time_discretization" in args:
                self.time_discretization=args["time_discretization"]
            else:
                raise KeyError("No time_discretization specified.")
        else:
            raise KeyError("Please specify a name (nonlinear_solver_name) for the nonlinear solver.")
    def setStepping(self,**args):
        if "type" in args:
            if args["type"]=="FixedTimeStepping":
                self.time_stepping="FixedTimeStepping"
                self.t_initial=args["t_initial"]
                self.t_end=args["t_end"]
                if "repeat" in args and "delta_t" in args:
                    self.t_repeat.append(args["repeat"])
                    self.t_deltat.append(args["delta_t"])
                else:
                    raise KeyError("No proper time stepping defined. Please specify repeat and delta_t.")
            elif args["type"]=="SingleStep":
                self.timestepping="SingleStep"
            else:
                raise KeyError("Specified time stepping scheme not valid.")
        else:
            raise KeyError("No type given.")
    def addOutput(self,**args):
        if "type" in args:
            if "prefix" in args:
                if "variables" in args:
                    self.outputtype=args["type"]
                    self.outputprefix=args["prefix"]
                    self.outputvariables=args["variables"]
                    if "repeat" in args:
                        if "each_steps" in args:
                            self.output_repeat.append(args["repeat"])
                            self.output_each_steps.append(args["each_steps"])
                        else:
                            raise KeyError("each_steps is a required tag.")
                    else:
                        pass
                else:
                    raise KeyError("Please provide a list with output variables.")
            else:
                raise KeyError("No prefix given.") 
        else:        
            raise KeyError("If you want to specify an output method, you need to provide type, prefix and a list of variables.")
    def addTimeSteppingPair(self,**args):
        if "repeat" in args and "delta_t" in args:
            self.t_repeat.append(args["repeat"])
            self.t_deltat.append(args["delta_t"])
        else:
            raise KeyError("You muss provide repeat and delta_t attributes to define additional time stepping pairs.")
    def addOutputPair(self,**args):
        if "repeat" in args and "each_steps" in args:
            self.output_repeat.append(args["repeat"])
            self.output_each_steps.append(args["each_steps"])
        else:
            raise KeyError("You muss provide repeat and each_steps attributes to define additional output pairs.")

