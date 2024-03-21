import sys
import warnings

import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.ticker as mticker
import pandas as pd
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
        self.filterdict = {"by_time_step":parse_fcts.analysis_time_step,
                "convergence_newton_iteration":parse_fcts.analysis_convergence_newton_iteration,
                "convergence_coupling_iteration": parse_fcts.analysis_convergence_coupling_iteration,
                "time_step_vs_iterations":  parse_fcts.time_step_vs_iterations,
                "analysis_simulation": parse_fcts.analysis_simulation,
                "fill_ogs_context": parse_fcts.fill_ogs_context
                }
        self.logfile_ref_df = {}
        if self.ref_file is not None:
            records_ref = parser.parse_file(self.ref_file, maximum_lines=self.maximum_lines, force_parallel=False)
            df_ref = pd.DataFrame(records_ref)
            df_ref = parse_fcts.fill_ogs_context(df_ref)
            for j, filt in enumerate(self.filters):
                self.logfile_ref_df[j] = self.filterdict[filt](df_ref)
                self.logfile_ref_df[j].reset_index(inplace=True)
        else:
            for j, filt in enumerate(self.filters):
                self.logfile_ref_df[j] = None
        self.plot_init()
        self.plot()
    def plot_init(self):
        style.use('fast')
        if self.show_quadrant == -1:
            self.fig, self.axs = plt.subplots(2,2)
        else:
            self.fig, self.axs = plt.subplots(1,1)
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
        def animate(_):
            logfile_df = {}
            start = time.time()
            records = parser.parse_file(self.log_file, maximum_lines=self.maximum_lines, force_parallel=False)
            stop = time.time()
            print(f"parse {stop-start} s")
            start = time.time()
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
            stop = time.time()
            print(f"transform/filter df {stop-start} s")
            start = time.time()
            if ((self.show_quadrant == -1) or (self.show_quadrant == 1)):
                if self.show_quadrant == -1:
                    ax = self.axs[0,0]
                else:
                    ax = self.axs
                ax.clear()
                ax.plot(logfile_df[0]["time_step"], logfile_df[0]["iteration_number"], 'b', label="actual log")
                axs12 = ax.twiny()
                if not self.logfile_ref_df[0] is None:
                    axs12.plot(self.logfile_ref_df[0]["time_step"], self.logfile_ref_df[0]["iteration_number"], 'k', label="reference data")
                ax.set(xlabel="time step", ylabel="iterations")
                lines, labels = axs12.get_legend_handles_labels()
                lines2, labels2 = ax.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc=0)
                ax.set_title("iterations per time step")

            if ((self.show_quadrant == -1) or (self.show_quadrant == 0)):
                if self.show_quadrant == -1:
                      ax = self.axs[0,1]
                else:
                      ax = self.axs
                ax.clear()
                ax.plot(logfile_df[1]["time_step"], logfile_df[1]["step_size"], 'b', label="actual log")
                axs22 = ax.twiny()
                if not self.logfile_ref_df[1] is None:
                    axs22.plot(self.logfile_ref_df[1]["time_step"], self.logfile_ref_df[1]["step_size"], 'k', label="reference data")
                lines, labels = axs22.get_legend_handles_labels()
                lines2, labels2 = ax.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc=0)
                ax.set(xlabel="time step", ylabel="step size")
                ax.set_title("time step sizes")

            if ((self.show_quadrant == -1) or (self.show_quadrant == 2)):
                if self.show_quadrant == -1:
                    ax = self.axs[1,0]
                else:
                    ax = self.axs
                ax.clear()
                ax.plot(logfile_df[1]["time_step"],logfile_df[1]["assembly_time"],"b-", label="assembly time (actual)")
                ax.plot(logfile_df[1]["time_step"],logfile_df[1]["linear_solver_time"], "g-", label="linear solver time (actual)")
                axs32 = ax.twiny()
                if not self.logfile_ref_df[1] is None:
                    axs32.plot(self.logfile_ref_df[1]["time_step"], self.logfile_ref_df[1]["assembly_time"], "b--", label="assembly time (ref)")
                    axs32.plot(self.logfile_ref_df[1]["time_step"], self.logfile_ref_df[1]["linear_solver_time"], "g--", label="linear solver time (ref)")
                lines, labels = axs32.get_legend_handles_labels()
                lines2, labels2 = ax.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc=0)
                ax.set(xlabel="time step", ylabel="time / s")
                ax.set_title("time step sizes")

            if ((self.show_quadrant == -1) or (self.show_quadrant == 3)):
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
                if self.show_quadrant == -1:
                    ax = self.axs[1,1]
                else:
                    ax = self.axs
                ax.clear()
                ax.plot(newindex, logfile_df[2][logfile_df[2]["component"]==self.crit_comp][self.crit], 'b', label="actual")
                axs42 = ax.twiny()
                if not self.logfile_ref_df[2] is None:
                    axs42.plot(newindex_ref, self.logfile_ref_df[2][self.logfile_ref_df[2]["component"]==self.crit_comp][self.crit], 'k', label="reference")
                    axs42.xaxis.set_major_formatter(mticker.FuncFormatter(update_ticks_ref))
                    sec_ref = axs42.secondary_xaxis(location=1)
                    sec_ref.set_xticks(newindex2_ref, labels=time_data_ref)
                    sec_ref.tick_params('x', length=0)
                lines, labels = axs42.get_legend_handles_labels()
                lines2, labels2 = ax.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc=0)
                ax.set(xlabel="\n\ntime step", ylabel=self.crit)
                ax.set_title("criterion")
                ax.xaxis.set_major_formatter(mticker.FuncFormatter(update_ticks))
                ax.set_yscale('log')
                sec = ax.secondary_xaxis(location=0)
                sec.set_xticks(newindex2, labels=time_data)
                sec.tick_params('x', length=0)
            if self.running is True:
                self.fig.suptitle("OGS Monitor\n(OGS running)")
            else:
                self.fig.suptitle(f"OGS Monitor\n(OGS excec time: {logfile_df[3]['execution_time'].iloc[0]} s)")
            stop = time.time()
            print(f"plot {stop-start} s")
        ani = animation.FuncAnimation(self.fig, animate, interval=self.interval)
        plt.tight_layout()
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
