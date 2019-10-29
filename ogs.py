# -*- coding: utf-8 -*-
import os
import sys
from lxml import etree as ET
from classes import *


class OGS(object):
    def __init__(self, **args):
        self.geo = geo.GEO()
        self.mesh = mesh.MESH()
        self.processes = processes.PROCESSES()
        self.media = media.MEDIA()
        self.timeloop = timeloop.TIMELOOP()
        self.parameters = parameters.PARAMETERS()
        self.processvars = processvars.PROCESSVARS()
        self.linsolvers = linsolvers.LINSOLVERS()
        self.nonlinsolvers = nonlinsolvers.NONLINSOLVERS()
        sys.setrecursionlimit(10000)
        self.tag = []
        ogs_name = ""
        if "PROJECT_FILE" in args:
            self.prjfile = args['PROJECT_FILE']
        else:
            print("PROJECT_FILE not given. Calling it default.prj.")
            self.prjfile = "default.prj"

    def runModel(self, **args):
        if sys.platform == "win32":
            self.ogs_name = "ogs.exe"
        else:
            self.ogs_name = "ogs"
        cmd = self.ogs_name + " " + self.prjfile + " >out"
        print("OGS running...")
        os.system(cmd)
        print("OGS finished")

    def dict2xml(self, parent, dictionary):
        for entry in dictionary:
            self.tag.append(ET.SubElement(parent, dictionary[entry]['tag']))
            self.tag[-1].text = dictionary[entry]['text']
            for attr in dictionary[entry]['attr']:
                self.tag[-1].set(attr, dictionary[entry]['attr'][attr])
            if len(dictionary[entry]['children']) > 0:
                self.dict2xml(self.tag[-1], dictionary[entry]['children'])

    def writeInput(self):
        self.root = ET.Element("OpenGeoSysProject")
        self.dict2xml(self.root, self.geo.tree)
        self.dict2xml(self.root, self.mesh.tree)
        self.dict2xml(self.root, self.processes.tree)
        self.dict2xml(self.root, self.media.tree)
        self.dict2xml(self.root, self.timeloop.tree)
        self.dict2xml(self.root, self.parameters.tree)
        self.dict2xml(self.root, self.processvars.tree)
        self.dict2xml(self.root, self.nonlinsolvers.tree)
        self.dict2xml(self.root, self.linsolvers.tree)
        # Reparsing for pretty_print to work properly
        parser = ET.XMLParser(remove_blank_text=True)
        self.tree_string = ET.tostring(self.root, pretty_print=True)
        self.tree = ET.fromstring(self.tree_string, parser=parser)
        self.tree_ = ET.ElementTree(self.tree)
        self.tree_.write(self.prjfile,
                         encoding="ISO-8859-1",
                         xml_declaration=True,
                         pretty_print=True)
        return True


if __name__ == '__main__':

    model = OGS(PROJECT_FILE="test.prj")
    model.geo.addGeom(filename="square_1x1.gml")
    model.mesh.addMesh(filename="square_1x1.vtu")
    model.mesh.addMesh(filename="square_1x1-2.vtu")
    model.mesh.addMesh(filename="quarter_002_2nd.vtu",
                       axially_symmetric="true")
    model.processes.setProcess(
        name="THM",
        type="THERMO_HYDRO_MECHANICS",
        integration_order="4",
        dimension="2",
        intrinsic_permeability="k",
        specific_storage="S",
        biot_coefficient="alpha",
        porosity="phi",
        solid_density="rho_sr",
        fluid_density="rho_fr",
        fluid_viscosity="mu",
        fluid_volumetric_thermal_expansion_coefficient="beta_f",
        solid_linear_thermal_expansion_coefficient="alpha_s",
        solid_specific_heat_capacity="C_s",
        solid_thermal_conductivity="lambda_s",
        fluid_specific_heat_capacity="C_f",
        fluid_thermal_conductivity="lambda_f",
        reference_temperature="T0",
        specific_body_force="0 0")
    model.processes.setConstitutiveRelation(type="LinearElasticIsotropic",
                                            youngs_modulus="E",
                                            poissons_ratio="nu")
    model.processes.addProcessVariable(process_variable="displacement",
                                       process_variable_name="displacement")
    model.processes.addProcessVariable(process_variable="pressure",
                                       process_variable_name="pressure")
    model.processes.addProcessVariable(process_variable="temperature",
                                       process_variable_name="temperature")
    model.processes.addProcessVariable(secondary_variable="sigma",
                                       type="static",
                                       output_name="sigma")
    model.processes.addProcessVariable(secondary_variable="epsilon",
                                       type="static",
                                       output_name="epsilon")
    model.media.addProperty(medium_id="0",
                            phase_type="AqueousLiquid",
                            name="specific_heat_capacity",
                            type="Constant",
                            value="4280.0")
    model.media.addProperty(medium_id="0",
                            phase_type="AqueousLiquid",
                            name="thermal_conductivity",
                            type="Constant",
                            value="0.6")
    model.media.addProperty(medium_id="0",
                            phase_type="Solid",
                            name="permeability",
                            type="Constant",
                            value="2e-20 0 0 2e-20")
    model.timeloop.addProcess(process="THERMO_HYDRO_MECHANICS",
                              nonlinear_solver_name="basic_newton",
                              convergence_type="PerComponentDeltaX",
                              norm_type="NORM2",
                              abstols="1e-5 1e-5 1e-5 1e-5",
                              time_discretization="BackwardEuler")
    model.timeloop.setStepping(process="THERMO_HYDRO_MECHANICS",
                               type="FixedTimeStepping",
                               t_initial="0",
                               t_end="50000",
                               repeat="10",
                               delta_t="5000")
    model.timeloop.addOutput(type="VTK",
                             prefix="blubb",
                             repeat="1",
                             each_steps="10",
                             variables=[
                                 "displacement", "pressure", "temperature",
                                 "sigma", "epsilon"
                             ])
    model.timeloop.addTimeSteppingPair(process="THERMO_HYDRO_MECHANICS",
                                       repeat="15",
                                       delta_t="32")
    model.timeloop.addOutputPair(repeat="12", each_steps="11")
    model.parameters.addParameter(name="displacement0",
                                  type="Constant",
                                  values="0 0")
    model.parameters.addParameter(name="T0", type="Constant", value="273.15")
    model.parameters.addParameter(name="C_s", type="Constant", value="917.654")
    model.processvars.setIC(process_variable_name="displacement",
                            components="2",
                            order="2",
                            initial_condition="displacement0")
    model.processvars.addBC(process_variable_name="displacement",
                            geometrical_set="square_1x1_geometry",
                            geometry="left",
                            type="Dirichlet",
                            component="0",
                            parameter="dirichlet0")
    model.processvars.addBC(process_variable_name="displacement",
                            geometrical_set="square_1x1_geometry",
                            geometry="bottom",
                            type="Dirichlet",
                            component="1",
                            parameter="dirichlet0")
    model.processvars.setIC(process_variable_name="pressure",
                            components="1",
                            order="1",
                            initial_condition="pressure_ic")
    model.processvars.addBC(process_variable_name="pressure",
                            geometrical_set="square_1x1_geometry",
                            geometry="out",
                            type="Dirichlet",
                            component="0",
                            parameter="pressure_bc_left")
    model.processvars.setIC(process_variable_name="temperature",
                            components="1",
                            order="1",
                            initial_condition="temperature_ic")
    model.processvars.addBC(process_variable_name="temperature",
                            geometrical_set="square_1x1_geometry",
                            geometry="out",
                            type="Dirichlet",
                            component="0",
                            parameter="temperature_bc_left")
    model.processvars.addST(process_variable_name="temperature",
                            geometrical_set="square_1x1_geometry",
                            geometry="center",
                            type="Nodal",
                            parameter="temperature_source_term")
    model.nonlinsolvers.addNonlinSolver(name="basic_newton",
                                        type="Newton",
                                        max_iter="4",
                                        linear_solver="general_linear_solver")
    model.linsolvers.addLinSolver(name="general_linear_solver",
                                  kind="lis",
                                  solver_type="cg",
                                  precon_type="jacobi",
                                  max_iteration_step="10000",
                                  error_tolerance="1e-16")
    model.linsolvers.addLinSolver(name="general_linear_solver",
                                  kind="eigen",
                                  solver_type="CG",
                                  precon_type="Diagonal",
                                  max_iteration_step="10000",
                                  error_tolerance="1e-16")
    model.linsolvers.addLinSolver(name="general_linear_solver",
                                  kind="petsc",
                                  solver_type="cg",
                                  precon_type="bjacobi",
                                  max_iteration_step="10000",
                                  error_tolerance="1e-16")
    model.writeInput()
