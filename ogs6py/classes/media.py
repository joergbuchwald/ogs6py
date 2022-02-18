# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class Media(build_tree.BuildTree):
    """
    Class for defining a media material properties."
    """
    def __init__(self):
        self.tree = {
            'media': {
                'tag': 'media',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.properties = {"AverageMolarMass": [],
            "BishopsSaturationCutoff": ["cutoff_value"],
            "BishopsPowerLaw": ["exponent"],
            "CapillaryPressureRegularizedVanGenuchten": ["exponent",
                    "p_b",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "CapillaryPressureVanGenuchten": ["exponent",
                    "maximum_capillary_pressure"
                    "p_b",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "ClausiusClapeyron": ["critical_pressure",
                    "critical_temperature",
                    "reference_pressure",
                    "reference_temperature",
                    "triple_pressure",
                    "triple_temperature"],
            "Constant": ["value"],
            "Curve" : ["curve", "independent_variable"],
            "DupuitPermeability": ["parameter_name"],
            "EffectiveThermalConductivityPorosityMixing": [],
            "EmbeddedFracturePermeability": ["intrinsic_permeability",
                    "initial_aperture",
                    "mean_frac_distance",
                    "threshold_strain",
                    "fracture_normal",
                    "fracture_rotation_xy",
                    "fracture_rotation_yz"],
            "Function": ["value"],
            "Exponential": ["offset","reference_value"],
            "GasPressureDependentPermeability": ["initial_permeability",
                    "a1", "a2",
                    "pressure_threshold",
                    "minimum_permeability",
                    "maximum_permeability"],
            "IdealGasLaw": [],
            "IdealGasLawBinaryMixture": [],
            "KozenyCarmanModel": ["intitial_permeability", "initial_prosity"],
            "Linear": ["reference_value"],
            "LinearSaturationSwellingStress" : ["coefficient", "reference_saturation"],
            "LinearWaterVapourLatentHeat" : [],
            "OrthotropicEmbeddedFracturePermeability": ["intrinsic_permeability",
                    "mean_frac_distances",
                    "threshold_strains",
                    "fracture_normals",
                    "fracture_rotation_xy",
                    "fracture_rotation_yz",
                    "jacobian_factor"],
            "Parameter": ["parameter_name"],
            "PermeabilityMohrCoulombFailureIndexModel": ["cohesion",
                    "fitting_factor",
                    "friction_angle",
                    "initial_ppermeability",
                    "maximum_permeability",
                    "reference_permeability",
                    "tensile_strength_parameter"],
            "PermeabilityOrthotropicPowerLaw": ["exponents",
                    "intrinsic_permeabilities"],
            "PorosityFromMassBalance": ["initial_porosity",
                    "maximal_porosity",
                    "minimal_porosity"],
            "RelPermBrooksCorey": ["lambda",
                    "min_relative_permeability"
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "RelPermBrooksCoreyNonwettingPhase": ["lambda",
                    "min_relative_permeability"
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "RelPermLiakopoulos": [],
            "RelativePermeabilityNonWettingVanGenuchten": ["exponent",
                    "minimum_relative_permeability",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "RelativePermeabilityUdell": ["min_relative_permeability",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "RelativePermeabilityUdellNonwettingPhase": ["min_relative_permeability",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "RelativePermeabilityVanGenuchten": ["exponent",
                    "minimum_relative_permeability_liquid",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "SaturationBrooksCorey": ["entry_pressure",
                    "lambda",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "SaturationDependentSwelling": ["exponents",
                    "lower_saturation_limit",
                    "swelling_pressures",
                    "upper_saturation_limit"],
            "SaturationDependentThermalConductivity": ["dry","wet"],
            "SaturationExponential": ["exponent",
                    "maximum_capillary_pressure",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "SaturationLiakopoulos": [],
            "SaturationVanGenuchten": ["exponent",
                    "p_b",
                    "residual_gas_saturation",
                    "residual_liquid_saturation"],
            "SoilThermalConductivitySomerton": ["dry_thermal_conductivity",
                    "wet_thermal_conductivity"],
            "StrainDependentPermeability": ["initial_permeability",
                    "b1", "b2", "b3",
                    "minimum_permeability",
                    "maximum_permeability"],
            "TemperatureDependentDiffusion": ["activation_energy",
                    "reference_diffusion",
                    "reference_temperature"],
            "TransportPorosityFromMassBalance": ["initial_porosity",
                    "maximal_porosity",
                    "minimal_porosity"],
            "VapourDiffusionFEBEX": ["tortuosity"],
            "VapourDiffusionPMQ": [],
            "VermaPruessModel": ["critical_porosity",
                    "exponent",
                    "initial_permeability",
                    "initial_porosity"],
            "WaterVapourDensity": [],
            "WaterVapourLatentHeatWithCriticalTemperature": []
            }

    def _generate_generic_property(self, args):
        property_parameters = {}
        for parameter in self.properties[args["type"]]:
            property_parameters[parameter] = {
                    'tag': parameter,
                    'text': args[parameter],
                    'attr': {},
                    'children': {}
                }
        return property_parameters
    def _generate_linear_property(self, args):
        property_parameters = {}
        for parameter in self.properties[args["type"]]:
            property_parameters[parameter] = {
                    'tag': parameter,
                    'text': args[parameter],
                    'attr': {},
                    'children': {}
                }
        for var, param in args["independent_variables"].items():
            property_parameters[f"independent_variable{var}"] = {
                    'tag': 'independent_variable',
                    'text': '',
                    'attr': {},
                    'children': {}
                }
            indep_var = property_parameters[f"independent_variable{var}"]['children']
            indep_var['variable_name'] = {
                    'tag': 'variable_name',
                    'text': var,
                    'attr': {},
                    'children': {}
                }
            attributes = ['reference_condition','slope']
            for attrib in attributes:
                indep_var[attrib] = {
                    'tag': attrib,
                    'text': str(param[attrib]),
                    'attr': {},
                    'children': {}
                }
        return property_parameters
    def _generate_function_property(self, args):
        property_parameters = {}
        for parameter in self.properties[args["type"]]:
            property_parameters[parameter] = {
                    'tag': parameter,
                    'text': "",
                    'attr': {},
                    'children': {}
                }
        property_parameters["value"]["children"]["expression"] = {
                    'tag': "expression",
                    'text': args["expression"],
                    'attr': {},
                    'children': {}
                }
        for dvar in args["dvalues"]:
            property_parameters[f"dvalue{dvar}"] = {
                    'tag': "dvalue",
                    'text': "",
                    'attr': {},
                    'children': {}
                }
            property_parameters[f"dvalue{dvar}"]["children"]["variable_name"] = {
                    'tag': "variable_name",
                    'text': dvar,
                    'attr': {},
                    'children': {}
                }
            property_parameters[f"dvalue{dvar}"]["children"]["expression"] = {
                    'tag': "expression",
                    'text': args["dvalues"][dvar]["expression"],
                    'attr': {},
                    'children': {}
                }
        return property_parameters
    def _generate_exponential_property(self, args):
        property_parameters = {}
        for parameter in self.properties[args["type"]]:
            property_parameters[parameter] = {
                    'tag': parameter,
                    'text': args[parameter],
                    'attr': {},
                    'children': {}
                }
        property_parameters["exponent"] = {
                    'tag': 'exponent',
                    'text': '',
                    'attr': {},
                    'children': {}
                }
        indep_var = property_parameters["exponent"]['children']
        indep_var['variable_name'] = {
                    'tag': 'variable_name',
                    'text': args["exponent"]["variable_name"],
                    'attr': {},
                    'children': {}
                }
        attributes = ['reference_condition','factor']
        for attrib in attributes:
            indep_var[attrib] = {
                    'tag': attrib,
                    'text': str(args["exponent"][attrib]),
                    'attr': {},
                    'children': {}
                }
        return property_parameters

    def add_property(self, **args):
        """
        Adds a property to medium/phase

        Parameters
        ----------
        medium_id : `int` or `str`
        phase_type : `str`
        name : `str`
        type : `str`
        value : `float` or `str`
        exponent : `float` or `str`
        cutoff_value : `float` or `str`
        independent_variable : `str`
        reference_condition : `float` or `str`
        reference_value : `float` or `str`
        slope : `float` or `str`
        parameter_name : `str`
        """
        self._convertargs(args)
        if "medium_id" in args:
            try:
                medium = self.tree['media']['children'][args['medium_id']]
            except KeyError:
                self.tree['media']['children'][args['medium_id']] = {
                        'tag': 'medium',
                        'text': '',
                        'attr': {
                        'id': args['medium_id']},
                        'children': {}
                }
                medium = self.tree['media']['children'][args['medium_id']]
            if "phase_type" in args:
                if not 'phases' in medium['children']:
                    medium['children']['phases'] = {
                        'tag': 'phases',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }
                try:
                    phase_ = medium['children']['phases']['children'][
                        args['phase_type']]
                except KeyError:
                    medium['children']['phases']['children'][
                        args['phase_type']] = {
                            'tag': 'phase',
                            'text': '',
                            'attr': {},
                            'children': {}
                        }
                    phase_ = medium['children']['phases']['children'][
                        args['phase_type']]
                    phase_['children'][args['phase_type']] = {
                        'tag': 'type',
                        'text': args['phase_type'],
                        'attr': {},
                        'children': {}
                    }
                    phase_['children']['properties'] = {
                        'tag': 'properties',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }
            else:
                try:
                    _ = medium['children']['properties']
                except KeyError:
                    medium['children']['properties'] = {
                        'tag': 'properties',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }
                phase_ = medium
            phase = phase_['children']['properties']['children']
            phase[args['name']] = {
                'tag': 'property',
                'text': '',
                'attr': {},
                'children': {}
            }
            base_property_param = ["name", "type"]
            for param in base_property_param:
                phase[args['name']]['children'][param] = {
                    'tag': param,
                    'text': args[param],
                    'attr': {},
                    'children': {}
            }
            try:
                if args['type'] == "Linear":
                    phase[args['name']]['children'].update(self._generate_linear_property(args))
                elif args['type'] == "Exponential":
                    phase[args['name']]['children'].update(self._generate_exponential_property(args))
                elif args['type'] == "Function":
                    phase[args['name']]['children'].update(self._generate_function_property(args))
                else:
                    phase[args['name']]['children'].update(self._generate_generic_property(args))
            except KeyError:
                print("Material property parameters incomplete for")
                if "phase_type" in args:
                    print(f"Medium {args['medium_id']}->{args['phase_type']}->{args['name']}[{args['type']}]")
                else:
                    print(f"Medium {args['medium_id']}->{args['name']}[{args['type']}]")
