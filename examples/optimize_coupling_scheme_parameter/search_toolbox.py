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
from ogs6py.log_parser.common_ogs_analyses import  fill_ogs_context, analysis_convergence_coupling_iteration
from scipy.optimize import minimize_scalar
import numpy as np
import pandas as pd


class coupling_parameter_search:

    def __init__(self, basename, ogs_dir=None):
        self.BASENAME = basename   # name of project file without suffix (.prj)
        self.OGS_DIR = ogs_dir   
        
        input_file = basename + ".prj"
        project_file = "auto_" + basename + ".prj"  # no changes so far
        log_file = "auto_" + basename + ".log"
    
        self.model = OGS(INPUT_FILE=input_file, PROJECT_FILE=project_file, MKL=False) 
        self.model.replace_text("results_" + basename, xpath="./time_loop/output/prefix") 


    def run_sim(self, csp):
        print("Run OGS with coupling scheme parameter = {}".format(csp))
        self.model.replace_text(csp, xpath="processes/process/coupling_scheme_parameter") 
        self.model.write_input()
        log_file = self.BASENAME + ".log"
        
        if self.OGS_DIR is None:
            self.model.run_model(logfile = log_file)   
        else:
            self.model.run_model(path=self.OGS_DIR, logfile = log_file)
        
        records = parse_file(log_file)
        df_records = pd.DataFrame(records)
        # df_error = analysis_simulation_termination(df_records)    # TODO diverged=infinite iterations
        df = fill_ogs_context(df_records)               
        df_coupling = analysis_convergence_coupling_iteration(df)
        coupling_iterations = []
        for time_step_tuple in df_coupling.groupby(by='time_step'):           
            coupling_iterations_per_time_step = time_step_tuple[1].index.get_level_values('coupling_iteration')
            coupling_iterations.append( coupling_iterations_per_time_step.max() )
        return np.mean(coupling_iterations)


    def start(self, x_minus=0.0, x_plus=1.0, tol=0.025):
    
        print("--- search (scipy) minimum within [{:1.3f}, {:1.3f}] ---".format(x_minus, x_plus))
        x_optimal = minimize_scalar(self.run_sim, bounds=(x_minus, x_plus), method='bounded', tol=tol)
        
        if x_optimal.success:
            print("--- optimal coupling scheme parameter = {} ---".format(x_optimal.x))
        else:
            print("--- search unsuccessfully stopped at coupling scheme parameter = {} ---".format(x_optimal.x))
            