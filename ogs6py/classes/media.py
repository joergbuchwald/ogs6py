"""
Copyright (c) 2012-2024, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from typing import Any

from lxml import etree as ET

from ogstools.ogs6py import build_tree


class Media(build_tree.BuildTree):
    """
    Class for defining a media material properties."
    """

    def __init__(self, tree: ET.ElementTree) -> None:
        self.tree = tree
        self.root = self._get_root()
        self.media = self.populate_tree(self.root, "media", overwrite=True)

        self.properties: dict[str, list[str]] = {
            "AverageMolarMass": [],
            "BishopsSaturationCutoff": ["cutoff_value"],
            "BishopsPowerLaw": ["exponent"],
            "CapillaryPressureRegularizedVanGenuchten": [
                "exponent",
                "p_b",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "CapillaryPressureVanGenuchten": [
                "exponent",
                "maximum_capillary_pressurep_b",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "ClausiusClapeyron": [
                "critical_pressure",
                "critical_temperature",
                "reference_pressure",
                "reference_temperature",
                "triple_pressure",
                "triple_temperature",
            ],
            "Constant": ["value"],
            "Curve": ["curve", "independent_variable"],
            "DupuitPermeability": ["parameter_name"],
            "EffectiveThermalConductivityPorosityMixing": [],
            "EmbeddedFracturePermeability": [
                "intrinsic_permeability",
                "initial_aperture",
                "mean_frac_distance",
                "threshold_strain",
                "fracture_normal",
                "fracture_rotation_xy",
                "fracture_rotation_yz",
            ],
            "Function": ["value"],
            "Exponential": ["offset", "reference_value"],
            "GasPressureDependentPermeability": [
                "initial_permeability",
                "a1",
                "a2",
                "pressure_threshold",
                "minimum_permeability",
                "maximum_permeability",
            ],
            "IdealGasLaw": [],
            "IdealGasLawBinaryMixture": [],
            "KozenyCarmanModel": ["intitial_permeability", "initial_prosity"],
            "Linear": ["reference_value"],
            "LinearSaturationSwellingStress": [
                "coefficient",
                "reference_saturation",
            ],
            "LinearWaterVapourLatentHeat": [],
            "OrthotropicEmbeddedFracturePermeability": [
                "intrinsic_permeability",
                "mean_frac_distances",
                "threshold_strains",
                "fracture_normals",
                "fracture_rotation_xy",
                "fracture_rotation_yz",
                "jacobian_factor",
            ],
            "Parameter": ["parameter_name"],
            "PermeabilityMohrCoulombFailureIndexModel": [
                "cohesion",
                "fitting_factor",
                "friction_angle",
                "initial_ppermeability",
                "maximum_permeability",
                "reference_permeability",
                "tensile_strength_parameter",
            ],
            "PermeabilityOrthotropicPowerLaw": [
                "exponents",
                "intrinsic_permeabilities",
            ],
            "PorosityFromMassBalance": [
                "initial_porosity",
                "maximal_porosity",
                "minimal_porosity",
            ],
            "RelPermBrooksCorey": [
                "lambda",
                "min_relative_permeabilityresidual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "RelPermBrooksCoreyNonwettingPhase": [
                "lambda",
                "min_relative_permeabilityresidual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "RelPermLiakopoulos": [],
            "RelativePermeabilityNonWettingVanGenuchten": [
                "exponent",
                "minimum_relative_permeability",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "RelativePermeabilityUdell": [
                "min_relative_permeability",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "RelativePermeabilityUdellNonwettingPhase": [
                "min_relative_permeability",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "RelativePermeabilityVanGenuchten": [
                "exponent",
                "minimum_relative_permeability_liquid",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "SaturationBrooksCorey": [
                "entry_pressure",
                "lambda",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "SaturationDependentSwelling": [
                "exponents",
                "lower_saturation_limit",
                "swelling_pressures",
                "upper_saturation_limit",
            ],
            "SaturationDependentThermalConductivity": ["dry", "wet"],
            "SaturationExponential": [
                "exponent",
                "maximum_capillary_pressure",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "SaturationLiakopoulos": [],
            "SaturationWeightedThermalConductivity": [
                "mean_type",
                "dry_thermal_conductivity",
                "wet_thermal_conductivity",
            ],
            "SaturationVanGenuchten": [
                "exponent",
                "p_b",
                "residual_gas_saturation",
                "residual_liquid_saturation",
            ],
            "SoilThermalConductivitySomerton": [
                "dry_thermal_conductivity",
                "wet_thermal_conductivity",
            ],
            "StrainDependentPermeability": [
                "initial_permeability",
                "b1",
                "b2",
                "b3",
                "minimum_permeability",
                "maximum_permeability",
            ],
            "TemperatureDependentDiffusion": [
                "activation_energy",
                "reference_diffusion",
                "reference_temperature",
            ],
            "TransportPorosityFromMassBalance": [
                "initial_porosity",
                "maximal_porosity",
                "minimal_porosity",
            ],
            "VapourDiffusionFEBEX": ["tortuosity"],
            "VapourDiffusionPMQ": [],
            "VermaPruessModel": [
                "critical_porosity",
                "exponent",
                "initial_permeability",
                "initial_porosity",
            ],
            "WaterVapourDensity": [],
            "WaterDensityIAPWSIF97Region1": [],
            "WaterVapourLatentHeatWithCriticalTemperature": [],
        }

    def _generate_generic_property(
        self, property_: ET.Element, args: dict[str, Any]
    ) -> None:
        for parameter in self.properties[args["type"]]:
            self.populate_tree(property_, parameter, text=args[parameter])

    def _generate_linear_property(
        self, property_: ET.Element, args: dict[str, Any]
    ) -> None:
        for parameter in self.properties[args["type"]]:
            self.populate_tree(property_, parameter, text=args[parameter])
        for var, param in args["independent_variables"].items():
            ind_var = self.populate_tree(property_, "independent_variable")
            self.populate_tree(ind_var, "variable_name", text=var)
            attributes = ["reference_condition", "slope"]
            for attrib in attributes:
                self.populate_tree(ind_var, attrib, text=str(param[attrib]))

    def _generate_function_property(
        self, property_: ET.Element, args: dict[str, Any]
    ) -> None:
        for parameter in self.properties[args["type"]]:
            value = self.populate_tree(
                property_, parameter, text=args[parameter]
            )
        self.populate_tree(value, "expression", text=args["expression"])
        for dvar in args["dvalues"]:
            dvalue = self.populate_tree(property_, "dvalue")
            self.populate_tree(dvalue, "variable_name", text=dvar)
            self.populate_tree(
                dvalue, "expression", text=args["dvalues"][dvar]["expression"]
            )

    def _generate_exponential_property(
        self, property_: ET.Element, args: dict[str, Any]
    ) -> None:
        for parameter in self.properties[args["type"]]:
            self.populate_tree(property_, parameter, text=args[parameter])
        exponent = self.populate_tree(property_, "exponent")
        self.populate_tree(
            exponent, "variable_name", text=args["exponent"]["variable_name"]
        )
        attributes = ["reference_condition", "factor"]
        for attrib in attributes:
            self.populate_tree(
                exponent, attrib, text=str(args["exponent"][attrib])
            )

    def add_property(self, **args: Any) -> None:
        """
        Adds a property to medium/phase

        Parameters
        ----------
        medium_id : `int` or `str`
        phase_type : `str` optional
        component_name : `str` optional
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
            medium = None
            for entry in self.media.findall("./medium"):
                if entry.get("id") == args["medium_id"]:
                    medium = entry
            if medium is None:
                medium = self.populate_tree(
                    self.media, "medium", attr={"id": args["medium_id"]}
                )
            if "phase_type" in args:
                phases = self.get_child_tag(medium, "phases")
                if phases is None:
                    phases = self.populate_tree(medium, "phases")
                phase = self.get_child_tag_for_type(
                    phases, "phase", args["phase_type"]
                )
                if phase is None:
                    phase = self.populate_tree(phases, "phase")
                    self.populate_tree(phase, "type", text=args["phase_type"])
                    if "component_name" in args:
                        components = self.populate_tree(phase, "components")
                        component = self.populate_tree(components, "component")
                        self.populate_tree(
                            component, "name", text=args["component_name"]
                        )
                        properties = self.populate_tree(component, "properties")
                    else:
                        properties = self.populate_tree(phase, "properties")
                else:
                    if "component_name" in args:
                        components = self.get_child_tag(phase, "components")
                        if components is None:
                            components = self.populate_tree(phase, "components")
                        component = self.get_child_tag_for_type(
                            components,
                            "component",
                            args["component_name"],
                            subtag="name",
                        )
                        if component is None:
                            component = self.populate_tree(
                                components, "component"
                            )
                            self.populate_tree(
                                component, "name", text=args["component_name"]
                            )
                        properties = self.populate_tree(
                            component, "properties", overwrite=True
                        )
                    else:
                        properties = self.get_child_tag(phase, "properties")
            else:
                properties = self.get_child_tag(medium, "properties")
                if properties is None:
                    properties = self.populate_tree(medium, "properties")
                phase = medium
            property_ = self.populate_tree(properties, "property")
            base_property_param = ["name", "type"]
            for param in base_property_param:
                self.populate_tree(property_, param, text=args[param])
            try:
                if args["type"] == "Linear":
                    self._generate_linear_property(property_, args)
                elif args["type"] == "Exponential":
                    self._generate_exponential_property(property_, args)
                elif args["type"] == "Function":
                    self._generate_function_property(property_, args)
                else:
                    self._generate_generic_property(property_, args)
            except KeyError:
                print("Material property parameters incomplete for")
                if "phase_type" in args:
                    print(
                        f"Medium {args['medium_id']}->{args['phase_type']}->{args['name']}[{args['type']}]"
                    )
                else:
                    print(
                        f"Medium {args['medium_id']}->{args['name']}[{args['type']}]"
                    )
