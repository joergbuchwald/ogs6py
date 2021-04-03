class TIMELOOP(object):
    def __init__(self, **args):
        self.process = {}
        self.baum = {
            'time_loop': {
                'tag': 'time_loop',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.outputtype = ""
        self.outputprefix = ""
        self.outputvariables = []
        self.output_repeat = []
        self.output_each_steps = []

    def _convertargs(self, args):
        for item, value in args.items():
            if not type(value) is list:
                args[item] = str(value)

    def populateTree(self, tag, text='', attr={}, children={}):
        return {'tag': tag, 'text': text, 'attr': attr, 'children': children}

    @property
    def tree(self):
        self.baum['time_loop']['children']['processes2'] = self.populateTree(
            'processes')
        process = self.baum['time_loop']['children']['processes2']['children']
        self.baum['time_loop']['children']['output'] = self.populateTree(
            'output', children={})
        output = self.baum['time_loop']['children']['output']['children']
        def popConvCrit():
            conv_crit_ = {}
            for entry, value in self.process[processname]["conv_crit"].items():
                conv_crit_[entry] = self.populateTree(entry, text=value, children={})
            return conv_crit_
        def popTimeStepping():
            ts = {}
            for entry, value in self.process[processname]['time_stepping'].items():
                if not ((entry == "t_repeat") or (entry == "t_deltat")):
                    ts[entry] = self.populateTree(entry, text=value, children={})
            return ts

        for processname in self.process:
            process[processname] = self.populateTree('process', attr={'ref': processname}, children={})
            process[processname]['children']['nonlinear_solver'] = self.populateTree(
                    'nonlinear_solver', text=self.process[processname]['nonlinear_solver'], children={})

            process[processname]['children']['convergence_criterion'] = self.populateTree('convergence_criterion', children={})
            conv_crit = process[processname]['children']['convergence_criterion']
            conv_crit['children'] = popConvCrit()

            process[processname]['children']['time_discretization'] = self.populateTree('time_discretization', children={})
            time_discr = process[processname]['children']['time_discretization']['children']
            time_discr['type'] = self.populateTree('type',text=self.process[processname]['time_discretization'],
                children={})

            process[processname]['children']['time_stepping'] = self.populateTree('time_stepping', children={})
            time_stepping = process[processname]['children']['time_stepping']
            time_stepping["children"] = popTimeStepping()

            if 't_repeat' in self.process[processname]['time_stepping']:
                time_stepping["children"]['timesteps'] = self.populateTree('timesteps',
                                                           children={})
                time_pair = time_stepping["children"]['timesteps']['children']
                for i, repeat in enumerate(self.process[processname]["time_stepping"]['t_repeat']):
                    time_pair['pair' + str(i)] = self.populateTree('pair', children={})
                    time_pair['pair' + str(i)]['children']['repeat'] = self.populateTree(
                              'repeat', text=repeat, children={})
                    time_pair['pair' + str(i)]['children']['delta_t'] = self.populateTree(
                              'delta_t',
                              text=self.process[processname]["time_stepping"]['t_deltat'][i], children={})
        output['type'] = self.populateTree('type',
                                           text=self.outputtype,
                                           children={})
        output['prefix'] = self.populateTree('prefix',
                                             text=self.outputprefix,
                                             children={})
        output['timesteps'] = self.populateTree('timesteps', children={})
        output_pair = output['timesteps']['children']
        for i, repeat in enumerate(self.output_repeat):
            output_pair['pair' + str(i)] = self.populateTree('pair',
                                                             children={})
            output_pair['pair' +
                        str(i)]['children']['repeat'] = self.populateTree(
                            'repeat', text=repeat, children={})
            output_pair['pair' +
                        str(i)]['children']['each_steps'] = self.populateTree(
                            'each_steps',
                            text=self.output_each_steps[i],
                            children={})
        output['variables'] = self.populateTree('variables', children={})
        for i, variable in enumerate(self.outputvariables):
            output['variables']['children']['variable' +
                                            str(i)] = self.populateTree(
                                                'variable',
                                                text=variable,
                                                children={})
        return self.baum

    def addProcess(self, **args):
        def readConvCrit():
            self.process[args['process']]["conv_crit"] = {}
            if args["convergence_type"] == "DeltaX":
                if not "norm_type" in args:
                    raise KeyError("No norm_type given.")
                else:
                    self.process[args['process']]["conv_crit"]['type'] = args["convergence_type"]
                    self.process[args['process']]["conv_crit"]['norm_type'] = args["norm_type"]
                    if "abstol" in args:
                        self.process[args['process']]["conv_crit"]['abstol'] = args["abstol"]
                    if "reltol" in args:
                        self.process[
                                args['process']]["conv_crit"]['reltol'] = args["reltol"]
            elif args["convergence_type"] == "PerComponentDeltaX":
                if "norm_type" in args:
                    self.process[args['process']]["conv_crit"]['type'] = args["convergence_type"]
                    self.process[
                            args['process']]["conv_crit"]['norm_type'] = args["norm_type"]
                    if "abstols" in args:
                        self.process[
                                args['process']]["conv_crit"]['abstols'] = args["abstols"]
                    if "reltols" in args:
                        self.process[
                                args['process']]["conv_crit"]['reltols'] = args["reltols"]
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

        self._convertargs(args)
        if "process" in args:
            self.process = {args["process"]: {}}
        else:
            raise KeyError("No process referenced")
        if not "nonlinear_solver_name" in args:
            raise KeyError("Please specify a name (nonlinear_solver_name) \
                        for the nonlinear solver.")
        else:
            self.process[args['process']]['nonlinear_solver'] = args[
                'nonlinear_solver_name']
            if not "convergence_type" in args:
                raise KeyError("No convergence criterion given. \
                            Specify convergence_type.")
            else:
                readConvCrit()
            if "time_discretization" in args:
                self.process[args['process']]['time_discretization'] = args[
                    "time_discretization"]
            else:
                raise KeyError("No time_discretization specified.")

    def setStepping(self, **args):
        self._convertargs(args)
        if not "process" in args:
            raise KeyError("Process reference missing")
        if not "type" in args:
            raise KeyError("No type given.")
        else:
            self.process[args['process']]['time_stepping'] = {}
            if args["type"] == "FixedTimeStepping":
                self.process[args['process']]['time_stepping']["type"] = "FixedTimeStepping"
                self.process[args['process']]['time_stepping']['t_initial'] = args["t_initial"]
                self.process[args['process']]['time_stepping']['t_end'] = args["t_end"]
                self.process[args['process']]['time_stepping']['t_repeat'] = []
                self.process[args['process']]['time_stepping']['t_deltat'] = []
                if "repeat" in args and "delta_t" in args:
                    self.process[args['process']]['time_stepping']['t_repeat'].append(args["repeat"])
                    self.process[args['process']]['time_stepping']['t_deltat'].append(args["delta_t"])
                else:
                    raise KeyError("No proper time stepping defined. \
                                Please specify repeat and delta_t.")
            elif args["type"] == "SingleStep":
                self.process[args['process']]['time_stepping']["type"] = "SingleStep"
            elif args["type"] == "IterationNumberBasedTimeStepping":
                self.process[args['process']]['time_stepping']["type"] = "IterationNumberBasedTimeStepping"
                self.process[args['process']]['time_stepping']['t_initial'] = args["t_initial"]
                self.process[args['process']]['time_stepping']['t_end'] = args["t_end"]
                self.process[args['process']]['time_stepping']['initial_dt'] = args["initial_dt"]
                self.process[args['process']]['time_stepping']['minimum_dt'] = args["minimum_dt"]
                self.process[args['process']]['time_stepping']['maximum_dt'] = args["maximum_dt"]
                numit_list = args["number_iterations"]
                multi_list = args["multiplier"]
                self.process[args['process']]['time_stepping']['number_iterations'] = " ".join(map(str, numit_list))
                self.process[args['process']]['time_stepping']['multiplier'] = " ".join(map(str, multi_list))
            elif args["type"] == "EvolutionaryPIDcontroller":
                self.process[
                    args['process']]['time_stepping']["type"] = "EvolutionaryPIDcontroller"
                self.process[args['process']]['time_stepping']['t_initial'] = args["t_initial"]
                self.process[args['process']]['time_stepping']['t_end'] = args["t_end"]
                self.process[args['process']]['time_stepping']['dt_guess'] = args["dt_guess"]
                self.process[args['process']]['time_stepping']['dt_min'] = args["dt_min"]
                self.process[args['process']]['time_stepping']['dt_max'] = args["dt_max"]
                self.process[args['process']]['time_stepping']['rel_dt_max'] = args["rel_dt_max"]
                self.process[args['process']]['time_stepping']['rel_dt_min'] = args["rel_dt_min"]
                self.process[args['process']]['time_stepping']['tol'] = args["tol"]

            else:
                raise KeyError("Specified time stepping scheme not valid.")

    def addOutput(self, **args):
        if not "type" in args:
            raise KeyError("If you want to specify an output method, \
                        you need to provide type, \
                        prefix and a list of variables.")
        else:
            if not "prefix" in args:
                raise KeyError("No prefix given.")
            else:
                if not "variables" in args:
                    raise KeyError(
                        "Please provide a list with output variables.")
                else:
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

    def addTimeSteppingPair(self, **args):
        self._convertargs(args)
        if "process" in args:
            pass
        else:
            raise KeyError("No process referenced")
        if "repeat" in args and "delta_t" in args:
            self.process[args['process']]['time_stepping']['t_repeat'].append(args["repeat"])
            self.process[args['process']]['time_stepping']['t_deltat'].append(args["delta_t"])
        else:
            raise KeyError("You muss provide repeat and delta_t attributes to \
                        define additional time stepping pairs.")

    def addOutputPair(self, **args):
        self._convertargs(args)
        if "repeat" in args and "each_steps" in args:
            self.output_repeat.append(args["repeat"])
            self.output_each_steps.append(args["each_steps"])
        else:
            raise KeyError("You muss provide repeat and each_steps attributes \
                        to define additional output pairs.")
