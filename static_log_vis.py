# pylint: disable=C0301
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

import ogs6py
import ogs6py.log_parser.log_parser as parser
import ogs6py.log_parser.common_ogs_analyses as parse_fcts

class PLOTLOG(object):
    def __init__(self,
                 logfilelist,
                 maximum_lines,
                 convergence_metric,
                 convergence_component,
                 convergence_type,
                 show_quadrant):
        self.log_file = logfilelist
        self.crit = convergence_metric
        self.crit_comp = convergence_component
        if maximum_lines is None:
            self.maximum_lines = maximum_lines
        else:
            self.maximum_lines = int(maximum_lines)
        self.running = True
        self.show_quadrant = int(show_quadrant)
        self.convergence_type = convergence_type
        self.criteria_types = {"PerComponentDeltaX": ogs6py.ogs_regexes.ogs_regexes.ComponentConvergenceCriterion,
                          "DeltaX": ogs6py.ogs_regexes.ogs_regexes.TimeStepConvergenceCriterion,
                          "Residual": ogs6py.ogs_regexes.ogs_regexes.ConvergenceCriterionResidual,
                          "Res": ogs6py.ogs_regexes.ogs_regexes.Residual,
                          "PerComponentResidual": ogs6py.ogs_regexes.ogs_regexes.ComponentConvergenceCriterionResidual}
        self.filters = ["time_step_vs_iterations","by_time_step", "convergence_newton_iteration","analysis_simulation"]
        # plot data from records actual
        self.last_record = {file:0 for file in self.log_file}
        self.last_line = {file:0 for file in self.log_file}
        self.timesteps = {file:[] for file in self.log_file}
        self.ts_simtime = {file:[] for file in self.log_file}
        self.iterations_per_ts = {file:[] for file in self.log_file}
        self.assembly_solver_time = {file:[] for file in self.log_file}
        self.criterion_x = {file:[] for file in self.log_file}
        self.criterion_label = {file:[] for file in self.log_file}
        self.criterion_y = {file:[] for file in self.log_file}
        self.crit_timesteppointer = {file:[] for file in self.log_file}
        self.time_step_solution_time = {file:[] for file in self.log_file}
        self.walltime = {file:0 for file in self.log_file}
        self.records = {}
        for file in logfilelist:
            records_ref, _ = parser.parse_file(file, maximum_lines=self.maximum_lines, force_parallel=False)
            self.records[file] =  records_ref
            self.parse_records(self.records[file], dataset=file)
        self.plot()

    def plot(self):
        if (self.show_quadrant == 1):
            for file in self.log_file:
                plt.plot(np.array(self.timesteps[file]), np.array(self.iterations_per_ts[file]), label=file)
            plt.xlabel("time step")
            plt.ylabel("iterations")
            plt.title("iterations per timestep")
            plt.legend()
            plt.show()
        elif self.show_quadrant == 0:
            for file in self.log_file:
                plt.plot(np.array(self.timesteps[file]), np.array(self.ts_simtime[file])[:,1], label=file)
            plt.xlabel("time step")
            plt.ylabel("step size")
            plt.title("step size per timestep")
            plt.legend()
            plt.show()
        elif self.show_quadrant == 2:
            for file in self.log_file:
                plt.plot(np.array(self.timesteps[file]), np.array(self.ts_simtime[file])[:,0], label=file)
            plt.xlabel("time step")
            plt.ylabel("time step start time")
            plt.title("start time vs timestep")
            plt.legend()
            plt.show()



    def parse_records(self, records, dataset="actual"):
        #len_records = len(records)
        for record in records: #[self.last_record[dataset]:len_records]:
            if isinstance(record, ogs6py.ogs_regexes.ogs_regexes.TimeStepStartTime):
                self.timesteps[dataset].append(int(record.time_step))
                self.ts_simtime[dataset].append((float(record.step_start_time), float(record.step_size)))
                self.iterations_per_ts[dataset].append(1)
                self.assembly_solver_time[dataset].append([0, 0])

            elif isinstance(record, ogs6py.ogs_regexes.ogs_regexes.IterationTime):
                self.iterations_per_ts[dataset][-1] = int(record.iteration_number)+1
            elif isinstance(record, ogs6py.ogs_regexes.ogs_regexes.AssemblyTime):
                self.assembly_solver_time[dataset][-1][0] = (self.assembly_solver_time[dataset][-1][0] +
                                                    float(record.assembly_time)) / (self.iterations_per_ts[dataset][-1])
            elif isinstance(record, ogs6py.ogs_regexes.ogs_regexes.LinearSolverTime):
                self.assembly_solver_time[dataset][-1][1] = (self.assembly_solver_time[dataset][-1][1] +
                                                   float(record.linear_solver_time)) / (self.iterations_per_ts[dataset][-1])
            elif isinstance(record, self.criteria_types[self.convergence_type]):
                if self.convergence_type in ["PerComponentResidual", "PerComponentDeltaX"]:
                    comp = record.component
                else:
                    comp = int(self.crit_comp)
                if comp == int(self.crit_comp):
                    if int(self.iterations_per_ts[dataset][-1]) == 1:
                        self.criterion_x[dataset].append(len(self.criterion_x[dataset])+1)
                        self.criterion_label[dataset].append(f"{self.iterations_per_ts[dataset][-1]} \n{self.timesteps[dataset][-1]}")
                        self.criterion_y[dataset].append(float(getattr(record, self.crit)))
                        self.crit_timesteppointer[dataset].append(len(self.criterion_x[dataset])-1)
                    else:
                        self.criterion_x[dataset].append(len(self.criterion_x[dataset])+1)
                        self.criterion_label[dataset].append(f"{self.iterations_per_ts[dataset][-1]} \n")
                        self.criterion_y[dataset].append(float(getattr(record, self.crit)))
            elif isinstance(record, ogs6py.ogs_regexes.ogs_regexes.TimeStepSolutionTime):
                self.time_step_solution_time[dataset].append(float(record.time_step_solution_time))
            elif isinstance(record, ogs6py.ogs_regexes.ogs_regexes.SimulationExecutionTime):
                self.walltime[dataset] = float(record.execution_time)

if __name__ == '__main__':
    input_files = []
    for entry in sys.argv:
        if ".log" in entry:
            input_files.append(entry)
    window_length = 10
    maximum_lines = None
    convergence_metric = "dx"
    convergence_component = 0
    convergence_type = "PerComponentDeltaX"
    show_quadrant = 0
    norun = False
    for i, arg in enumerate(sys.argv):
        if arg == "-r":
            ref_file = sys.argv[i+1]
        elif arg == "-wl":
            window_length = sys.argv[i+1]
        elif arg == "-ml":
            maximum_lines = sys.argv[i+1]
        elif arg == "-cm":
            convergence_metric = sys.argv[i+1]
        elif arg == "-cc":
            convergence_component = sys.argv[i+1]
        elif arg == "-ct":
            convergence_type = sys.argv[i+1]
        elif arg == "-ui":
            update_interval = sys.argv[i+1]
        elif arg == "-q":
            show_quadrant = sys.argv[i+1]
        elif arg == "-h":
            norun = True
            print("OGS monitor help\n")
            print("default usage: ogs-monitor.py [logfile.log ...] args")
            print("args:")
            print(" -ml [max lines]  : provide maximum lines to read in")
            print(" -cm [convergence metric]  : provide convergence metric, could be dx, r, dx/x")
            print(" -cc [convergence component]  : provide convergence component, default: 0")
            print(" -ct [convergence type] : provide a type could be DeltaX, PerComponentDeltaX (default), PerComponentResidual, Residual")
            print(" -q [X] : show only quadrant X, default: all four are shown")
            print(" -h : display this help")
    if norun is False:
        ogs_monitor = PLOTLOG(input_files, maximum_lines, convergence_metric, convergence_component, convergence_type, show_quadrant)
    
