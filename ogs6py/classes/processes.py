# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
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
    def __init__(self):
        self.tree = {
            'processes': {
                'tag': 'processes',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.tree['processes']['children'] = {
            'process': {
                'tag': 'process',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.constreltree = {
            'tag': 'constitutive_relation',
            'text': '',
            'attr': {},
            'children': {}
        }
        self.proc_vartree = {
            'tag': 'process_variables',
            'text': '',
            'attr': {},
            'children': {}
        }
        self.sec_vartree = {
            'tag': 'secondary_variables',
            'text': '',
            'attr': {},
            'children': {}
        }
        self.bhe_tree = {                           
            'tag': 'borehole_heat_exchangers',
            'text': '',
            'attr': {},
            'children': {}
        } 
        self.sflux_vartree = {
            'tag': 'calculatesurfaceflux',
            'text': '',
            'attr': {},
            'children': {}
            }

    def add_process_variable(self, **args):
        """
        Adds a process variable.

        Parameters
        ----------
        process_variable : `str`
        process_variable_name : `str`
        secondary_variable : `str`
        output_name : `str`
        """
        self._convertargs(args)
        if "process_variable" in args:
            if "process_variable_name" not in args:
                raise KeyError("process_variable_name missing.")
            self.tree['processes']['children']['process']['children'][
                    'process_variables'] = self.proc_vartree
            self.proc_vartree['children'][args['process_variable_name']] = {
                    'tag': args['process_variable'],
                    'text': args['process_variable_name'],
                    'attr': {},
                    'children': {}
                    }
        elif "secondary_variable" in args:
            if "output_name" not in args:
                raise KeyError("No output_name given.")
            self.tree['processes']['children']['process']['children'][
                    'secondary_variables'] = self.sec_vartree
            self.sec_vartree['children'][args['output_name']] = {
                    'tag': 'secondary_variable',
                    'text': '',
                    'attr': {
                        'internal_name': args['secondary_variable'],
                        'output_name': args['output_name']
                        },
                    'children': {}
                    }
        else:
            raise KeyError("No process_variable/secondary_variable given.")

    def set_process(self, **args):
        """
        Set basic process properties.

        Parameters
        ----------
        name : `str`
        type : `str`
        integration_order : `str`
        darcy_gravity : `list` or `tuple`
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
                    self.tree['processes']['children']['process'][
                        'children']['darcy_gravity'] = self.populate_tree('darcy_gravity')
                    darcy_vel = self.tree['processes']['children']['process'][
                                    'children']['darcy_gravity']
                    darcy_vel['children']['axis'] = self.populate_tree('axis_id', text=str(i))
                    darcy_vel['children']['g'] = self.populate_tree('g', text=str(entry))

        for key, value in args.items():
            if isinstance(value, str):
                self.tree['processes']['children']['process'][
                    'children'][key] = self.populate_tree(key, text=args[key])


    def set_constitutive_relation(self, **args):
        """
        Sets constituitive relation

        Parameters
        ----------

        any pair tag="value" translates to
        <tag>value</tag> in process section
        """
        self._convertargs(args)
        self.tree['processes']['children']['process']['children'][
            'constitutive_relation'] = self.constreltree
        for key in args:
            self.constreltree['children'][key] = {
                'tag': key,
                'text': args[key],
                'attr': {},
                'children': {}
            }


    def add_bhe_type(self, **args):      
        self.tree['processes']['children']['process']['children']['borehole_heat_exchangers'] = {
            'borehole_heat_exchangers': {
                'tag': 'borehole_heat_exchangers',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        if 'bhe_type' in args:
            if not 'bhe_type' in args:
                raise KeyError('BHE type missing.')
            else:
                self.tree['processes']['children']['process']['children']['borehole_heat_exchangers'] = self.bhe_tree
                self.bhe_tree['children']['borehole_heat_exchanger'] = {
                    'tag': 'borehole_heat_exchanger',
                    'text': '',
                    'attr': {},
                    'children': {}
                }
                self.bhe_tree['children']['borehole_heat_exchanger']['children']['type'] = {
                    'tag': 'type',
                    'text': args['bhe_type'],
                    'attr': {},
                    'children': {}
                }
    def add_bhe_component(self, **args):      
        if not 'comp_type' in args:
            raise KeyError("No bhe component name specified.")
        else:
            self.bhe_tree['children']['borehole_heat_exchanger']['children'][args['comp_type']] = {
                    'tag': args['comp_type'],
                    'text': '',
                    'attr': {},
                    'children': {}
                }
            bhe_component = self.bhe_tree['children']['borehole_heat_exchanger']['children'][args['comp_type']]
            if args['comp_type'] == 'borehole':
                bhe_component['children']['length'] = self.populate_tree('length', text = args['length'], children={})
                bhe_component['children']['diameter'] = self.populate_tree('diameter', text = args['diameter'], children={})
            elif args['comp_type'] == 'pipes':
                if self.bhe_tree['children']['borehole_heat_exchanger']['children']['type']['text'] == "1U" or self.bhe_tree['children']['borehole_heat_exchanger']['children']['type']['text'] == "2U":
                    self.bhe_tree['children']['borehole_heat_exchanger']['children'][args['comp_type']]['children']['inlet'] = {
                        'tag': 'inlet',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }
                    self.bhe_tree['children']['borehole_heat_exchanger']['children'][args['comp_type']]['children']['outlet'] = {
                        'tag': 'outlet',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }                
                    bhe_component['children']['distance_between_pipes'] = self.populate_tree('distance_between_pipes', text = args['distance_between_pipes'], children={})
                elif self.bhe_tree['children']['borehole_heat_exchanger']['children']['type']['text'] == "CXC" or self.bhe_tree['children']['borehole_heat_exchanger']['children']['type']['text'] == "CXA":
                    self.bhe_tree['children']['borehole_heat_exchanger']['children'][args['comp_type']]['children']['inlet'] = {
                        'tag': 'inner',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }
                    self.bhe_tree['children']['borehole_heat_exchanger']['children'][args['comp_type']]['children']['outlet'] = {
                        'tag': 'outer',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }                
                inlet = self.bhe_tree['children']['borehole_heat_exchanger']['children'][args['comp_type']]['children']['inlet']
                outlet = self.bhe_tree['children']['borehole_heat_exchanger']['children'][args['comp_type']]['children']['outlet']
                inlet['children']['diameter'] = self.populate_tree('diameter', text = args['inlet_diameter'], children={})
                inlet['children']['wall_thickness'] = self.populate_tree('wall_thickness', text = args['inlet_wall_thickness'], children={})
                inlet['children']['wall_thermal_conductivity'] = self.populate_tree('wall_thermal_conductivity', text = args['inlet_wall_thermal_conductivity'], children={})
                outlet['children']['diameter'] = self.populate_tree('diameter', text = args['outlet_diameter'], children={})
                outlet['children']['wall_thickness'] = self.populate_tree('wall_thickness', text = args['outlet_wall_thickness'], children={})
                outlet['children']['wall_thermal_conductivity'] = self.populate_tree('wall_thermal_conductivity', text = args['outlet_wall_thermal_conductivity'], children={})
                bhe_component['children']['longitudinal_dispersion_length'] = self.populate_tree('longitudinal_dispersion_length', text = args['longitudinal_dispersion_length'], children={})
            elif args['comp_type'] == 'flow_and_temperature_control':
                if args['type'] == "FixedPowerConstantFlow":
                    bhe_component['children']['type'] = self.populate_tree('type', text = args['type'], children={})
                    bhe_component['children']['power'] = self.populate_tree('power', text = args['power'], children={})
                    bhe_component['children']['flow_rate'] = self.populate_tree('flow_rate', text = args['flow_rate'], children={})
                elif args['type'] == "FixedPowerFlowCurve":
                    bhe_component['children']['type'] = self.populate_tree('type', text = args['type'], children={})
                    bhe_component['children']['power'] = self.populate_tree('power', text = args['power'], children={})
                    bhe_component['children']['flow_rate_curve'] = self.populate_tree('flow_rate_curve', text = args['flow_rate_curve'], children={})
                elif args['type'] == "PowerCurveConstantFlow":
                    bhe_component['children']['type'] = self.populate_tree('type', text = args['type'], children={})
                    bhe_component['children']['power_curve'] = self.populate_tree('power_curve', text = args['power_curve'], children={})
                    bhe_component['children']['flow_rate'] = self.populate_tree('flow_rate', text = args['flow_rate'], children={}) 
                elif args['type'] == "TemperatureCurveConstantFlow":
                    bhe_component['children']['type'] = self.populate_tree('type', text = args['type'], children={})
                    bhe_component['children']['flow_rate'] = self.populate_tree('flow_rate', text = args['flow_rate'], children={})
                    bhe_component['children']['temperature_curve'] = self.populate_tree('temperature_curve', text = args['temperature_curve'], children={})
                elif args['type'] == "TemperatureCurveFlowCurve":
                    bhe_component['children']['type'] = self.populate_tree('type', text = args['type'], children={})
                    bhe_component['children']['flow_rate_curve'] = self.populate_tree('flow_rate_curve', text = args['flow_rate_curve'], children={})
                    bhe_component['children']['temperature_curve'] = self.populate_tree('temperature_curve', text = args['temperature_curve'], children={})
                elif args['type'] == "PowerCurveFlowCurve":
                    bhe_component['children']['type'] = self.populate_tree('type', text = args['type'], children={})
                    bhe_component['children']['power_curve'] = self.populate_tree('power_curve', text = args['power_curve'], children={})
                    bhe_component['children']['flow_rate_curve'] = self.populate_tree('flow_rate_curve', text = args['flow_rate_curve'], children={})          
            elif args['comp_type'] == 'grout':
                bhe_component['children']['density'] = self.populate_tree('density', text = args['density'], children={})
                bhe_component['children']['porosity'] = self.populate_tree('porosity', text = args['porosity'], children={})
                bhe_component['children']['specific_heat_capacity'] = self.populate_tree('specific_heat_capacity', text = args['specific_heat_capacity'], children={})
                bhe_component['children']['thermal_conductivity'] = self.populate_tree('thermal_conductivity', text = args['thermal_conductivity'], children={})
            elif args['comp_type'] == 'refrigerant':
                bhe_component['children']['density'] = self.populate_tree('density', text = args['density'], children={})
                bhe_component['children']['viscosity'] = self.populate_tree('viscosity', text = args['viscosity'], children={})
                bhe_component['children']['specific_heat_capacity'] = self.populate_tree('specific_heat_capacity', text = args['specific_heat_capacity'], children={})
                bhe_component['children']['thermal_conductivity'] = self.populate_tree('thermal_conductivity', text = args['thermal_conductivity'], children={})
                bhe_component['children']['reference_temperature'] = self.populate_tree('reference_temperature', text = args['reference_temperature'], children={})
    def add_surfaceflux(self,**args):
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
        self.tree['processes']['children']['process']['children'][
                'calculatesurfaceflux'] = self.sflux_vartree
        self.sflux_vartree['children']['mesh'] = {
                'tag': 'mesh',
                'text': args['mesh'],
                'attr': {},
                'children': {}
                }
        self.sflux_vartree['children']['property_name'] = {
                'tag': 'property_name',
                'text': args['property_name'],
                'attr': {},
                'children': {}
                }
