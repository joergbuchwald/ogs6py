#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 13:58:50 2021

@author: dominik
"""
from search_toolbox import coupling_parameter_search

ogs_dir = "/home/dominik/OGS/release/bin"
basename = "StaggeredInjectionProduction1D"

CPS = coupling_parameter_search(ogs_dir, basename)

CPS.start(0.7, 0.1)

