import os
import sys
import warnings

import time
import numpy as np
try:
    from PIL import Image
    imagemodule = True
except ModuleNotFoundError:
    print("module Image not installed")
    imagemodule = False
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.ticker as mticker
import pandas as pd
import ogs6py
import ogs6py.log_parser.log_parser as parser
import ogs6py.log_parser.common_ogs_analyses as parse_fcts

warnings.simplefilter(action='ignore', category=FutureWarning)

class OGSMONITOR(object):
    def __init__(self, logfile, reffile, update_interval, window_length, maximum_lines, convergence_metric, convergence_component, show_quadrant):
        self.log_file = logfile
        self.ref_file = reffile
        self.crit = convergence_metric
        self.crit_comp = convergence_component
        self.window_length = int(window_length)
        self.interval = float(update_interval)
        if maximum_lines is None:
            self.maximum_lines = maximum_lines
        else:
            self.maximum_lines = int(maximum_lines)
        self.running = True
        self.show_quadrant = int(show_quadrant)
        self.filters = ["time_step_vs_iterations","by_time_step", "convergence_newton_iteration","analysis_simulation"]
        """
        self.filterdict = {"by_time_step":parse_fcts.analysis_time_step,
                "convergence_newton_iteration":parse_fcts.analysis_convergence_newton_iteration,
                "convergence_coupling_iteration": parse_fcts.analysis_convergence_coupling_iteration,
                "time_step_vs_iterations":  parse_fcts.time_step_vs_iterations,
                "analysis_simulation": parse_fcts.analysis_simulation,
                "fill_ogs_context": parse_fcts.fill_ogs_context
                }
        """
        # plot data from records actual
        self.last_record = {"actual": 0, "ref": 0}
        self.last_line = {"actual": 0, "ref": 0}
        self.timesteps = {"actual": [], "ref": []}
        self.ts_simtime = {"actual": [], "ref": []}
        self.iterations_per_ts = {"actual": [], "ref": []}
        self.assembly_solver_time = {"actual": [], "ref": []}
        self.criterion_x = {"actual": [], "ref": []}
        self.criterion_label = {"actual": [], "ref": []}
        self.criterion_y = {"actual": [], "ref": []}
        self.crit_timesteppointer = {"actual": [], "ref": []}

        if self.ref_file is not None:
            records_ref, _ = parser.parse_file(self.ref_file, maximum_lines=self.maximum_lines, force_parallel=False)
            self.parse_records(records_ref, dataset="ref")
            """
            df_ref = pd.DataFrame(records_ref)
            df_ref = parse_fcts.fill_ogs_context(df_ref)
            for j, filt in enumerate(self.filters):
                self.logfile_ref_df[j] = self.filterdict[filt](df_ref)
                self.logfile_ref_df[j].reset_index(inplace=True)
            """
        self.q0_xb = None
        self.q0_yb = None
        self.q1_xb = None
        self.q1_yb = None
        self.q2_xb = None
        self.q2_yb = None
        self.q3_xb = None
        self.q3_yb = None
        # plot data from records actual
        self.plot_init()
        self.plot()

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
            elif isinstance(record, ogs6py.ogs_regexes.ogs_regexes.ComponentConvergenceCriterion):
                if record.component == int(self.crit_comp):
                    if int(self.iterations_per_ts[dataset][-1]) == 1:
                        self.criterion_x[dataset].append(len(self.criterion_x[dataset])+1)
                        self.criterion_label[dataset].append(f"{self.iterations_per_ts[dataset][-1]} \n{self.timesteps[dataset][-1]}")
                        self.criterion_y[dataset].append(float(getattr(record, self.crit)))
                        self.crit_timesteppointer[dataset].append(len(self.criterion_x[dataset])-1)
                    else:
                        self.criterion_x[dataset].append(len(self.criterion_x[dataset])+1)
                        self.criterion_label[dataset].append(f"{self.iterations_per_ts[dataset][-1]} \n")
                        self.criterion_y[dataset].append(float(getattr(record, self.crit)))
                    #self.criterion[dataset].append((self.timesteps[dataset][-1], self.iterations_per_ts[dataset], getattr(record, self.crit)))
        #self.last_record[dataset] = len_records


    def plot_init(self):
        style.use('fast')
        if self.show_quadrant == -1:
            self.fig, self.axs = plt.subplots(2,2)
        else:
            self.fig, self.axs = plt.subplots(1,1)
        if imagemodule is True:
            dirname = os.path.dirname(__file__)
            im = Image.open(os.path.join(dirname, "ogs.png"))
            height = im.size[1]
            width = im.size[0]
            newsize = (int(width/2), int(height/2))
            im = im.resize(newsize)
            self.fig.figimage(im, 0, 0, alpha=0.5)
    def map_quadrant_rqfilter(self, j):
        if j == 3:
            return True
        elif self.show_quadrant == -1:
            return True
        elif j == 1 and self.show_quadrant == 0:
            return True
        elif j == 0 and self.show_quadrant == 1:
            return True
        elif j == 1 and self.show_quadrant == 2:
            return True
        elif j == 2 and self.show_quadrant == 3:
            return True
        else:
            return False
    def plot(self):
        def animate(m):
            print(m)
            logfile_df = {}
            start = time.time()
            records, self.last_line["actual"] = parser.parse_file(
                    self.log_file,
                    maximum_lines=self.maximum_lines,
                    force_parallel=False,
                    start_line=self.last_line["actual"])
            stop = time.time()
            print(f"parse {stop-start} s")
            start = time.time()
            self.parse_records(records)
            """
            df = pd.DataFrame(records)
            df = parse_fcts.fill_ogs_context(df)
            for j, filt in enumerate(self.filters):
                if self.map_quadrant_rqfilter(j):
                    try:
                        logfile_df[j] = self.filterdict[filt](df)
                        logfile_df[j].reset_index(inplace=True)
                        if j == 3:
                            self.running = False
                        elif j == 2:
                            logfile_df[j] = logfile_df[j][logfile_df[j]["time_step"] >= logfile_df[j].time_step.max()-self.window_length]
                            if self.ref_file is not None:
                                self.logfile_ref_df[j] = self.logfile_ref_df[j][self.logfile_ref_df[j]["time_step"] >= self.logfile_ref_df[j].time_step.max()-self.window_length]
                        else:
                            logfile_df[j] = logfile_df[j][-self.window_length:]
                            if self.ref_file is not None:
                                self.logfile_ref_df[j] = self.logfile_ref_df[j][-self.window_length:]
                    except:
                        if j ==3:
                            self.running = True
                        logfile_df[j] = None
            if ((self.show_quadrant == 0) or (self.show_quadrant == -1)):
                if logfile_df[1] is None:
                    return
            if ((self.show_quadrant == 1) or (self.show_quadrant == -1)):
                if logfile_df[0] is None:
                    return
            """
            stop = time.time()
            print(f"transform/filter df {stop-start} s")
            start = time.time()
            window_length = self.window_length
            if len(self.timesteps["actual"]) < self.window_length:
                window_length = len(self.timesteps["actual"])
            ts0 = int(np.array(self.timesteps["actual"])[-window_length])-1
            ts1 = int(np.array(self.timesteps["actual"])[-1])
            if ((self.show_quadrant == -1) or (self.show_quadrant == 1)):
                if self.show_quadrant == -1:
                    ax = self.axs[0,0]
                else:
                    ax = self.axs
                ax.clear()
                #ax.spines['top'].set_visible(False) not working
                #ax.spines['right'].set_visible(False)
                """
                ax.plot(logfile_df[0]["time_step"], logfile_df[0]["iteration_number"], 'b', label="actual log")
                """
                ax.plot(np.array(self.timesteps["actual"])[-window_length:], np.array(self.iterations_per_ts["actual"])[-window_length:], 'b', label="actual log")
                if self.q1_yb is None:
                    self.q1_yb = ax.twiny()
                    self.q1_yb.get_legend_handles_labels()
                    #self.q1_yb.get_yaxis().set_visible(False)
                if not self.ref_file is None:
                    #self.q1_yb.get_yaxis().set_visible(False)
                    self.q1_yb.clear()
                    self.q1_yb.plot(np.array(self.timesteps["ref"])[ts0:ts1], np.array(self.iterations_per_ts["ref"])[ts0:ts1], 'k', label="reference data")
                ax.set(xlabel="time step", ylabel="iterations")
                lines, labels = self.q1_yb.get_legend_handles_labels()
                lines2, labels2 = ax.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc=0)
                ax.set_title("iterations per time step")

            if ((self.show_quadrant == -1) or (self.show_quadrant == 0)):
                if self.show_quadrant == -1:
                      ax = self.axs[0,1]
                else:
                      ax = self.axs
                #ax.spines['top'].set_visible(False)
                for entry in ax.get_shared_x_axes().get_siblings(ax):
                    entry.clear()
                """
                ax.plot(logfile_df[1]["time_step"], logfile_df[1]["step_size"], 'b-', label="time step (actual)")
                """
                ax.plot(np.array(self.timesteps["actual"])[-window_length:], np.array(self.ts_simtime["actual"])[:,1][-window_length:], 'b-', label="time step (actual)")
                if self.q0_yb is None:
                    self.q0_yb = ax.twiny()
                    #self.q0_yb.get_yaxis().set_visible(False)
                if not self.ref_file is None:
                    #self.q0_yb.get_yaxis().set_visible(True)
                    self.q0_yb.clear()
                    self.q0_yb.plot(np.array(self.timesteps["ref"])[ts0:ts1], np.array(self.ts_simtime["ref"])[:,1][ts0:ts1], 'k-', label="time step (reference)")
                if self.q0_xb is None:
                    self.q0_xb = ax.twinx()
                """
                self.q0_xb.plot(logfile_df[1]["time_step"], logfile_df[1]["step_start_time"], 'r-', label="start time (actual)")
                """
                self.q0_xb.plot(np.array(self.timesteps["actual"])[-window_length:], np.array(self.ts_simtime["actual"])[:,0][-window_length:], 'r-', label="start time (actual)")
                self.q0_xb.set_ylabel("time / s", color="r")
                self.q0_xb.yaxis.set_label_position("right")
                lines, labels = self.q0_yb.get_legend_handles_labels()
                lines2, labels2 = ax.get_legend_handles_labels()
                lines3, labels3 = self.q0_xb.get_legend_handles_labels()
                ax.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc=0)
                ax.set_xlabel("time step")
                ax.set_ylabel("step size", color='b')
                ax.set_title("time step sizes")

            if ((self.show_quadrant == -1) or (self.show_quadrant == 2)):
                if self.show_quadrant == -1:
                    ax = self.axs[1,0]
                else:
                    ax = self.axs
                ax.clear()
                """
                ax.plot(logfile_df[1]["time_step"],logfile_df[1]["assembly_time"],"b-", label="assembly time (actual)")
                ax.plot(logfile_df[1]["time_step"],logfile_df[1]["linear_solver_time"], "g-", label="linear solver time (actual)")
                """
                ax.plot(np.array(self.timesteps["actual"])[-window_length:], np.array(self.assembly_solver_time["actual"])[:,0][-window_length:],"b-", label="assembly time (actual)")
                ax.plot(np.array(self.timesteps["actual"])[-window_length:], np.array(self.assembly_solver_time["actual"])[:,1][-window_length:], "g-", label="linear solver time (actual)")
                if self.q2_yb is None:
                    self.q2_yb = ax.twiny()
                    #self.q2_yb.get_yaxis().set_visible(False)
                if not self.ref_file is None:
                    #self.q2_yb.get_yaxis().set_visible(True)
                    self.q2_yb.clear()
                    self.q2_yb.plot(self.timesteps["ref"][ts0:ts1], np.array(self.assembly_solver_time["ref"])[:,0][ts0:ts1], "b--", label="assembly time (ref)")
                    self.q2_yb.plot(self.timesteps["ref"][ts0:ts1], np.array(self.assembly_solver_time["ref"])[:,1][ts0:ts1], "g--", label="linear solver time (ref)")
                lines, labels = self.q2_yb.get_legend_handles_labels()
                lines2, labels2 = ax.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc=0)
                ax.set(xlabel="time step", ylabel="time / s")
                ax.set_title("time step sizes")

            if ((self.show_quadrant == -1) or (self.show_quadrant == 3)):
                """
                start2 = time.time()
                newindex = []
                for i in logfile_df[2][logfile_df[2]["component"]==self.crit_comp].index:
                    newindex.append(f"{i}")

                def update_ticks(x, pos):
                    if pos is None:
                        return ""
                    else:
                        it_num = logfile_df[2][logfile_df[2]["component"]==self.crit_comp]["iteration_number"].iloc[pos]
                        return f"{it_num}"
                def update_ticks_ref(x, pos):
                    if pos is None:
                        return ""
                    else:
                        it_num = self.logfile_ref_df[2][self.logfile_ref_df[2]["component"]==self.crit_comp]["iteration_number"].iloc[pos]
                        return f"{it_num}\n"

                newindex2 = [i for i in range(len(newindex))]
                time_data = []
                tmp = ""
                for i in logfile_df[2][logfile_df[2]["component"]==self.crit_comp]["time_step"]:
                    if i == tmp:
                        time_data.append("")
                    else:
                        time_data.append(f"\n\n{i}")
                    tmp = i

                if not self.logfile_ref_df[2] is None:
                    newindex_ref = []
                    for i in self.logfile_ref_df[2][self.logfile_ref_df[2]["component"]==self.crit_comp].index:
                        newindex_ref.append(f"{i}")

                    newindex2_ref = [i for i in range(len(newindex_ref))]
                    time_data_ref = []
                    tmp = ""
                    for i in self.logfile_ref_df[2][self.logfile_ref_df[2]["component"]==self.crit_comp]["time_step"]:
                        if i == tmp:
                            time_data_ref.append("")
                        else:
                            time_data_ref.append(f"{i}")
                        tmp = i
                stop2 = time.time()
                print(f"index trafo {stop2-start2} s")
                """
                line_begin = self.crit_timesteppointer['actual'][ts0]
                line_begin_ref = self.crit_timesteppointer['ref'][ts0]
                line_stop_ref = line_begin_ref
                if len(self.crit_timesteppointer['ref']) <= ts1:
                    ts1 = len(self.crit_timesteppointer['ref']) - 1
                    line_stop_ref = len(self.criterion_x['ref'])
                else:
                    line_stop_ref = self.crit_timesteppointer['ref'][ts1-1]
                def update_ticks(x, pos):
                    if pos is None:
                        return ""
                    else:
                        it_num = self.criterion_label["actual"][line_begin:][pos]
                        return f"{it_num}"
                def update_ticks_ref(x, pos):
                    if pos is None:
                        return ""
                    else:
                        it_num = self.criterion_label["ref"][line_begin_ref:line_stop_ref][pos]
                        return f"{it_num}"
                if self.show_quadrant == -1:
                    ax = self.axs[1,1]
                else:
                    ax = self.axs
                ax.clear()
                #ax.plot(newindex, logfile_df[2][logfile_df[2]["component"]==self.crit_comp][self.crit], 'b', label="actual")
                ax.plot(np.array(self.criterion_x["actual"])[line_begin:], np.array(self.criterion_y["actual"])[line_begin:],"b-", label="criterion (actual)")
                if self.q3_yb is None:
                    self.q3_yb = ax.twiny()
                    #self.q3_yb.get_yaxis().set_visible(False)
                if not self.ref_file is None:
                    self.q3_yb.clear()
                    #self.q3_yb.get_yaxis().set_visible(True)
                    self.q3_yb.plot(np.array(self.criterion_x["ref"])[line_begin_ref:line_stop_ref], np.array(self.criterion_y["ref"])[line_begin_ref:line_stop_ref], 'k', label="reference")
                    self.q3_yb.set_xticks(np.array(self.criterion_x["actual"][line_begin_ref:line_stop_ref]))
                    self.q3_yb.xaxis.set_major_formatter(mticker.FuncFormatter(update_ticks_ref))
                    #sec_ref = self.q3_yb.secondary_xaxis(location=1)
                    #sec_ref.set_xticks(newindex2_ref, labels=time_data_ref)
                    #sec_ref.tick_params('x', length=0)
                lines, labels = self.q3_yb.get_legend_handles_labels()
                lines2, labels2 = ax.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc=0)
                ax.set(xlabel="\niterations, time step", ylabel=self.crit)
                ax.set_title("criterion")
                ax.tick_params('x', which='both', length=0)
                ax.set_xticks(np.array(self.criterion_x["actual"][line_begin:]))
                ax.xaxis.set_major_formatter(mticker.FuncFormatter(update_ticks))
                ax.set_yscale('log')
                #sec = ax.secondary_xaxis(location=0)
                #sec.set_xticks(newindex2, labels=time_data)
                #sec.tick_params('x', length=0)
            if self.running is True:
                try:
                    self.fig.suptitle(f"OGS running\n({logfile_df[1]['time_step_solution_time'].sum()} s)")
                except:
                    self.fig.suptitle("OGS running")
            else:
                self.fig.suptitle(f"OGS finished\n({logfile_df[3]['execution_time'].iloc[0]} s)")
            stop = time.time()
            print(f"plot {stop-start} s")
        ani = animation.FuncAnimation(self.fig, animate, interval=self.interval)
        #äplt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        plt.subplots_adjust(plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9, hspace=0.3, wspace=0.2))
        plt.show()


if __name__ == '__main__':
    input_file = sys.argv[1]
    ref_file = None
    update_interval = 4000
    window_length = 10
    maximum_lines = None
    convergence_metric = "dx"
    convergence_component = 0
    show_quadrant = -1
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
        elif arg == "-ui":
            update_interval = sys.argv[i+1]
        elif arg == "-q":
            show_quadrant = sys.argv[i+1]
        elif arg == "-h":
            norun = True
            print("OGS monitor help\n")
            print("default usage: ogs-monitor.py logfile.log")
            print("args:")
            print(" -r [file]  : provide reference data")
            print(" -wl [window length]  : provide length of displayed data")
            print(" -ml [max lines]  : provide maximum lines to read in")
            print(" -cm [convergence metric]  : provide convergence metric, could be dx, r, dx/x")
            print(" -cc [convergence component]  : provide convergence component, default: 0")
            print(" -ui [update interval]  : provide an update interval in ms")
            print(" -q [X] : show only quadrant X, default: all four are shown")
            print(" -h : display this help")
    if norun is False:
        ogs_monitor = OGSMONITOR(input_file, ref_file, update_interval, window_length, maximum_lines, convergence_metric, convergence_component, show_quadrant)
