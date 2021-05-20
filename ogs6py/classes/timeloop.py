# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class TimeLoop(build_tree.BuildTree):
    """
    Class managing the time loop in the project file
    """
    def __init__(self):
        self.process = {}
        self.baum = {
            'time_loop': {
                'tag': 'time_loop',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.output = {}
        self.outputtype = ""
        self.outputprefix = ""
        self.outputvariables = []
        self.output_repeat = []
        self.output_each_steps = []

    @property
    def tree(self):
        self.baum['time_loop']['children']['processes2'] = self.populate_tree(
            'processes')
        process = self.baum['time_loop']['children']['processes2']['children']
        self.baum['time_loop']['children']['output'] = self.populate_tree(
            'output', children={})
        output = self.baum['time_loop']['children']['output']
        def pop_conv_crit(processname):
            conv_crit_ = {}
            for entry, value in self.process[processname]["conv_crit"].items():
                conv_crit_[entry] = self.populate_tree(entry, text=value, children={})
            return conv_crit_
        def pop_time_stepping(processname):
            ts = {}
            for entry, value in self.process[processname]['time_stepping'].items():
                if entry not in ('t_repeat', 't_deltat'):
                    ts[entry] = self.populate_tree(entry, text=value, children={})
            return ts
        def pop_output():
            output = {}
            for key, val in self.output.items():
                if isinstance(val, str):
                    output[key] = self.populate_tree(key, text=val, children={})
                else:
                    output['timesteps'] = self.populate_tree('timesteps', children={})
                    output_pair = output['timesteps']['children']
                    for i, repeat in enumerate(self.output["repeat"]):
                        output_pair['pair' + str(i)] = self.populate_tree('pair', children={})
                        output_pair['pair' + str(i)]['children']['repeat'] = self.populate_tree(
                                'repeat', text=repeat, children={})
                        output_pair['pair' + str(i)]['children']['each_steps'] = self.populate_tree(
                                'each_steps',text=self.output["each_steps"][i], children={})
                    output['variables'] = self.populate_tree('variables', children={})
                    for i, variable in enumerate(self.output["variables"]):
                        output['variables']['children']['variable'+str(i)] = self.populate_tree(
                                                'variable',text=variable, children={})
                    if 'meshes' in self.output:
                        output['meshes'] = self.populate_tree('meshes', children={})
                        for i, mesh in enumerate(self.output["meshes"]):
                            output['meshes']['children']['mesh'+str(i)] = self.populate_tree(
                                    'mesh',text= mesh, children={})
            return output

        for processname in self.process:
            process[processname] = self.populate_tree('process', attr={'ref': processname},
                    children={})
            process[processname]['children']['nonlinear_solver'] = self.populate_tree(
                    'nonlinear_solver', text=self.process[processname]['nonlinear_solver'],
                    children={})

            process[processname]['children']['convergence_criterion'] = self.populate_tree(
                    'convergence_criterion', children={})
            conv_crit = process[processname]['children']['convergence_criterion']
            conv_crit['children'] = pop_conv_crit(processname)

            process[processname]['children']['time_discretization'] = self.populate_tree(
                    'time_discretization', children={})
            time_discr = process[processname]['children']['time_discretization']['children']
            time_discr['type'] = self.populate_tree('type',text=self.process[processname][
                'time_discretization'], children={})

            process[processname]['children']['time_stepping'] = self.populate_tree('time_stepping',
                    children={})
            time_stepping = process[processname]['children']['time_stepping']
            time_stepping["children"] = pop_time_stepping(processname)

            if 't_repeat' in self.process[processname]['time_stepping']:
                time_stepping["children"]['timesteps'] = self.populate_tree('timesteps',
                                                           children={})
                time_pair = time_stepping["children"]['timesteps']['children']
                for i, repeat in enumerate(self.process[processname]["time_stepping"]['t_repeat']):
                    time_pair['pair' + str(i)] = self.populate_tree('pair', children={})
                    time_pair['pair' + str(i)]['children']['repeat'] = self.populate_tree(
                              'repeat', text=repeat, children={})
                    time_pair['pair' + str(i)]['children']['delta_t'] = self.populate_tree(
                              'delta_t',
                              text=self.process[processname]["time_stepping"]['t_deltat'][i],
                              children={})
        output['children'] = pop_output()
        return self.baum

    def add_process(self, **args):
        """
        Add a process section to timeloop

        Parameters
        ----------
        process : `str`
        convergence_type : `str`
        abstol : `str`
        abstols : `str`
        reltol : `str`
        reltols : `str`
        norm_type : `str`
        nonlinear_solver_name : `str`
        time_discretization : `str`
        """
        def read_conv_crit():
            self.process[args['process']]["conv_crit"] = {}
            if args["convergence_type"] == "DeltaX":
                if "norm_type" not in args:
                    raise KeyError("No norm_type given.")
                self.process[args['process']]["conv_crit"]['type'] = args["convergence_type"]
                self.process[args['process']]["conv_crit"]['norm_type'] = args["norm_type"]
                if "abstol" in args:
                    self.process[args['process']]["conv_crit"]['abstol'] = args["abstol"]
                if "reltol" in args:
                    self.process[args['process']]["conv_crit"]['reltol'] = args["reltol"]
            elif args["convergence_type"] == "PerComponentDeltaX":
                if "norm_type" not in args:
                    raise KeyError("No norm_type given")
                self.process[args['process']]["conv_crit"]['type'] = args["convergence_type"]
                self.process[args['process']]["conv_crit"]['norm_type'] = args["norm_type"]
                if "abstols" in args:
                    self.process[args['process']]["conv_crit"]['abstols'] = args["abstols"]
                if "reltols" in args:
                    self.process[args['process']]["conv_crit"]['reltols'] = args["reltols"]
                if ("abstol" in args) or ("reltol" in args):
                    raise KeyError("Convergence type \
                                    PerComponentDeltaX requires \
                                    plural s for the tolerances.")
            elif args["convergence_type"] == "PerComponentResidual":
                pass
            elif args["convergence_type"] == "Residual":
                pass
            else:
                raise KeyError("Invalid convergence_type.")

        self._convertargs(args)
        if "process" not in args:
            raise KeyError("No process referenced")
        self.process = {args["process"]: {}}
        if "nonlinear_solver_name" not in args:
            raise KeyError("Please specify a name (nonlinear_solver_name) \
                        for the nonlinear solver.")
        self.process[args['process']]['nonlinear_solver'] = args[
            'nonlinear_solver_name']
        if "convergence_type" not in args:
            raise KeyError("No convergence criterion given. \
                            Specify convergence_type.")
        read_conv_crit()
        if "time_discretization" not in args:
            raise KeyError("No time_discretization specified.")
        self.process[args['process']]['time_discretization'] = args["time_discretization"]

    def set_stepping(self, **args):
        """
        Sets the time stepping

        Parameters
        ----------
        type : `str`
        process : `str`
        t_initial : `int` or `str`
        t_end : `int` or `str`
        repeat : `int` or `str`
        delta_t : `float` or `str`
        minimum_dt : `float` or `str`
        maximum_dt : `float` or `str`
        number_iterations : `list`
        multiplier : `list`
        dt_guess : `float` or `str`
        dt_min : `float` or `str`
        dt_max : `float` or `str`
        rel_dt_max : `float` or `str`
        rel_dt_min : `float` or `str`
        tol : `float` or `str`
        """
        self._convertargs(args)
        if "process" not in args:
            raise KeyError("Process reference missing")
        if "type" not in args:
            raise KeyError("No type given.")
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
            self.process[args['process']]['time_stepping'][
                    "type"] = "IterationNumberBasedTimeStepping"
            self.process[args['process']]['time_stepping']['t_initial'] = args["t_initial"]
            self.process[args['process']]['time_stepping']['t_end'] = args["t_end"]
            self.process[args['process']]['time_stepping']['initial_dt'] = args["initial_dt"]
            self.process[args['process']]['time_stepping']['minimum_dt'] = args["minimum_dt"]
            self.process[args['process']]['time_stepping']['maximum_dt'] = args["maximum_dt"]
            numit_list = args["number_iterations"]
            multi_list = args["multiplier"]
            self.process[args['process']]['time_stepping']['number_iterations'] = " ".join(
                    map(str, numit_list))
            self.process[args['process']]['time_stepping']['multiplier'] = " ".join(
                    map(str, multi_list))
        elif args["type"] == "EvolutionaryPIDcontroller":
            self.process[args['process']]['time_stepping']["type"] = "EvolutionaryPIDcontroller"
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

    def add_output(self, **args):
        """
        Add output section.

        Parameters
        ----------
        type : `str`
        prefix : `str`
        suffix : `str`
        variables : `list` or `str`
        data_mode : `str`
        compress_output : `str`
        output_iteration_results: `bool` or `str`
        meshes : `str`
        repeat : `list` or `str`
        each_steps : `list` or `str`
        fixed_output_times : `list` or `str`
        """
        if "type" not in args:
            raise KeyError("If you want to specify an output method, \
                        you need to provide type, \
                        prefix and a list of variables.")
        if "prefix" not in args:
            raise KeyError("No prefix given.")
        if "variables" not in args:
            raise KeyError("Please provide a list with output variables.")
        self.output["type"] = args["type"]
        self.output["prefix"] = args["prefix"]
        if "suffix" in args:
            self.output["suffix"] = args["suffix"]
        if isinstance(args["variables"], list):
            self.output["variables"] = args["variables"]
        else:
            self.output["variables"] = [args["variables"]]
        if "data_mode" in args:
            self.output["data_mode"] = args["data_mode"]
        if "compress_output" in args:
            if isinstance(args["compress_output"], bool):
                if args["compress_output"] is True:
                    args["compress_output"] = "true"
                else:
                    args["compress_output"] = "false"
            self.output["compress_output"] = args["compress_output"]
        if "output_iteration_results" in args:
            if isinstance(args["output_iteration_results"], bool):
                if args["output_iteration_results"] is True:
                    args["output_iteration_results"] = "true"
                else:
                    args["output_iteration_results"] = "false"
            self.output["output_iteration_results"] = args["output_iteration_results"]
        if "meshes" in args:
            self.output["meshes"] = args["meshes"]
        if "repeat" in args:
            if "each_steps" not in args:
                raise KeyError("each_steps is a required tag if repeat is given.")
            if isinstance(args["repeat"], list):
                self.output["repeat"] = args["repeat"]
            else:
                self.output["repeat"] = [args["repeat"]]
            if isinstance(args["each_steps"], list):
                self.output["each_steps"] = args["each_steps"]
            else:
                self.output["each_steps"] = [args["each_steps"]]
        if "fixed_output_times" in args:
            if isinstance(args["fixed_output_times"], list):
                self.output["fixed_output_times"] = ' '.join([str(item) for item in args[
                    "fixed_output_times"]])
            else:
                self.output["fixed_output_times"] = str(args["fixed_output_times"])


    def add_time_stepping_pair(self, **args):
        """
        add a time stepping pair

        Parameters
        ----------
        repeat : `int` or `str`
        delta_t : `int` or `str`

        """
        self._convertargs(args)
        if "process" not in args:
            raise KeyError("No process referenced")
        if "repeat" in args and "delta_t" in args:
            self.process[args['process']]['time_stepping']['t_repeat'].append(args["repeat"])
            self.process[args['process']]['time_stepping']['t_deltat'].append(args["delta_t"])
        else:
            raise KeyError("You muss provide repeat and delta_t attributes to \
                        define additional time stepping pairs.")

    def add_output_pair(self, **args):
        """
        add an output pair

        Parameters
        ----------
        repeat : `int` or `str`
        each_steps : `int` or `str`
        """
        self._convertargs(args)
        if "repeat" in args and "each_steps" in args:
            self.output["repeat"].append(args["repeat"])
            self.output["each_steps"].append(args["each_steps"])
        else:
            raise KeyError("You muss provide repeat and each_steps attributes \
                        to define additional output pairs.")
