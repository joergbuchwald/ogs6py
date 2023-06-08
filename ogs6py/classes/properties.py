# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2023, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913

from dataclasses import dataclass, field
from typing import List, Any
from lxml import etree as ET

@dataclass
class Value:
    medium : str
    value : Any


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

property_dict = {"Solid": {"density": {"title": "Solid density", "symbol": "$\\rho_\\text{s}$", "unit": "kg m$^{-3}$"},
                           "specific_heat_capacity": {"title": "Specific heat capacity", "symbol": "$c_\\text{s}$", "unit": "J kg$^{-1}$ K$^{-1}$"},
                           "thermal_expansivity": {"title": "Thermal expansivity", "symbol": "$a_s$", "unit": "K$^{-1}$"},
                           "youngs_modulus": {"title": "Young's modulus", "symbol": "$E$", "unit": "Pa"},
                           "poissons_ratio": {"title": "Poisson's ratio", "symbol": "$\\nu$", "unit": "1"},

                           },
                 "Medium": {"porosity": {"title": "Porosity", "symbol": "$\phi$", "unit": "1"},
                            "biot_coefficient": {"title": "Biot-Willis coefficient", "symbol": "$\\alpha_\mathrm{B}$", "unit": "1"},
                            "permeability": {"title": "Intrinsic permeability", "symbol": "$k$", "unit": "m$^2$"},
                            "thermal_conductivity": {"title": "Thermal conductivity", "symbol": "$\lambda$", "unit": "W m$^{-1}$ K$^{-1}$"},
                            "vgsat_residual_liquid_saturation": {"title": "Saturation: Van Genuchten, \\\ residual liquid saturation", "symbol": "$S^r_\\text{L}$", "unit": "1"},
                            "vgsat_residual_gas_saturation": {"title": "Saturation: Van Genuchten, \\\ residual gas saturation  ", "symbol": "$S^r_\\text{g}$", "unit": "1"},
                            "vgsat_exponent": {"title": "Saturation: Van Genuchten, \\\ exponent", "symbol": "$m$", "unit": "1"},
                            "vgsat_p_b": {"title": "Saturation: Van Genuchten, \\\ entry pressure", "symbol": "$p_b$", "unit": "Pa"},
                            "vgrelperm_residual_liquid_saturation": {"title": "Relative permeability: Van Genuchten, \\\ residual liquid saturation  ", "symbol": "$S^r_\\text{L}$", "unit": "1"},
                            "vgrelperm_residual_gas_saturation": {"title": "Relative permeability: Van Genuchten, \\\ residual gas saturation  ", "symbol": "$S^r_\\text{g}$", "unit": "1"},
                            "vgrelperm_exponent": {"title": "Relative permeability: Van Genuchten, \\\ exponent", "symbol": "$m$", "unit": "1"},
                            "vgrelperm_minimum_relative_permeability_liquid": {"title": "Relative permeability: Van Genuchten, \\\ minimmum relative permeability", "symbol": "$k^\\text{min}_r$", "unit": "1"},
                            },
                 "AqueousLiquid": {"viscosity": {"title": "Liquid phase viscosity", "symbol": "$\mu_\mathrm{LR}$", "unit": "Pa s"},
                                   "density": {"title": "Liquid phase density", "symbol": "$\\rho_\mathrm{LR}$", "unit": "kg m$^{-3}$"},
                                   "specific_heat_capacity": {"title": "Liquid specific heat capacity", "symbol": "$c_\\text{LR}$", "unit": "J kg$^{-1}$ K$^{-1}$"},}}
location_pointer = {"Solid": "phases/phase[type='Solid']/",
                    "Medium": "",
                    "AqueousLiquid": "phases/phase[type='AqueousLiquid']/"}

def expand_tensors(obj, numofmedia, multidim_prop, root, location):
    #constant
    for medium_id in range(numofmedia):
        medium = obj._get_medium_pointer(root, medium_id)
        const_props = medium.findall(f"./{location_pointer[location]}properties/property[type='Constant']/value")
        tobedeleted = []
        for prop in const_props:
            proplist = prop.text.split(" ")
            tags = prop.getparent().getchildren()
            for tag in tags:
                if tag.tag == "name":
                    name = tag.text
                    multidim_prop[medium_id][name] = len(proplist)
            if multidim_prop[medium_id][name] > 1:
                properties_level = prop.getparent().getparent()
                tobedeleted.append(prop.getparent())
                taglist = ["name", "type", "value"]
                for i in range(multidim_prop[medium_id][name]):
                    textlist = [f"{name}{i}", "Constant", f"{proplist[i]}"]
                    q = ET.SubElement(properties_level, "property")
                    for i, tag in enumerate(taglist):
                        r = ET.SubElement(q, tag)
                        if not textlist[i] is None:
                            r.text = str(textlist[i])
    for element in tobedeleted:
        element.getparent().remove(element)
    #function
    for medium_id in range(numofmedia):
        medium = obj._get_medium_pointer(root, medium_id)
        function_props = medium.findall(f"./{location_pointer[location]}properties/property[type='Function']/value")
        tobedeleted = []
        for prop in function_props:
            proplist = [i.text for i in prop.findall("./expression")]
            tags = prop.getparent().getchildren()
            for tag in tags:
                if tag.tag == "name":
                    name = tag.text
                    multidim_prop[medium_id][name] = len(proplist)
            if multidim_prop[medium_id][name] > 1:
                properties_level = prop.getparent().getparent()
                tobedeleted.append(prop.getparent())
                taglist = ["name", "type", "value"]
                for i in range(multidim_prop[medium_id][name]):
                    textlist = [f"{name}{i}", "Function", None]
                    q = ET.SubElement(properties_level, "property")
                    for i, tag in enumerate(taglist):
                        r = ET.SubElement(q, tag)
                        if not textlist[i] is None:
                            r.text = str(textlist[i])
                        if tag == "value":
                            s = ET.SubElement(r, "expression")
                            s.text =  f"{proplist[i]}"
    for element in tobedeleted:
        element.getparent().remove(element)

def expand_van_genuchten(obj, numofmedia, root, location):
    for medium_id in range(numofmedia):
        medium = obj._get_medium_pointer(root, medium_id)
        sat_vg_props = medium.findall(f"./{location_pointer[location]}properties/property[type='SaturationVanGenuchten']")
        relperm_vg_props = medium.findall(f"./{location_pointer[location]}properties/property[type='RelativePermeabilityVanGenuchten']")
        vg_properties = [sat_vg_props, relperm_vg_props]
        tobedeleted = []
        for vg_property in vg_properties:
            for prop in vg_property:
                proplist = [property for property in prop.getchildren()]
                const_taglist = ["name", "type", "value"]
                prefix = ""
                for subprop in proplist:
                    if "SaturationVanGenuchten" in subprop.text:
                        prefix = "vgsat_"
                    elif "RelativePermeabilityVanGenuchten" in subprop.text:
                        prefix = "vgrelperm_"
                for subprop in proplist:
                    if not subprop.tag in ["name", "type"]:
                        const_textlist = [prefix+subprop.tag, "Constant", subprop.text]
                        q = ET.SubElement(prop.getparent(), "property")
                        for i, tag in enumerate(const_taglist):
                            r = ET.SubElement(q, tag)
                            if not const_textlist[i] is None:
                                r.text = str(const_textlist[i])
                tobedeleted.append(prop)
    for element in tobedeleted:
        element.getparent().remove(element)
