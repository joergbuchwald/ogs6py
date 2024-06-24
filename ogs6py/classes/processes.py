# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2024, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class Processes(build_tree.BuildTree):
    """
    Class for managing the processes section in the project file.
    """
    def __init__(self, tree):
        self.tree = tree
        self.root = self._get_root()
        self.processes = self.populate_tree(self.root, "processes", overwrite=True)
        self.process = self.populate_tree(self.processes, "process", overwrite=True)
        self.procvars = None
        self.procvar = {}
        self.secondvars = None
        self.secondvar = {}
        self.process_baseentries = {}
        self.constitutive_relation = {}
        self.borehole_heat_exchangers = None
        self.borehole_heat_exchanger = []

    def add_process_variable(self, process_variable="", process_variable_name=""):
        """
        Adds a process variable.

        Parameters
        ----------
        process_variable : `str`
        process_variable_name : `str`
        """
        self.procvars = self.populate_tree(self.process, "process_variables", overwrite=True)
        if process_variable != "":
            if process_variable_name == "":
                raise KeyError("process_variable_name missing.")
            self.procvar[process_variable] = self.populate_tree(self.procvars,
                                            process_variable, text=process_variable_name)

    def add_secondary_variable(self, internal_name, output_name):
        """
        Adds a secondary variable.

        Parameters
        ----------
        internal_variable : `str`
        output_name : `str`
        """
        self.secondvars = self.populate_tree(self.process, "secondary_variables", overwrite=True)
        attrs = {"internal_name": internal_name, "output_name": output_name}
        self.populate_tree(self.secondvars, "secondary_variable", attr=attrs)

    def set_process(self, **args):
        """
        Set basic process properties.

        Parameters
        ----------
        name : `str`
        type : `str`
        integration_order : `str`
        darcy_gravity/specific_body_force : `list` or `tuple`
                        holding darcy accelleration as vector
        any pair tag="value" translates to
        <tag>value</tag> in process section
        """
        self._convertargs(args)
        if "name" not in args:
            raise KeyError("No process name given.")
        if "type" not in args:
            raise KeyError("type missing.")
        if "integration_order" not in args:
            raise KeyError("integration_order missing.")
        if "darcy_gravity" in args:
            for i, entry in enumerate(args["darcy_gravity"]):
                if entry != 0.0:
                    self.process_baseentries["darcy_gravity"] = self.populate_tree(
                            self.process, "darcy_gravity")
                    self.populate_tree(self.process_baseentries["darcy_gravity"],
                            "axis_id",text =str(i))
                    self.populate_tree(self.process_baseentries["darcy_gravity"],
                            "g",text = str(entry))
        if "specific_body_force" in args:
            self.populate_tree(self.process, "specific_body_force", text=" ".join(str(x) for x in args['specific_body_force']))
        for key, value in args.items():
            if isinstance(value, str):
                self.populate_tree(self.process, key, text=value)


    def set_constitutive_relation(self, **args):
        """
        Sets constituitive relation

        Parameters
        ----------

        any pair property="parameter_name" translates to
        <property>parameter_name</property> in constitutive_relation section
        if more constitutuitive relations are given use id key word
        """
        self._convertargs(args)
        if "id" in args:
            const_rel = self.populate_tree(self.process, "constitutive_relation", attr={"id": args["id"]})
        else:
            const_rel = self.populate_tree(self.process, "constitutive_relation", overwrite=True)
        for key, value in args.items():
            if key not in ["id"]:
                self.populate_tree(const_rel, key, text=value, overwrite=True)


    def add_bhe_type(self, bhe_type):
        """
        Adds a BHE type
        """
        self.borehole_heat_exchangers = self.populate_tree(
                self.process, "borehole_heat_exchangers", overwrite=True)
        self.borehole_heat_exchanger.append(self.populate_tree(
                        self.borehole_heat_exchangers, "borehole_heat_exchanger"))
        self.populate_tree(self.borehole_heat_exchanger[-1], "type", text = bhe_type)

    def add_bhe_component(self, index=0, **args):
        """
        adds a BHE component
        """
        self._convertargs(args)
        bhe_type = ""
        if 'comp_type' not in args:
            raise KeyError("No BHE component name specified.")
        bhecomponent = self.populate_tree(self.borehole_heat_exchanger[index], args['comp_type'])
        if bhecomponent.tag == "borehole":
            self.populate_tree(bhecomponent, 'length', text = args['length'])
            self.populate_tree(bhecomponent, 'diameter', text = args['diameter'])
        elif bhecomponent.tag == "pipes":
            for element in self.borehole_heat_exchanger[index]:
                if element.tag == "type":
                    bhe_type = element.text
            inlet_text = "inlet"
            outlet_text = "outlet"
            if bhe_type in ("CXA", "CXC"):
                inlet_text = "inner"
                outlet_text = "outer"
            inlet = self.populate_tree(bhecomponent, inlet_text)
            outlet = self.populate_tree(bhecomponent, outlet_text)
            self.populate_tree(inlet, "diameter", text=args['inlet_diameter'])
            self.populate_tree(inlet, "wall_thickness", text=args['inlet_wall_thickness'])
            self.populate_tree(inlet, "wall_thermal_conductivity", text=args['inlet_wall_thermal_conductivity'])
            self.populate_tree(outlet, "diameter", text=args['outlet_diameter'])
            self.populate_tree(outlet, "wall_thickness", text=args['outlet_wall_thickness'])
            self.populate_tree(outlet, "wall_thermal_conductivity", text=args['outlet_wall_thermal_conductivity'])
            self.populate_tree(bhecomponent, "distance_between_pipes", text=args['distance_between_pipes'])
            self.populate_tree(bhecomponent, "longitudinal_dispersion_length", text=args['longitudinal_dispersion_length'])

        elif bhecomponent.tag == "flow_and_temperature_control":
            self.populate_tree(bhecomponent, "type", text=args['type'])
            if args['type']  == "FixedPowerConstantFlow":
                self.populate_tree(bhecomponent, "power", text=args['power'])
                self.populate_tree(bhecomponent, "flow_rate", text=args['flow_rate'])
            elif args['type'] == "FixedPowerFlowCurve":
                self.populate_tree(bhecomponent, "power", text=args['power'])
                self.populate_tree(bhecomponent, "flow_rate_curve", text=args['flow_rate_curve'])
            elif args['type'] == "PowerCurveConstantFlow":
                self.populate_tree(bhecomponent, "power_curve", text=args['power_curve'])
                self.populate_tree(bhecomponent, "flow_rate", text=args['flow_rate'])
            elif args['type'] == "TemperatureCurveConstantFlow":
                self.populate_tree(bhecomponent, "flow_rate", text=args['flow_rate'])
                self.populate_tree(bhecomponent, "temperature_curve", text=args['temperature_curve'])
            elif args['type'] == "TemperatureCurveFlowCurve":
                self.populate_tree(bhecomponent, "flow_rate_curve", text=args['flow_rate_curve'])
                self.populate_tree(bhecomponent, "temperature_curve", text=args['temperature_curve'])
            elif args['type'] == "PowerCurveFlowCurve":
                self.populate_tree(bhecomponent, "power_curve", text=args['power_curve'])
                self.populate_tree(bhecomponent, "flow_rate_curve", text=args['flow_rate_curve'])

        elif bhecomponent.tag == "grout":
            self.populate_tree(bhecomponent, "density", text=args['density'])
            self.populate_tree(bhecomponent, "porosity", text=args['porosity'])
            self.populate_tree(bhecomponent, "specific_heat_capacity", text=args['specific_heat_capacity'])
            self.populate_tree(bhecomponent, "thermal_conductivity", text=args['thermal_conductivity'])

        elif bhecomponent.tag == "refrigerant":
            self.populate_tree(bhecomponent, "density", text=args['density'])
            self.populate_tree(bhecomponent, "viscosity", text=args['viscosity'])
            self.populate_tree(bhecomponent, "specific_heat_capacity", text=args['specific_heat_capacity'])
            self.populate_tree(bhecomponent, "thermal_conductivity", text=args['thermal_conductivity'])
            self.populate_tree(bhecomponent, "reference_temperature", text=args['reference_temperature'])

    def add_surfaceflux(self, **args):
        """
        Add SurfaceFlux

        Parameters
        ----------
        mesh : `str`
        property_name : `str`

        Raises
        ------
        KeyError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self._convertargs(args)

        if "mesh" not in args:
            raise KeyError("No surface mesh for flux analysis assigned")
        if "property_name" not in args:
            raise KeyError("No property name, e.g specific_flux, assigned")
        surfaceflux = self.populate_tree(self.process, "calculatesurfaceflux", overwrite=True)
        self.populate_tree(surfaceflux, "mesh", args["mesh"])
        self.populate_tree(surfaceflux, "property_name", args["property_name"])
