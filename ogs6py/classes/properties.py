# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2023, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913

from dataclasses import dataclass, field
from typing import List

@dataclass
class Value:
    medium : str
    value : float


@dataclass
class Property:
    title : str
    symbol : str
    unit : str
    value : List[Value] =  field(default_factory=list)

    def _dict(self):
        a = {
            "title": self.title,
            "symbol": self.symbol,
            "unit": self.unit,
        }
        for d in self.value:
            a[d.medium] = d.value
        return a



@dataclass
class PropertySet:
    property : List[Property] = field(default_factory=list)

    def __len__(self):
        """Number of time steps"""
        return len(self.property)

    def __iter__(self):
        for v in self.property:
            yield v._dict()

property_dict = {"Solid": {"density": {"title": "Solid density", "symbol": "$\rho_\text{s}$", "unit": "kg m$^{-3}$"},
                           "specific_heat_capacity": {"title": "Specific heat capacity", "symbol": "$c_\text{s}$", "unit": "J kg$^{-1}$ K$^{-1}$"},
                           "thermal_expansivity": {"title": "Thermal expansivity", "symbol": "$a_s$", "unit": "K$^{-1}$"},
                           "youngs_modulus": {"title": "Young's modulus", "symbol": "$E$", "unit": "Pa"},
                           "poissons_ratio": {"title": "Poisson's ratio", "symbol": "$\nu$", "unit": "1"},
                           },
                 "Medium": {"porosity": {"title": "Porosity", "symbol": "$\phi$", "unit": "1"},
                            "biot_coefficient": {"title": "Biot-Willis coefficient", "symbol": "$α_\mathrm{B}$", "unit": "1"},
                            "permeability": {"title": "Intrinsic permeability", "symbol": "$k$", "unit": "m$^2$"},
                            "thermal_conductivity": {"title": "Thermal conductivity", "symbol": "$\lambda$", "unit": "W m$^{-1}$ K$^{-1}$"}
                            },
                 "AqueousLiquid": {"viscosity": {"title": "Liquid phase viscosity", "symbol": "$\mu_\mathrm{LR}$", "unit": "Pa s"},
                                   "density": {"title": "Liquid phase density", "symbol": "$\rho_\mathrm{LR}$", "unit": "kg m$^{-3}$"},
                                   "specific_heat_capacity": {"title": "Liquid specific heat capacity", "symbol": "$c_\text{LR}$", "unit": "J kg$^{-1}$ K$^{-1}$"},}}
location_pointer = {"Solid": "phases/phase[type='Solid']/",
                    "Medium": "",
                    "AqueousLiquid": "phases/phase[type='AqueousLiquid']/"}
