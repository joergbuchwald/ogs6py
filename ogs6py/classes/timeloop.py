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
    def __init__(self, tree):
        self.tree = tree
        self.root = self._get_root()
        self.time_loop = self.populate_tree(self.root, 'time_loop', overwrite=True)
        self.processes = self.populate_tree(self.time_loop, 'processes', overwrite=True)
        self.output = self.populate_tree(self.time_loop, 'output', overwrite=True)

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
        self._convertargs(args)
        if "process" not in args:
            raise KeyError("No process referenced")
        process_name = args['process']
        process = self.populate_tree(self.processes, 'process', attr={'ref': process_name})
        if "nonlinear_solver_name" not in args:
            raise KeyError("Please specify a name (nonlinear_solver_name) \
                        for the nonlinear solver.")
        self.populate_tree(process, 'nonlinear_solver', text=args['nonlinear_solver_name'])
        if "convergence_type" not in args:
            raise KeyError("No convergence criterion given. \
                            Specify convergence_type.")
        conv_crit = self.populate_tree(process, 'convergence_criterion')
        self.populate_tree(conv_crit, 'type', text=args['convergence_type'])
        if "norm_type" not in args:
            raise KeyError("No norm_type given.")
        self.populate_tree(conv_crit, 'norm_type', text=args['norm_type'])
        if (args["convergence_type"] == "DeltaX") or (args["convergence_type"] == "Residual"):
            if (("abstols" in args) or ("reltols" in args)):
                raise KeyError("Plural tolerances only available for PerComponent conv. types")
            if "abstol" in args:
                self.populate_tree(conv_crit, 'abstol', text=args['abstol'])
            if "reltol" in args:
                self.populate_tree(conv_crit, 'reltol', text=args['reltol'])
        elif (args["convergence_type"] == "PerComponentDeltaX") or (args["convergence_type"] == "PerComponentResidual"):
            if (("abstol" in args) or ("reltol" in args)):
                raise KeyError("Singular tolerances only available for scalar conv. types")
            if "abstols" in args:
                self.populate_tree(conv_crit, 'abstols', text=args['abstols'])
            if "reltols" in args:
                self.populate_tree(conv_crit, 'reltols', text=args['reltols'])
        else:
            raise KeyError("No convergence_type given.")
        if "time_discretization" not in args:
            raise KeyError("No time_discretization specified.")
        td = self.populate_tree(process, 'time_discretization')
        self.populate_tree(td, 'type', text=args['time_discretization'])


    def set_stepping(self, **args):
        """
        Sets the time stepping

        Parameters
        ----------
        type : `str`
        process : `str`
        t_initial : `int` or `str`
        initial_dt : `float` or `str`
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
        procs = self.processes.findall("./process")
        process = None
        for proc in procs:
            if args["process"] == proc.get("ref"):
                process = proc
        if process is None:
            raise KeyError("Process reference not found.")
        if "type" not in args:
            raise KeyError("No type given.")
        time_stepping = self.populate_tree(process, 'time_stepping')
        self.populate_tree(time_stepping, 'type', text=args['type'])
        if args["type"] == "FixedTimeStepping":
            self.populate_tree(time_stepping, 't_initial', text=args['t_initial'])
            self.populate_tree(time_stepping, 't_end', text=args['t_end'])
            if "repeat" in args and "delta_t" in args:
                ts = self.populate_tree(time_stepping, 'timesteps')
                if isinstance(args["repeat"], str) and isinstance(args["delta_t"], str):
                    pair = self.populate_tree(ts, 'pair')
                    self.populate_tree(pair, 'repeat', text=args['repeat'])
                    self.populate_tree(pair, 'delta_t', text=args['delta_t'])
                else:
                    for i, entry in enumerate(args["repeat"]):
                        pair = self.populate_tree(ts, 'pair')
                        self.populate_tree(pair, 'repeat', text=entry)
                        self.populate_tree(pair, 'delta_t', text=args['delta_t'][i])
            else:
                raise KeyError("No proper time stepping defined. \
                                Please specify repeat and delta_t.")
        elif args["type"] == "SingleStep":
            pass
        elif args["type"] == "IterationNumberBasedTimeStepping":
            self.populate_tree(time_stepping, 't_initial', text=args['t_initial'])
            self.populate_tree(time_stepping, 't_end', text=args['t_end'])
            self.populate_tree(time_stepping, 'initial_dt', text=args['initial_dt'])
            self.populate_tree(time_stepping, 'minimum_dt', text=args['minimum_dt'])
            self.populate_tree(time_stepping, 'maximum_dt', text=args['maximum_dt'])
            if isinstance(args["number_iterations"], str) and isinstance(args["multiplier"], str):
                self.populate_tree(time_stepping, 'number_iterations', text=args['number_iterations'])
                self.populate_tree(time_stepping, 'multiplier', text=args['multiplier'])
            else:
                self.populate_tree(time_stepping, 'number_iterations', text=" ".join(str(x) for x in args['number_iterations']))
                self.populate_tree(time_stepping, 'multiplier', text=" ".join(str(x) for x in args['multiplier']))

        elif args["type"] == "EvolutionaryPIDcontroller":
            self.populate_tree(time_stepping, 't_initial', text=args['t_initial'])
            self.populate_tree(time_stepping, 't_end', text=args['t_end'])
            self.populate_tree(time_stepping, 'dt_guess', text=args['dt_guess'])
            self.populate_tree(time_stepping, 'dt_min', text=args['dt_min'])
            self.populate_tree(time_stepping, 'dt_max', text=args['dt_max'])
            self.populate_tree(time_stepping, 'rel_dt_max', text=args['rel_dt_max'])
            self.populate_tree(time_stepping, 'rel_dt_min', text=args['rel_dt_min'])
            self.populate_tree(time_stepping, 'tol', text=args['tol'])

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
        variables : `list`
        data_mode : `str`
        compress_output : `str`
        output_iteration_results: `bool` or `str`
        meshes : `list` or `str`
        repeat : `list` or `str`
        each_steps : `list` or `str`
        fixed_output_times : `list` or `str`
        """
        if "type" not in args:
            raise KeyError("If you want to specify an output method, \
                        you need to provide type, \
                        prefix and a list of variables.")
        self.populate_tree(self.output, 'type', text=args['type'])
        if "prefix" in args:
            self.populate_tree(self.output, 'prefix', text=args['prefix'])
        if "suffix" in args:
            self.populate_tree(self.output, 'suffix', text=args['suffix'])
        if "data_mode" in args:
            self.populate_tree(self.output, 'data_mode', text=args['data_mode'])
        if "compress_output" in args:
            if isinstance(args["compress_output"], bool):
                if args["compress_output"] is True:
                    self.populate_tree(self.output, 'compress_output', text="true")
                else:
                    self.populate_tree(self.output, 'compress_output', text="false")
            else:
                self.populate_tree(self.output, 'compress_output', text=args["compress_output"])
        if "output_iteration_results" in args:
            if isinstance(args["output_iteration_results"], bool):
                if args["output_iteration_results"] is True:
                    self.populate_tree(self.output, 'output_iteration_results', text="true")
                else:
                    self.populate_tree(self.output, 'output_iteration_results', text="false")
            else:
                self.populate_tree(self.output, 'output_iteration_results', text=args["output_iteration_results"])
        if "meshes" in args:
            meshes = self.populate_tree(self.output, 'meshes')
            if isinstance(args["meshes"], str):
                self.populate_tree(meshes, 'mesh', text=args["meshes"])
            else:
                for mesh in args["meshes"]:
                    self.populate_tree(meshes, 'mesh', text=mesh)
                    # material_id attribute missing
        timesteps = self.populate_tree(self.output, 'timesteps')
        if "repeat" in args:
            if "each_steps" not in args:
                raise KeyError("each_steps is a required tag if repeat is given.")
            if isinstance(args["repeat"], list) and isinstance(args["each_steps"], list):
                for i, entry in enumerate(args["repeat"]):
                    pair = self.populate_tree(timesteps, 'pair')
                    self.populate_tree(pair, 'repeat', text=entry)
                    self.populate_tree(pair, 'each_steps', text=args['each_steps'][i])
            else:
                pair = self.populate_tree(timesteps, 'pair')
                self.populate_tree(pair, 'repeat', text=args["repeat"])
                self.populate_tree(pair, 'each_steps', text=args['each_steps'])
        variables = self.populate_tree(self.output, 'variables')
        if "variables" in args:
            if isinstance(args["variables"], list):
                for var in args["variables"]:
                    self.populate_tree(variables, 'variable', text=var)
            else:
                raise KeyError("parameter variables needs to be a list")
        if "fixed_output_times" in args:
            if isinstance(args["fixed_output_times"], list):
                self.populate_tree(self.output, 'fixed_output_times', text=" ".join(str(x) for x in args["fixed_output_times"]))
            else:
                self.populate_tree(self.output, 'fixed_output_times', text=args["fixed_output_times"])


    def add_time_stepping_pair(self, **args):
        """
        add a time stepping pair

        Parameters
        ----------
        process : `str`
        repeat : `int` or `str` or `list`
        delta_t : `int` or `str` or `list`

        """
        self._convertargs(args)
        if "process" not in args:
            raise KeyError("No process referenced")
        procs = self.processes.findall("./process")
        process = None
        for proc in procs:
            if args["process"] == proc.get("ref"):
                process = proc
        if process is None:
            raise KeyError("Process reference not found.")
        ts = process.find("./time_stepping/timesteps")
        if ts is None:
            raise RuntimeError("Cannot find time stepping section in the input file.")
        if "repeat" in args and "delta_t" in args:
            if isinstance(args["repeat"], str) and isinstance(args["delta_t"], str):
                pair = self.populate_tree(ts, 'pair')
                self.populate_tree(pair, 'repeat', text=args['repeat'])
                self.populate_tree(pair, 'delta_t', text=args['delta_t'])
            else:
                for i, entry in enumerate(args["repeat"]):
                    pair = self.populate_tree(ts, 'pair')
                    self.populate_tree(pair, 'repeat', text=entry)
                    self.populate_tree(pair, 'delta_t', text=args['delta_t'][i])
        else:
            raise KeyError("You muss provide repeat and delta_t attributes to \
                        define additional time stepping pairs.")

    def add_output_pair(self, **args):
        """
        add an output pair

        Parameters
        ----------
        repeat : `int` or `str` or `list`
        each_steps : `int` or `str` or `list`
        """
        self._convertargs(args)
        timesteps = self.output.find("./timesteps")
        if "repeat" in args and "each_steps" in args:
            if isinstance(args["repeat"], list) and isinstance(args["each_steps"], list):
                for i, entry in enumerate(args["repeat"]):
                    pair = self.populate_tree(timesteps, 'pair')
                    self.populate_tree(pair, 'repeat', text=entry)
                    self.populate_tree(pair, 'each_steps', text=args['each_steps'][i])
            else:
                pair = self.populate_tree(timesteps, 'pair')
                self.populate_tree(pair, 'repeat', text=args["repeat"])
                self.populate_tree(pair, 'each_steps', text=args['each_steps'])
        else:
            raise KeyError("You muss provide repeat and each_steps attributes \
                        to define additional output pairs.")
