#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 13:58:50 2021

This examples shows how to optimize the coupling parameter for a staggered scheme.
The staggered scheme is the fixed-stress split for hydromechanical systems.

More information about
- staggered scheme [Mikelic, Wheeler: Convergence of iterative coupling for coupled flow and geomechanics]
- coupling parameter [Storvik, Both, Kumar, Nordbotten, Radu: On the optimization of the fixed-stress splitting for Biot's equations]
- example model [Kim, Tchelepi: Stability, Accuracy and Efficiency of Sequential Methods for Coupled Flow and Geomechanics]

@author: dominik kern (tu freiberg)
"""
from search_toolbox import coupling_parameter_search

basename = "StaggeredInjectionProduction1D"  # to derive filenames

CPS = coupling_parameter_search(basename)
CPS.start(x_minus=0.16, x_plus=1.0, abs_tol=0.01)
