#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 14:15:08 2021

Find optimal coupling scheme parameter for the staggered scheme,
currently this parametrized scheme is only available for the HM-process. 

@author: dominik kern
"""

from ogs6py.ogs import OGS
from ogs6py.log_parser.log_parser import parse_file
from ogs6py.log_parser.common_ogs_analyses import (
    fill_ogs_context,
    analysis_convergence_coupling_iteration,
    analysis_simulation_termination,
)
from scipy.optimize import minimize_scalar
import numpy as np
import pandas as pd


class coupling_parameter_search:
    """Class for coupling scheme parameter search.

    Parameters
    ----------
    basename : `str`
        name from which filenames are derived
    ogs_dir : `str`, optional
        path to OGS installation
        if set to 'None', then it falls back to ogs6py default
        Default : None
    """

    def __init__(self, basename, ogs_dir=None):
        self.BASENAME = basename  # name of project file without suffix (.prj)
        self.OGS_DIR = ogs_dir
        self.MCI = (
            1000  # maximal number of coupling iterations (to assign to diverged runs)
        )
        self.default_csp = (
            0.5  # default value for coupling scheme parameter [Mikelic & Wheeler]
        )

        input_file = basename + ".prj"
        project_file = "auto_" + basename + ".prj"  # no changes so far

        self.model = OGS(INPUT_FILE=input_file, PROJECT_FILE=project_file, MKL=False)
        self.model.replace_text(
            "results_" + basename, xpath="./time_loop/output/prefix"
        )

    def run_sim(self, csp):
        """Runs a simulation with given coupling scheme parameter.

            Parameters
            ----------
            csp : `double`
                coupling scheme parameter
        """

        print("Run OGS with coupling scheme parameter = {}".format(csp))
        self.model.replace_text(
            csp, xpath="processes/process/coupling_scheme_parameter"
        )
        self.model.write_input()
        log_file = "auto_" + self.BASENAME + ".log"

        RUN_ERROR = False
        try:
            self.model.run_model(logfile=log_file, path=self.OGS_DIR)
        except RuntimeError:
            RUN_ERROR = True

        records = parse_file(log_file)
        df_records = pd.DataFrame(records)

        if RUN_ERROR:
            df_error = analysis_simulation_termination(df_records)
            mean_coupling_iterations = self.MCI + int(
                np.abs(100 * (csp - self.default_csp))
            )  # abs() to slide back to default 0.5

        else:
            df = fill_ogs_context(df_records)
            df_coupling = analysis_convergence_coupling_iteration(df)
            coupling_iterations = []
            for time_step_tuple in df_coupling.groupby(by="time_step"):
                coupling_iterations_per_time_step = time_step_tuple[
                    1
                ].index.get_level_values("coupling_iteration")
                coupling_iterations.append(coupling_iterations_per_time_step.max())

            mean_coupling_iterations = np.mean(coupling_iterations)

        return mean_coupling_iterations

    def start(self, x_minus=0.0, x_plus=1.0, abs_tol=0.025):
        """Start search for optimal parameter in given interval

            Parameters
            ----------
            x_minus : `double`
                lower endpoint
            x_plus : `double`
                upper endpoint
            abs_tol : `double`
                absolute tolerance to terminate search
        """

        print(
            "--- search (scipy) minimum within [{:1.3f}, {:1.3f}] ---".format(
                x_minus, x_plus
            )
        )
        x_optimal = minimize_scalar(
            self.run_sim,
            bounds=(x_minus, x_plus),
            method="bounded",
            options={"xatol": abs_tol},
        )

        if x_optimal.success:
            print("--- optimal coupling scheme parameter = {} ---".format(x_optimal.x))
        else:
            print(
                "--- search unsuccessfully stopped at coupling scheme parameter = {} ---".format(
                    x_optimal.x
                )
            )
