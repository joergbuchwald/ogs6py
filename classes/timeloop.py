class TIMELOOP(object):
    def __init__(self, **args):
        self.process = { }
        self.outputtype = ""
        self.outputprefix = ""
        self.outputvariables = []
        self.output_repeat = []
        self.output_each_steps = []
    def populateTree(self, tag, text='', attr={}, children={}):
        return { 'tag': tag, 'text': text, 'attr': attr, 'children': children }
    @property
    def tree(self):
        baum = { 'time_loop': { 'tag': 'time_loop', 'text': '', 'attr': {}, 'children': {} } }
        baum['time_loop']['children']['processes'] = { 'processes': { 'tag': 'processes', 'text': '', 'attr': {}, 'children': {} } }
        process = baum['time_loop']['children']['processes']['children']
        baum['time_loop']['children']['output'] = { 'processes': { 'tag': 'processes', 'text': '', 'attr': {}, 'children': {} } }
        output = baum['time_loop']['children']['output']['children']
        for processname in self.process:
            process[processname] = populateTree( 'process', attr= { 'ref': processname })
            process[processname]['children']['nonlinear_solver'] =  populateTree( 'nonlinear_solver', text=self.process[processname]['nonlinear_solver'])
            process[processname]['children']['convergence_criterion']= populateTree( 'convergence_criterion')
            conv_crit = process[processname]['children']['convergence_criterion']['children']
            conv_crit['type'] = populateTree( 'type', text=self.process[processname]['convergence_type'])
            conv_crit['norm_type'] = populateTree( 'type', text=self.process[processname]['norm_type'])
            if 'abstol' in self.process[processname]:
                conv_crit['abstol']= populateTree( 'abstol', text=self.process[processname]['abstol'])
            elif 'abstols' in self.process[processname]:
                conv_crit['abstols']= populateTree( 'abstols', text=self.process[processname]['abstols'])
            elif 'reltol' in self.process[processname]:
                conv_crit['reltol']= populateTree( 'reltol', text=self.process[processname]['reltol'])
            elif 'reltol' in self.process[processname]:
                conv_crit['reltols']= populateTree( 'reltols', text=self.process[processname]['reltols'])
            process[processname]['children']['time_discretization']= populateTree( 'time_discretization')
            time_discr = process[processname]['children']['time_discretization']['children']
            time_discr['type'] = populateTree( 'type', text=self.process[processname]['time_discretization'])
            process[processname]['children']['time_stepping']= populateTree( 'time_stepping')
            time_stepping = process[processname]['children']['time_stepping']['children']

        return baum
    def addProcess(self, **args):
        if "process" in args:
            self.process = { args["process"] : {} }
            self.process['process']['t_repeat'] = []
            self.process['process']['delat_t'] = []
        else:
            raise KeyError("No process referenced")
        if "nonlinear_solver_name" in args:
            self.process[args['process']]['nonlinear_solver'] = args['nonlinear_solver_name']
            if "convergence_type" in args:
                if args["convergence_type"] == "DeltaX":
                    # print("CONVERGENCE_TYPE:",args["convergence_type"])
                    if "norm_type" in args:
                        self.process[args['process']]['convergence_type'] = args["convergence_type"]
                        self.process[args['process']]['norm_type'] = args["norm_type"]
                        if "abstol" in args:
                            self.process[args['process']]['abstol'] = args["abstol"]
                        if "reltol" in args:
                            self.process[args['process']]['reltol'] = args["reltol"]
                    else:
                        raise KeyError("No norm_type given.")
                elif args["convergence_type"] == "PerComponentDeltaX":
                    if "norm_type" in args:
                        self.process[args['process']]['convergence_type'] = args["convergence_type"]
                        self.process[args['process']]['norm_type'] = args["norm_type"]
                        if "abstols" in args:
                            self.process[args['process']]['abstol'] = args["abstols"]
                        if "reltols" in args:
                            self.process[args['process']]['reltol'] = args["reltols"]
                        if ("abstol" in args) or ("reltol" in args):
                            raise KeyError("Convergence type \
                                    PerComponentDeltaX requires \
                                    plural s for the tolerances.")
                    else:
                        raise KeyError("No norm_type given")
                elif args["convergence_type"] == "PercpomponentResidual":
                    pass
                elif args["convergence_type"] == "Residual":
                    pass
                else:
                    raise KeyError("Invalid convergence_type.")
            else:
                raise KeyError("No convergence criterion given. \
                            Specify convergence_type.")
            if "time_discretization" in args:
                self.process[args['process']]['time_discretization'] = args["time_discretization"]
            else:
                raise KeyError("No time_discretization specified.")
        else:
            raise KeyError("Please specify a name (nonlinear_solver_name) \
                        for the nonlinear solver.")

    def setStepping(self, **args):
        if "process" in args:
            pass
        else:
            raise KeyError("Process reference missing")
        if "type" in args:
            if args["type"] == "FixedTimeStepping":
                self.process[args['process']]['time_stepping'] = "FixedTimeStepping"
                self.process[args['process']]['t_initial'] = args["t_initial"]
                self.process[args['process']]['t_end'] = args["t_end"]
                if "repeat" in args and "delta_t" in args:
                    self.process[args['process']]['t_repeat'].append(args["repeat"])
                    self.process[args['process']]['t_deltat'].append(args["delta_t"])
                else:
                    raise KeyError("No proper time stepping defined. \
                                Please specify repeat and delta_t.")
            elif args["type"] == "SingleStep":
                self.process[args['process']]['time_stepping'] = "SingleStep"
            else:
                raise KeyError("Specified time stepping scheme not valid.")
        else:
            raise KeyError("No type given.")

    def addOutput(self, **args):
        if "type" in args:
            if "prefix" in args:
                if "variables" in args:
                    self.outputtype = args["type"]
                    self.outputprefix = args["prefix"]
                    self.outputvariables = args["variables"]
                    if "repeat" in args:
                        if "each_steps" in args:
                            self.output_repeat.append(args["repeat"])
                            self.output_each_steps.append(args["each_steps"])
                        else:
                            raise KeyError("each_steps is a required tag.")
                    else:
                        pass
                else:
                    raise KeyError(
                        "Please provide a list with output variables.")
            else:
                raise KeyError("No prefix given.")
        else:
            raise KeyError("If you want to specify an output method, \
                        you need to provide type, \
                        prefix and a list of variables.")

    def addTimeSteppingPair(self, **args):
        if "process" in args:
            pass
        else:
            raise KeyError("No process referenced")
        if "repeat" in args and "delta_t" in args:
            self.process['process']['t_repeat'].append(args["repeat"])
            self.process['process']['t_deltat'].append(args["delta_t"])
        else:
            raise KeyError("You muss provide repeat and delta_t attributes to \
                        define additional time stepping pairs.")

    def addOutputPair(self, **args):
        if "repeat" in args and "each_steps" in args:
            self.output_repeat.append(args["repeat"])
            self.output_each_steps.append(args["each_steps"])
        else:
            raise KeyError("You muss provide repeat and each_steps attributes \
                        to define additional output pairs.")
