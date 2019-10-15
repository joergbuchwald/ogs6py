# -*- coding: utf-8 -*-
import os
import sys
from lxml import etree as ET
from classes import *
import numpy as np


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

    def dict2xml(self,parent,dictionary):
        for entry in dictionary:
            tag = ET.SubElement(parent, dictionary[entry]['tag'])
            tag.text = dictionary[entry]['text']
            for attr in dictionary[entry]['attr']:
                tag.set(attr,dictionary[entry]['attr'][attr])
            if len(dictionary[entry]['children']) >0:
                self.dict2xml(tag,dictionary[entry]['children'])
    def writeInput_ng(self):
        root = ET.Element("OpenGeoSysProject")
        self.dict2xml(root,self.geo.tree)
        self.dict2xml(root,self.mesh.tree)
        self.dict2xml(root,self.processes.tree)
        self.dict2xml(root,self.media.tree)
        tree = ET.ElementTree(root)
        tree.write(self.prjfile,
                   encoding="ISO-8859-1",
                   xml_declaration=True,
                   pretty_print=True)
        return True
    def writeInput(self):
        root = ET.Element("OpenGeoSysProject")
        geometry = ET.SubElement(root, "geometry")
        geometry.text = self.geo.geomfile
        if len(self.mesh.meshfiles) > 1:
            meshes = ET.SubElement(root, "meshes")
            mesh = []
            for i in np.arange(0, len(self.mesh.meshfiles)):
                mesh.append(ET.SubElement(meshes, "mesh"))
                mesh[i].text = self.mesh.meshfiles[i]
                if self.mesh.axially_symmetric[i] == "true":
                    mesh[i].set("axially_symmetric", "true")
        else:
            mesh = ET.SubElement(root, "mesh")
            mesh.text = self.mesh.meshfiles[0]
            if self.mesh.axially_symmetric[0] == "true":
                mesh.set("axially_symmetric", "true")
        processes = ET.SubElement(root, "processes")
        process = ET.SubElement(processes, "process")
        process_name = ET.SubElement(process, "name")
        process_name.text = self.processes.process[1, 0]
        process_type = ET.SubElement(process, "type")
        process_type.text = self.processes.process[1, 1]
        process_integration_order = ET.SubElement(process, "integration_order")
        process_integration_order.text = self.processes.process[1, 2]
        if self.processes.process[1, 1] == "SMALL_DEFORMATION":
            solid_density = ET.SubElement(process, "solid_density")
            solid_density.text = self.processes.SM_param[1, 1]
            reference_temperature = ET.SubElement(process,
                                                  "reference_temperature")
            reference_temperature.text = self.processes.SM_param[1, 0]
            specific_body_force = ET.SubElement(process, "specific_body_force")
            specific_body_force.text = self.processes.SM_param[1, 2]
        if self.processes.process[1, 1] == "GROUNDWATER_FLOW":
            hydraulic_conductivity = ET.SubElement(process,
                                                   "hydraulic_conductivity")
            hydraulic_conductivity.text = self.processes.GW_param[1, 0]
        if self.processes.process[1, 1] == "THERMO_HYDRO_MECHANICS":
            if len(self.processes.THM_param) > 0:
                thm_tag = []
                k = 0
                for i in self.processes.THM_param:
                    thm_tag.append(ET.SubElement(process, i))
                    thm_tag[k].text = self.processes.THM_param[i]
                    k = k + 1
        if len(self.processes.constitutive_relation) > 0:
            const_rel = ET.SubElement(process, "constitutive_relation")
            tag = []
            k = 0
            for i in self.processes.constitutive_relation:
                tag.append(ET.SubElement(const_rel, i))
                tag[k].text = self.processes.constitutive_relation[i]
                k = k + 1
        processvars = ET.SubElement(process, "process_variables")
        processvar = []
        for i in np.arange(1, len(self.processes.primary_variables)):
            processvar.append(
                ET.SubElement(processvars,
                              self.processes.primary_variables[i, 0]))
            processvar[i - 1].text = self.processes.primary_variables[i, 1]
        secondaryvars = ET.SubElement(process, "secondary_variables")
        secondaryvar = []
        for i in np.arange(1, len(self.processes.secondary_variables[:, 0])):
            secondaryvar.append(
                ET.SubElement(secondaryvars, "secondary_variable"))
            secondaryvar[i - 1].set("type",
                                    self.processes.secondary_variables[i, 0])
            secondaryvar[i - 1].set("internal_name",
                                    self.processes.secondary_variables[i, 1])
            secondaryvar[i - 1].set("output_name",
                                    self.processes.secondary_variables[i, 2])
        timeloop = ET.SubElement(root, "time_loop")
        tl_processes = ET.SubElement(timeloop, "processes")
        tl_process = ET.SubElement(tl_processes, "process")
        tl_process.set("ref", self.processes.process[1, 0])
        tl_process_nonlinsolver = ET.SubElement(tl_process, "nonlinear_solver")
        tl_process_nonlinsolver.text = self.timeloop.nonlinear_solver
        tl_process_conv_crit = ET.SubElement(tl_process,
                                             "convergence_criterion")
        tl_process_conv_crit_type = ET.SubElement(tl_process_conv_crit, "type")
        tl_process_conv_crit_type.text = self.timeloop.convergence_type
        if self.timeloop.convergence_type == "DeltaX":
            tl_process_conv_crit_norm = ET.SubElement(tl_process_conv_crit,
                                                      "norm_type")
            tl_process_conv_crit_norm.text = self.timeloop.norm_type
            if self.timeloop.abstol != "":
                tl_process_conv_crit_abstol = ET.SubElement(
                    tl_process_conv_crit, "abstol")
                tl_process_conv_crit_abstol.text = self.timeloop.abstol
            if self.timeloop.reltol != "":
                tl_process_conv_crit_reltol = ET.SubElement(
                    tl_process_conv_crit, "reltol")
                tl_process_conv_crit_reltol.text = self.timeloop.reltol
        if self.timeloop.convergence_type == "PerComponentDeltaX":
            tl_process_conv_crit_norm = ET.SubElement(tl_process_conv_crit,
                                                      "norm_type")
            tl_process_conv_crit_norm.text = self.timeloop.norm_type
            if self.timeloop.abstol != "":
                tl_process_conv_crit_abstol = ET.SubElement(
                    tl_process_conv_crit, "abstols")
                tl_process_conv_crit_abstol.text = self.timeloop.abstol
            if self.timeloop.reltol != "":
                tl_process_conv_crit_reltol = ET.SubElement(
                    tl_process_conv_crit, "reltols")
                tl.process_conv_crit_reltol.text = self.timeloop.reltol
        tl_process_td = ET.SubElement(tl_process, "time_discretization")
        tl_process_tdtype = ET.SubElement(tl_process_td, "type")
        tl_process_tdtype.text = self.timeloop.time_discretization
        tl_process_ts = ET.SubElement(tl_process, "time_stepping")
        tl_process_ts_type = ET.SubElement(tl_process_ts, "type")
        tl_process_ts_type.text = self.timeloop.time_stepping
        tl_process_ts_initial = ET.SubElement(tl_process_ts, "t_initial")
        tl_process_ts_initial.text = self.timeloop.t_initial
        tl_process_ts_end = ET.SubElement(tl_process_ts, "t_end")
        tl_process_ts_end.text = self.timeloop.t_end
        tl_process_ts_ts = ET.SubElement(tl_process_ts, "timesteps")
        tl_process_ts_ts_pair = []
        tl_process_ts_ts_pair_repeat = []
        tl_process_ts_ts_pair_deltat = []
        for i in np.arange(0, len(self.timeloop.t_repeat)):
            tl_process_ts_ts_pair.append(
                ET.SubElement(tl_process_ts_ts, "pair"))
            tl_process_ts_ts_pair_repeat.append(
                ET.SubElement(tl_process_ts_ts_pair[i], "repeat"))
            tl_process_ts_ts_pair_repeat[i].text = self.timeloop.t_repeat[i]
            tl_process_ts_ts_pair_deltat.append(
                ET.SubElement(tl_process_ts_ts_pair[i], "delta_t"))
            tl_process_ts_ts_pair_deltat[i].text = self.timeloop.t_deltat[i]
        tl_output = ET.SubElement(timeloop, "output")
        tl_output_type = ET.SubElement(tl_output, "type")
        tl_output_type.text = self.timeloop.outputtype
        tl_output_prefix = ET.SubElement(tl_output, "prefix")
        tl_output_prefix.text = self.timeloop.outputprefix
        tl_output_ts_pair = []
        tl_output_ts_repeat = []
        tl_output_ts_each_steps = []
        if len(self.timeloop.output_repeat) > 0:
            tl_output_timesteps = ET.SubElement(tl_output, "timesteps")
            for i in np.arange(0, len(self.timeloop.output_repeat)):
                tl_output_ts_pair.append(
                    ET.SubElement(tl_output_timesteps, "pair"))
                tl_output_ts_repeat.append(
                    ET.SubElement(tl_output_ts_pair[i], "repeat"))
                tl_output_ts_repeat[i].text = self.timeloop.output_repeat[i]
                tl_output_ts_each_steps.append(
                    ET.SubElement(tl_output_ts_pair[i], "each_steps"))
                tl_output_ts_each_steps[i].text \
                        = self.timeloop.output_each_steps[i]
        tl_output_variables = ET.SubElement(tl_output, "variables")
        tl_output_variable = []
        for i in np.arange(0, len(self.timeloop.outputvariables)):
            tl_output_variable.append(
                ET.SubElement(tl_output_variables, "variable"))
            tl_output_variable[i].text = self.timeloop.outputvariables[i]
        parameters = ET.SubElement(root, "parameters")
        parameter = []
        para_name = []
        para_type = []
        para_mesh = []
        para_value = []
        for i in np.arange(0, len(self.parameters.parameters) - 1):
            parameter.append(ET.SubElement(parameters, "parameter"))
            para_name.append(ET.SubElement(parameter[i], "name"))
            para_name[i].text = self.parameters.parameters[i + 1, 0]
            para_type.append(ET.SubElement(parameter[i], "type"))
            para_type[i].text = self.parameters.parameters[i + 1, 1]
            if self.parameters.parameters[i + 1, 1] == "Constant":
                if len(self.parameters.parameters[i + 1, 2].split()) > 1:
                    para_value.append(ET.SubElement(parameter[i], "values"))
                else:
                    para_value.append(ET.SubElement(parameter[i], "value"))
                para_value[i].text = self.parameters.parameters[i + 1, 2]
            if self.parameters.parameters[i + 1, 3] != '':
                para_mesh.append(ET.SubElement(parameter[i], "mesh"))
                para_mesh.text = self.parameters.parameters[i + 1, 3]
            if self.parameters.parameters[i + 1, 1] == "MeshElement" \
                    or self.parameters.parameters[i + 1, 1] == "MeshNode":
                para_value.append(ET.SubElement(parameter[i], "field_name"))
                para_value[i].text = self.parameters.parameters[i + 1, 4]
            if self.parameters.parameters[i + 1, 1] == "Function":
                para_value.append(ET.SubElement(parameter[i], "expression"))
                para_value[i].text = self.parameters.parameters[i + 1, 5]
        procvars = ET.SubElement(root, "process_variables")
        procvar = []
        procvar_name = []
        procvar_components = []
        procvar_order = []
        procvar_ic = []
        procvar_bcs = []
        procvar_bc = []
        procvar_bc_geomset = []
        procvar_bc_geometry = []
        procvar_bc_type = []
        procvar_bc_mesh = []
        procvar_bc_component = []
        procvar_bc_param = []
        procvar_bc_bcobject = []
        procvar_sts = []
        procvar_st = []
        procvar_st_geomset = []
        procvar_st_geometry = []
        procvar_st_type = []
        procvar_st_mesh = []
        procvar_st_component = []
        procvar_st_param = []
        procvar_st_stobject = []
        #        print("initial conditions:", self.processvars.initial_conditions)
        #        print("boundary conditions:", self.processvars.boundary_conditions)
        #        print("Source Terms:",self.processvars.source_terms)
        for i in np.arange(0, len(self.processes.primary_variables[:, 0]) - 1):
            procvar.append(ET.SubElement(procvars, "process_variable"))
            procvar_name.append(ET.SubElement(procvar[i], "name"))
            procvar_name[i].text = self.processes.primary_variables[i + 1, 1]
            procvar_order.append(ET.SubElement(procvar[i], "order"))
            procvar_components.append(ET.SubElement(procvar[i], "components"))
            procvar_ic.append(ET.SubElement(procvar[i], "initial_condition"))
            for j in np.arange(
                    0,
                    len(self.processvars.initial_conditions[:, 0]) - 1):
                if self.processvars.initial_conditions[j + 1, 0] \
                        == self.processes.primary_variables[i + 1, 1]:
                    procvar_order[i].text \
                            = self.processvars.initial_conditions[j + 1, 2]
                    procvar_components[i].text \
                            = self.processvars.initial_conditions[j + 1, 1]
                    procvar_ic[i].text \
                            = self.processvars.initial_conditions[j + 1, 3]
            procvar_bcs.append(ET.SubElement(procvar[i],
                                             "boundary_conditions"))
            procvar_bc.append('')
            procvar_bc_geomset.append('')
            procvar_bc_geometry.append('')
            procvar_bc_type.append('')
            procvar_bc_mesh.append('')
            procvar_bc_component.append('')
            procvar_bc_param.append('')
            procvar_bc_bcobject.append('')
            procvar_bc[i] = []
            procvar_bc_geomset[i] = []
            procvar_bc_geometry[i] = []
            procvar_bc_type[i] = []
            procvar_bc_mesh[i] = []
            procvar_bc_component[i] = []
            procvar_bc_param[i] = []
            procvar_bc_bcobject[i] = []
            for j in np.arange(
                    0,
                    len(self.processvars.boundary_conditions[:, 0]) - 1):
                if self.processvars.boundary_conditions[j + 1, 0] \
                        == self.processes.primary_variables[i + 1, 1]:
                    procvar_bc[i].append(
                        ET.SubElement(procvar_bcs[i], "boundary_condition"))
                    q = len(procvar_bc[i]) - 1
                    if not self.processvars.boundary_conditions[j +
                                                                1, 1] == "":
                        procvar_bc_geomset[i].append(
                            ET.SubElement(procvar_bc[i][q], "geometrical_set"))
                        procvar_bc_geomset[i][q].text \
                                = self.processvars.boundary_conditions[j + 1, 1]
                        procvar_bc_geometry[i].append(
                            ET.SubElement(procvar_bc[i][q], "geometry"))
                        procvar_bc_geometry[i][q].text \
                                = self.processvars.boundary_conditions[j + 1, 2]
                        procvar_bc_mesh[i].append('')
                    else:
                        procvar_bc_geomset[i].append('')
                        procvar_bc_geometry[i].append('')
                        procvar_bc_mesh[i].append(
                            ET.SubElement(procvar_bc[i][q], "mesh"))
                        procvar_bc_mesh[i][q].text \
                                = self.processvars.boundary_conditions[j + 1, 3]
                    procvar_bc_type[i].append(
                        ET.SubElement(procvar_bc[i][q], "type"))
                    procvar_bc_type[i][q].text \
                            = self.processvars.boundary_conditions[j + 1, 4]
                    if not self.processvars.boundary_conditions[j +
                                                                1, 5] == "":
                        procvar_bc_component[i].append(
                            ET.SubElement(procvar_bc[i][q], "component"))
                        procvar_bc_component[i][q].text \
                                = self.processvars.boundary_conditions[j + 1, 5]
                    else:
                        procvar_bc_component[i].append('')
                    if not self.processvars.boundary_conditions[j +
                                                                1, 6] == "":
                        procvar_bc_param[i].append(
                            ET.SubElement(procvar_bc[i][q], "parameter"))
                        procvar_bc_param[i][q].text \
                                = self.processvars.boundary_conditions[j + 1, 6]
                        procvar_bc_bcobject[i].append('')
                    else:
                        procvar_bc_param[i].append('')
                        procvar_bc_bcobject[i].append(
                            ET.SubElement(procvar_bc[i][q], "bc_object"))
                        procvar_bc_bcobject[i][q].text \
                                = self.processvars.boundary_conditions[j + 1, 7]
            procvar_sts.append('')
            procvar_st.append('')
            procvar_st_geomset.append('')
            procvar_st_geometry.append('')
            procvar_st_type.append('')
            procvar_st_mesh.append('')
            procvar_st_component.append('')
            procvar_st_param.append('')
            procvar_st_stobject.append('')
            procvar_st[i] = []
            procvar_st_geomset[i] = []
            procvar_st_geometry[i] = []
            procvar_st_type[i] = []
            procvar_st_mesh[i] = []
            procvar_st_component[i] = []
            procvar_st_param[i] = []
            procvar_st_stobject[i] = []
            for j in np.arange(0,
                               len(self.processvars.source_terms[:, 0]) - 1):
                if self.processvars.source_terms[j + 1, 0] \
                        == self.processes.primary_variables[i + 1, 1]:
                    if procvar_sts[i] == '':
                        procvar_sts[i] = ET.SubElement(procvar[i],
                                                       "source_terms")
                    procvar_st[i].append(
                        ET.SubElement(procvar_sts[i], "source_term"))
                    q = len(procvar_st[i]) - 1
                    if not self.processvars.source_terms[j + 1, 1] == "":
                        procvar_st_geomset[i].append(
                            ET.SubElement(procvar_st[i][q], "geometrical_set"))
                        procvar_st_geomset[i][q].text \
                                = self.processvars.source_terms[j + 1, 1]
                        procvar_st_geometry[i].append(
                            ET.SubElement(procvar_st[i][q], "geometry"))
                        procvar_st_geometry[i][q].text \
                                = self.processvars.source_terms[j + 1, 2]
                        procvar_st_mesh[i].append('')
                    else:
                        procvar_st_geomset[i].append('')
                        procvar_st_geometry[i].append('')
                        procvar_st_mesh[i].append(
                            ET.SubElement(procvar_st[i][q], "mesh"))
                        procvar_st_mesh[i][q].text \
                                = self.processvars.source_terms[j + 1, 3]
                    procvar_st_type[i].append(
                        ET.SubElement(procvar_st[i][q], "type"))
                    procvar_st_type[i][q].text \
                            = self.processvars.source_terms[j + 1, 4]
                    if not self.processvars.source_terms[j + 1, 5] == "":
                        procvar_st_component[i].append(
                            ET.SubElement(procvar_st[i][q], "component"))
                        procvar_st_component[i][q].text \
                                = self.processvars.source_terms[j + 1, 5]
                    else:
                        procvar_st_component[i].append('')
                    if not self.processvars.source_terms[j + 1, 6] == "":
                        procvar_st_param[i].append(
                            ET.SubElement(procvar_st[i][q], "parameter"))
                        procvar_st_param[i][q].text \
                                = self.processvars.source_terms[j + 1, 6]
                        procvar_st_stobject[i].append('')
                    else:
                        procvar_st_param[i].append('')
                        procvar_st_stobject[i].append(
                            ET.SubElement(procvar_st[i][q],
                                          "source_term_object"))
                        procvar_st_stobject[i][q].text \
                                = self.processvars.source_terms[j + 1, 7]

        nonlinsolvers = ET.SubElement(root, "nonlinear_solvers")
        nonlinsolver = []
        nonlinsolvername = []
        nonlinsolvertype = []
        nonlinsolveriter = []
        nonlinsolverlin = []
        nonlinsolverdamp = []
        for i in np.arange(0,
                           len(self.nonlinsolvers.nonlin_solvers[:, 0]) - 1):
            nonlinsolver.append(
                ET.SubElement(nonlinsolvers, "nonlinear_solver"))
            nonlinsolvername.append(ET.SubElement(nonlinsolver[i], "name"))
            nonlinsolvername[i].text \
                    = self.nonlinsolvers.nonlin_solvers[i + 1, 0]
            nonlinsolvertype.append(ET.SubElement(nonlinsolver[i], "type"))
            nonlinsolvertype[i].text \
                    = self.nonlinsolvers.nonlin_solvers[i + 1, 1]
            nonlinsolveriter.append(ET.SubElement(nonlinsolver[i], "max_iter"))
            nonlinsolveriter[i].text \
                    = self.nonlinsolvers.nonlin_solvers[i + 1, 2]
            nonlinsolverlin.append(
                ET.SubElement(nonlinsolver[i], "linear_solver"))
            nonlinsolverlin[i].text \
                    = self.nonlinsolvers.nonlin_solvers[i + 1, 3]
            if not self.nonlinsolvers.nonlin_solvers[i + 1, 4] == "":
                nonlinsolverdamp.append(
                    ET.SubElement(nonlinsolver[i], "damping"))
                nonlinsolverdamp[i].text \
                        = self.nonlinsolvers.nonlin_solvers[i + 1, 4]
            else:
                nonlinsolverdamp.append('')
        linsolvers = ET.SubElement(root, "linear_solvers")
        linsolver = ET.SubElement(linsolvers, "linear_solver")
        linsolvername = ET.SubElement(linsolver, "name")
        linsolvername.text = self.linsolvers.lin_solver_name
        for i in np.arange(0, len(self.linsolvers.lin_solvers[:, 0]) - 1):
            if self.linsolvers.lin_solvers[i + 1, 0] == "lis":
                lis = ET.SubElement(linsolver, "lis")
                lis.text = "-i " + self.linsolvers.lin_solvers[i + 1, 1] \
                        + " -p " + self.linsolvers.lin_solvers[i + 1, 2] \
                        + " -tol " + self.linsolvers.lin_solvers[i + 1, 4] \
                        + " -maxiter " + self.linsolvers.lin_solvers[i + 1, 3]
            if self.linsolvers.lin_solvers[i + 1, 0] == "eigen":
                eigen = ET.SubElement(linsolver, "eigen")
                eigentype = ET.SubElement(eigen, "solver_type")
                eigentype.text = self.linsolvers.lin_solvers[i + 1, 1]
                eigenprecon = ET.SubElement(eigen, "precon_type")
                eigenprecon.text = self.linsolvers.lin_solvers[i + 1, 2]
                eigenit = ET.SubElement(eigen, "max_iteration_step")
                eigenit.text = self.linsolvers.lin_solvers[i + 1, 3]
                eigentol = ET.SubElement(eigen, "error_tolerance")
                eigentol.text = self.linsolvers.lin_solvers[i + 1, 4]
                if self.linsolvers.lin_solvers[i + 1, 5] == "0":
                    pass
                else:
                    eigenscaling = ET.SubElement(eigen, "scaling")
                    eigenscaling.text = "1"
            if self.linsolvers.lin_solvers[i + 1, 0] == "petsc":
                petsc = ET.SubElement(linsolver, "petsc")
                petscparam = ET.SubElement(petsc, "parameters")
                petscparam.text = "-ksp_type " \
                        + self.linsolvers.lin_solvers[i + 1, 1] \
                        + " -pc_type " \
                        + self.linsolvers.lin_solvers[i + 1, 2] \
                        + " -ksp_rtol " \
                        + self.linsolvers.lin_solvers[i + 1, 4] \
                        + " -ksp_max_it " \
                        + self.linsolvers.lin_solvers[i + 1, 3]

        tree = ET.ElementTree(root)
        tree.write(self.prjfile,
                   encoding="ISO-8859-1",
                   xml_declaration=True,
                   pretty_print=True)
        return True
if __name__ == '__main__':
    model = OGS(PROJECT_FILE="test.prj")
    model.geo.addGeom(filename="square_1x1.gml")
    model.mesh.addMesh(filename="square_1x1.vtu")
    model.mesh.addMesh(filename="square_1x1-2.vtu")
    model.mesh.addMesh(filename="quarter_002_2nd.vtu", axially_symmetric="true")
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
    model.processes.addProcessVariable(
            process_variable="displacement",
            process_variable_name="displacement")
    model.processes.addProcessVariable(
            process_variable="pressure",
            process_variable_name="pressure")
    model.processes.addProcessVariable(
            process_variable="temperature",
            process_variable_name="temperature")
    model.processes.addProcessVariable(secondary_variable="sigma",
                                   type="static",
                                   output_name="sigma")
    model.processes.addProcessVariable(secondary_variable="epsilon",
                                   type="static",
                                   output_name="epsilon")
    model.media.addProperty(medium_id="0", phase_type="AqueousLiquid", name="specific_heat_capacity", type="Constant", value="4280.0")
    model.media.addProperty(medium_id="0", phase_type="AqueousLiquid", name="thermal_conductivity", type="Constant", value="0.6")
    model.media.addProperty(medium_id="0", phase_type="Solid", name="permeability", type="Constant", value="2e-20 0 0 2e-20")
    model.writeInput_ng()
