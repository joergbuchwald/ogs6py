import sys
import warnings

from ogs6py.ogs import OGS
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.ticker as mticker
import pandas as pd

warnings.simplefilter(action='ignore', category=FutureWarning)

class OGSMONITOR(object):
    def __init__(self, logfile, reffile, update_interval, window_length, maximum_lines, convergence_metric, convergence_component):
        self.f = OGS()
        self.log_file = logfile
        self.ref_file = reffile
        self.crit = convergence_metric
        self.crit_comp = convergence_component
        self.window_length = window_length
        self.interval = update_interval
        self.maximum_lines = maximum_lines
        self.filters = ["time_step_vs_iterations","by_time_step", "convergence_newton_iteration"]
        self.plot_init()
        self.plot()
    def plot_init(self):
        style.use('fast')
        self.fig, self.axs = plt.subplots(2,2)
    def plot(self):
        def animate(_):
            logfile_df = {}
            logfile_ref_df = {}
            for j, filt in enumerate(self.filters):
                try:
                    logfile_df[j] = self.f.parse_out(logfile=self.log_file, filter = filt, maximum_lines=self.maximum_lines)
                    if j == 2:
                        logfile_df[j] = logfile_df[j][logfile_df[j]["time_step"] >= logfile_df[j].time_step.max()-self.window_length]
                    else:
                        logfile_df[j] = logfile_df[j][-self.window_length:]
                except:
                    logfile_df[j] = None
                if self.ref_file is not None:
                    logfile_ref_df[j] = self.f.parse_out(logfile=self.ref_file, filter = filt)
                    if j == 2:
                        logfile_ref_df[j] = logfile_ref_df[j][logfile_ref_df[j]["time_step"] >= logfile_ref_df[j].time_step.max()-self.window_length]
                    else:
                        logfile_ref_df[j] = logfile_ref_df[j][-self.window_length:]
                else:
                    logfile_ref_df[j] = None
            if logfile_df[0] is None:
                return
            if logfile_df[1] is None:
                return
            self.axs[0,0].clear()
            self.axs[0,0].plot(logfile_df[0]["time_step"],logfile_df[0]["iteration_number"], 'b', label="actual log")
            axs12 = self.axs[0,0].twiny()
            if not logfile_ref_df[0] is None:
                axs12.plot(logfile_ref_df[0]["time_step"],logfile_ref_df[0]["iteration_number"], 'k', label="reference data")
                #axs12.set(xlabel="time step", ylabel="iterations")
            self.axs[0,0].set(xlabel="time step", ylabel="iterations")
            lines, labels = axs12.get_legend_handles_labels()
            lines2, labels2 = self.axs[0,0].get_legend_handles_labels()
            self.axs[0,0].legend(lines + lines2, labels + labels2, loc=0)
            #self.axs[0,0].legend()
            self.axs[0,0].set_title("iterations per time step")

            self.axs[0,1].clear()
            self.axs[0,1].plot(logfile_df[1]["time_step"],logfile_df[1]["step_size"], 'b', label="actual log")
            axs22 = self.axs[0,1].twiny()
            if not logfile_ref_df[1] is None:
                axs22.plot(logfile_ref_df[1]["time_step"],logfile_ref_df[1]["step_size"], 'k', label="reference data")
                #axs22.set(xlabel="time step", ylabel="step size")
            lines, labels = axs22.get_legend_handles_labels()
            lines2, labels2 = self.axs[0,1].get_legend_handles_labels()
            self.axs[0,1].legend(lines + lines2, labels + labels2, loc=0)
            self.axs[0,1].set(xlabel="time step", ylabel="step size")
            #self.axs[0,1].legend()
            self.axs[0,1].set_title("time step sizes")

            self.axs[1,0].clear()
            self.axs[1,0].plot(logfile_df[1]["time_step"],logfile_df[1]["assembly_time"],"b-", label="assembly time (actual)")
            self.axs[1,0].plot(logfile_df[1]["time_step"],logfile_df[1]["linear_solver_time"], "g-", label="linear solver time (actual)")
            axs32 = self.axs[1,0].twiny()
            if not logfile_ref_df[1] is None:
                axs32.plot(logfile_ref_df[1]["time_step"],logfile_ref_df[1]["assembly_time"], "b--", label="assembly time (ref)")
                axs32.plot(logfile_ref_df[1]["time_step"],logfile_ref_df[1]["linear_solver_time"], "g--", label="linear solver time (ref)")
                #axs32.set(xlabel="time step", ylabel="time / s")
            lines, labels = axs32.get_legend_handles_labels()
            lines2, labels2 = self.axs[1,0].get_legend_handles_labels()
            self.axs[1,0].legend(lines + lines2, labels + labels2, loc=0)
            self.axs[1,0].set(xlabel="time step", ylabel="time / s")
            #self.axs[1,0].legend()
            self.axs[1,0].set_title("time step sizes")

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
                    it_num = logfile_ref_df[2][logfile_ref_df[2]["component"]==self.crit_comp]["iteration_number"].iloc[pos]
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

            if not logfile_ref_df[2] is None:
                newindex_ref = []
                for i in logfile_ref_df[2][logfile_ref_df[2]["component"]==self.crit_comp].index:
                    newindex_ref.append(f"{i}")

                newindex2_ref = [i for i in range(len(newindex_ref))]
                time_data_ref = []
                tmp = ""
                for i in logfile_ref_df[2][logfile_ref_df[2]["component"]==self.crit_comp]["time_step"]:
                    if i == tmp:
                        time_data_ref.append("")
                    else:
                        time_data_ref.append(f"{i}")
                    tmp = i

            self.axs[1,1].clear()
            self.axs[1,1].plot(newindex, logfile_df[2][logfile_df[2]["component"]==self.crit_comp][self.crit], 'b', label="actual")
            axs42 = self.axs[1,1].twiny()
            if not logfile_ref_df[2] is None:
                axs42.plot(newindex_ref, logfile_ref_df[2][logfile_ref_df[2]["component"]==self.crit_comp][self.crit], 'k', label="reference")
                #axs42.set(xlabel="\n\ntime step", ylabel=self.crit)
                axs42.xaxis.set_major_formatter(mticker.FuncFormatter(update_ticks_ref))
                sec_ref = axs42.secondary_xaxis(location=1)
                sec_ref.set_xticks(newindex2_ref, labels=time_data_ref)
                sec_ref.tick_params('x', length=0)
            lines, labels = axs42.get_legend_handles_labels()
            lines2, labels2 = self.axs[1,1].get_legend_handles_labels()
            self.axs[1,1].legend(lines + lines2, labels + labels2, loc=0)
            self.axs[1,1].set(xlabel="\n\ntime step", ylabel=self.crit)
            #self.axs[1,1].legend()
            self.axs[1,1].set_title("criterion")
            self.axs[1,1].xaxis.set_major_formatter(mticker.FuncFormatter(update_ticks))
            self.axs[1,1].set_yscale('log')
            sec = self.axs[1,1].secondary_xaxis(location=0)
            sec.set_xticks(newindex2, labels=time_data)
            sec.tick_params('x', length=0)
        ani = animation.FuncAnimation(self.fig, animate, interval=self.interval)
        #plt.title("OGS Monitor")
        plt.tight_layout()
        plt.show()

#ani = animation.FuncAnimation(fig, animate, interval=1000)
#plt.show()

if __name__ == '__main__':
    input_file = sys.argv[1]
    ref_file = None
    update_interval = 3000
    window_length = 10
    maximum_lines = None
    convergence_metric = "dx"
    convergence_component = 0
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
            print(" -h : display this help")
    if norun is False:
        ogs_monitor = OGSMONITOR(input_file, ref_file, update_interval, window_length, maximum_lines, convergence_metric, convergence_component)
