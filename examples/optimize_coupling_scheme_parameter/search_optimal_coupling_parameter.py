#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 13:58:50 2021

@author: dominik kern (tu freiberg)
"""
from search_toolbox import coupling_parameter_search

basename = "StaggeredInjectionProduction1D"  # to derive filenames

CPS = coupling_parameter_search(basename)
CPS.start(x_minus=0.16, x_plus=1.0, tol = 0.01)

