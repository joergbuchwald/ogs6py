#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 14:15:08 2021

find optimal coupling scheme parameter for staggered scheme
functionality currently only available for HM process (ogs)

@author: dominik
"""
from ogs6py.ogs import OGS
from ogs6py.log_parser.log_parser import parse_file
from ogs6py.log_parser.common_ogs_analyses import  fill_ogs_context, analysis_convergence_coupling_iteration
import numpy as np
import pandas as pd

class coupling_parameter_search:

    def __init__(self, ogs_dir, basename):
        self.OGS_DIR = ogs_dir   # directory with OGS executable, usually .../ogs/bin
        self.BASENAME = basename   # name of project file without suffix (.prj)
        
        input_file = basename + ".prj"
        project_file = "auto_" + basename + ".prj"  # no changes so far
        log_file = "auto_" + basename + ".log"
    
        self.model = OGS(INPUT_FILE=input_file, PROJECT_FILE=project_file, MKL=False) 
        self.model.replace_text("results_" + basename, xpath="./time_loop/output/prefix")

        self.invphi = (np.sqrt(5) - 1) / 2  # 1 / phi
        self.invphi2 = (3 - np.sqrt(5)) / 2  # 1 / phi^2


    def golden_section_search(self, f, a, b, tol=1e-5, h=None, c=None, d=None, fc=None, fd=None):
        """ Golden-section search, recursive.
    
        Given a function f with a single local minimum in
        the interval [a,b], gss returns a subset interval
        [c,d] that contains the minimum with d-c <= tol.
    
        Example:
        >>> f = lambda x: (x-2)**2
        >>> a = 1
        >>> b = 5
        >>> tol = 1e-5
        >>> (c,d) = gssrec(f, a, b, tol)
        >>> print (c, d)
        1.9999959837979107 2.0000050911830893
        """
    
        (a, b) = (min(a, b), max(a, b))
        if h is None: h = b - a
        if h <= tol: return (a, b)
        if c is None: c = a + self.invphi2 * h
        if d is None: d = a + self.invphi * h
        if fc is None: fc = f(c)
        if fd is None: fd = f(d)
        if fc < fd:
            return self.golden_section_search(f, a, d, tol, h * self.invphi, c=None, fc=None, d=c, fd=fc)
        else:
            return self.golden_section_search(f, c, b, tol, h * self.invphi, c=d, fc=fd, d=None, fd=None)


    def follow_descent(self, f, x, dx):
        """ go down until it goes up
        f function f(x)
        x starting value
        dx step size
        """
        x_center = x
        x_minus = x_center - dx
        x_plus = x_center + dx
    
        f_center = f(x_center)
        f_minus = f(x_minus)
        f_plus = f(x_plus)
    
        if (f_center > f_minus and f_center > f_plus):
            print("Warning, unexpected case of a maximum.")   # then both directions need to be checked!
            
        while not (f_center <= f_minus and f_center <= f_plus):   # go for minimum
            if f_minus <= f_center:
                x_plus -= dx
                x_center -= dx
                x_minus -= dx
                f_plus = f_center
                f_center = f_minus
                f_minus = f(x_minus)
            else: 
                x_plus += dx
                x_center += dx
                x_minus += dx
                f_minus = f_center
                f_center = f_plus
                f_plus = f(x_plus)
    
        return(x_minus, x_plus)    


    def run_sim(self, csp):
        self.model.replace_text(csp, xpath="processes/process/coupling_scheme_parameter") 
        self.model.write_input()
        log_file = self.BASENAME + ".log"
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


    def start(self, x_start=0.6, x_delta=0.1, tol=0.01):
        print("start search at {:1.3f} with step size {:1.3f}".format(x_start, x_delta))
        (x_minus, x_plus) = self.follow_descent(self.run_sim, x_start, x_delta)
        
        # search minimum
        print("search minimum within [{:1.3f}, {:1.3f}]".format(x_minus, x_plus))
        (found_minus, found_plus) = self.golden_section_search(self.run_sim, x_minus, x_plus, tol)
        x_optimal = 0.5*(found_minus + found_plus)

        print("optimal coupling scheme parameter = {}".format(x_optimal))
