import unittest

import pandas as pd

import tempfile
import os
import shutil
import hashlib
from lxml import etree as ET

from context import ogs6py
from ogs6py.log_parser.log_parser import parse_file
# this needs to be replaced with regexes from specific ogs version
from collections import namedtuple, defaultdict
from ogs6py.log_parser.common_ogs_analyses import fill_ogs_context, analysis_time_step, \
    analysis_convergence_newton_iteration, analysis_convergence_coupling_iteration, analysis_simulation_termination, \
    time_step_vs_iterations


def log_types(records):
    d = defaultdict(list)
    for record in records:
        d[type(record)].append(record)
    return d

class TestiOGS(unittest.TestCase):

    def test_buildfromscratch(self):
        model = ogs6py.OGS(PROJECT_FILE="tunnel_ogs6py.prj", MKL=True, OMP_NUM_THREADS=4)
        model.mesh.add_mesh(filename="tunnel.vtu")
        model.mesh.add_mesh(filename="tunnel_left.vtu")
        model.mesh.add_mesh(filename="tunnel_right.vtu")
        model.mesh.add_mesh(filename="tunnel_bottom.vtu")
        model.mesh.add_mesh(filename="tunnel_top.vtu")
        model.mesh.add_mesh(filename="tunnel_inner.vtu")
        model.processes.set_process(
            name="THERMO_RICHARDS_MECHANICS",
            type="THERMO_RICHARDS_MECHANICS",
            integration_order="3",
            specific_body_force="0 0",
            initial_stress="Initial_stress")
        model.processes.set_constitutive_relation(type="LinearElasticIsotropic",
                                                youngs_modulus="E",
                                                poissons_ratio="nu")
        model.processes.add_process_variable(process_variable="displacement",
                                        process_variable_name="displacement")
        model.processes.add_process_variable(process_variable="pressure",
                                        process_variable_name="pressure")
        model.processes.add_process_variable(process_variable="temperature",
                                        process_variable_name="temperature")
        model.processes.add_process_variable(secondary_variable="sigma",
                                        output_name="sigma")
        model.processes.add_process_variable(secondary_variable="epsilon",
                                        output_name="epsilon")
        model.processes.add_process_variable(secondary_variable="velocity",
                                        output_name="velocity")
        model.processes.add_process_variable(secondary_variable="saturation",
                                        output_name="saturation")

        model.media.add_property(medium_id="0",
                                phase_type="AqueousLiquid",
                                name="specific_heat_capacity",
                                type="Constant",
                                value="4280.0")
        model.media.add_property(medium_id="0",
                                phase_type="AqueousLiquid",
                                name="thermal_conductivity",
                                type="Constant",
                                value="0.6")
        model.media.add_property(medium_id="0",
                                phase_type="AqueousLiquid",
                                name="density",
                                type="Linear",
                                reference_value="999.1",
                                variable_name="phase_pressure",
                                reference_condition="1e5",
                                slope="4.5999999999999996e-10")
        model.media.add_property(medium_id="0",
                                phase_type="AqueousLiquid",
                                name="thermal_expansivity",
                                type="Constant",
                                value="3.98e-4")
        model.media.add_property(medium_id="0",
                                phase_type="AqueousLiquid",
                                name="viscosity",
                                type="Constant",
                                value="1.e-3")
        model.media.add_property(medium_id="0",
                                name="permeability",
                                type="Constant",
                                value="1e-17")
        model.media.add_property(medium_id="0",
                                name="porosity",
                                type="Constant",
                                value="0.15")
        model.media.add_property(medium_id="0",
                                phase_type="Solid",
                                name="density",
                                type="Constant",
                                value="2300")
        model.media.add_property(medium_id="0",
                                phase_type="Solid",
                                name="thermal_conductivity",
                                type="Constant",
                                value="1.9")
        model.media.add_property(medium_id="0",
                                phase_type="Solid",
                                name="specific_heat_capacity",
                                type="Constant",
                                value="800")
        model.media.add_property(medium_id="0",
                                name="biot_coefficient",
                                type="Constant",
                                value="0.6")
        model.media.add_property(medium_id="0",
                                phase_type="Solid",
                                name="thermal_expansivity",
                                type="Constant",
                                value="1.7e-5")
        model.media.add_property(medium_id="0",
                                name="thermal_conductivity",
                                type="EffectiveThermalConductivityPorosityMixing")
        model.media.add_property(medium_id="0",
                                name="saturation",
                                type="Constant",
                                value="1")
        model.media.add_property(medium_id="0",
                                name="relative_permeability",
                                type="Constant",
                                value="1")
        model.media.add_property(medium_id="0",
                                name="bishops_effective_stress",
                                type="BishopsPowerLaw",
                                exponent="1")
        model.timeloop.add_process(process="THERMO_RICHARDS_MECHANICS",
                                nonlinear_solver_name="nonlinear_solver",
                                convergence_type="PerComponentDeltaX",
                                norm_type="NORM2",
                                abstols="1e-4 1e-4 1e-10 1e-10",
                                time_discretization="BackwardEuler")
        model.timeloop.set_stepping(process="THERMO_RICHARDS_MECHANICS",
                                type="IterationNumberBasedTimeStepping",
                                t_initial=0,
                                t_end=8,
                                initial_dt=0.1,
                                minimum_dt=1e-7,
                                maximum_dt=0.1,
                                number_iterations=[1, 4, 10, 20],
                                multiplier=[1.2, 1.0, 0.9, 0.8])
        model.timeloop.add_output(
            type="VTK",
            prefix="tunnel",
            repeat="10000",
            each_steps="1",
            variables=["displacement", "pressure", "temperature",
                    "sigma", "epsilon", "velocity", "saturation"],
            fixed_output_times=[1, 2, 3],
            suffix="_ts_{:timestep}_t_{:time}")
        model.parameters.add_parameter(name="Initial_stress", type="Function",
                                    mesh="tunnel", expression=["-5e6", "-5e6", "-5e6", "0"])
        model.parameters.add_parameter(name="E", type="Constant", value="2e9")
        model.parameters.add_parameter(name="nu", type="Constant", value="0.3")
        model.parameters.add_parameter(name="T0", type="Constant", value="273.15")
        model.parameters.add_parameter(name="displacement0",
                                    type="Constant",
                                    values="0 0")

        model.parameters.add_parameter(name="pressure_ic", type="Constant", value="1e6")
        model.parameters.add_parameter(name="dirichlet0", type="Constant", value="0")
        model.parameters.add_parameter(name="temperature_ic",
                                    type="Constant",
                                    value="293.15")
        model.parameters.add_parameter(name="pressure_bc",
                                    type="CurveScaled",
                                    curve="excavation_curve",
                                    parameter="pressure_ic")
        model.parameters.add_parameter(name="PressureLoad",
                                    type="CurveScaled",
                                    curve="excavation_curve",
                                    parameter="PressureLoadValue")
        model.parameters.add_parameter(
                                name="PressureLoadValue", type="Constant", value="-5.6e6")
        model.parameters.add_parameter(name="heat_bv",
                                    type="Constant",
                                    value="25")
        model.curves.add_curve(name="excavation_curve", coords=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
                            values=[1.0, 1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.0])
        model.processvars.set_ic(process_variable_name="temperature",
                                components="1",
                                order="1",
                                initial_condition="temperature_ic")
        model.processvars.add_bc(process_variable_name="temperature",
                                mesh="tunnel_right",
                                type="Dirichlet",
                                component="0",
                                parameter="temperature_ic")
        model.processvars.add_bc(process_variable_name="temperature",
                                mesh="tunnel_left",
                                type="Dirichlet",
                                component="0",
                                parameter="temperature_ic")
        model.processvars.add_bc(process_variable_name="temperature",
                                mesh="tunnel_bottom",
                                type="Dirichlet",
                                component="0",
                                parameter="temperature_ic")
        model.processvars.add_bc(process_variable_name="temperature",
                                mesh="tunnel_top",
                                type="Dirichlet",
                                component="0",
                                parameter="temperature_ic")

        model.processvars.set_ic(process_variable_name="displacement",
                                components="2",
                                order="1",
                                initial_condition="displacement0")
        model.processvars.add_bc(process_variable_name="displacement",
                                mesh="tunnel_right",
                                type="Dirichlet",
                                component="0",
                                parameter="dirichlet0")
        model.processvars.add_bc(process_variable_name="displacement",
                                mesh="tunnel_left",
                                type="Dirichlet",
                                component="0",
                                parameter="dirichlet0")
        model.processvars.add_bc(process_variable_name="displacement",
                                mesh="tunnel_top",
                                type="Dirichlet",
                                component="1",
                                parameter="dirichlet0")
        model.processvars.add_bc(process_variable_name="displacement",
                                mesh="tunnel_bottom",
                                type="Dirichlet",
                                component="1",
                                parameter="dirichlet0")
        model.processvars.add_bc(process_variable_name="displacement",
                                mesh="tunnel_inner",
                                type="NormalTraction",
                                parameter="PressureLoad")
        model.processvars.set_ic(process_variable_name="pressure",
                                components="1",
                                order="1",
                                initial_condition="pressure_ic")
        model.processvars.add_bc(process_variable_name="pressure",
                                mesh="tunnel_right",
                                type="Dirichlet",
                                component="0",
                                parameter="pressure_ic")
        model.processvars.add_bc(process_variable_name="pressure",
                                mesh="tunnel_left",
                                type="Dirichlet",
                                component="0",
                                parameter="pressure_ic")
        model.processvars.add_bc(process_variable_name="pressure",
                                mesh="tunnel_top",
                                type="Dirichlet",
                                component="0",
                                parameter="pressure_ic")
        model.processvars.add_bc(process_variable_name="pressure",
                                mesh="tunnel_bottom",
                                type="Dirichlet",
                                component="0",
                                parameter="pressure_ic")
        model.processvars.add_bc(process_variable_name="pressure",
                                mesh="tunnel_inner",
                                type="Dirichlet",
                                component="0",
                                parameter="pressure_bc")

        model.nonlinsolvers.add_non_lin_solver(name="nonlinear_solver",
                                            type="Newton",
                                            max_iter="50",
                                            linear_solver="general_linear_solver")
        model.linsolvers.add_lin_solver(name="general_linear_solver",
                                    kind="eigen",
                                    solver_type="PardisoLU")
        model.add_entry(parent_xpath="./linear_solvers/linear_solver/eigen", tag="scaling", text="1")
        model.add_block("parameter", parent_xpath="./parameters", taglist=["name", "type", "value"], textlist=["T1", "Constant", "300"])
        model.write_input()
        with open("tunnel_ogs6py.prj", "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        self.assertEqual(file_hash.hexdigest(), '3664e20f5ac0f151949b8aeeb9afabca')

    def test_replace_text(self):
        prjfile = "tunnel_ogs6py_replace.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.replace_text("tunnel_replace", xpath="./time_loop/output/prefix")
        model.write_input()
        root = ET.parse(prjfile)
        find = root.findall("./time_loop/output/prefix")
        self.assertEqual("tunnel_replace", find[0].text)

    def test_empty_replace(self):
        inputfile="tests/tunnel_ogs6py.prj"
        prjfile = "tunnel_ogs6py_empty_replace.prj"
        model = ogs6py.OGS(INPUT_FILE=inputfile, PROJECT_FILE=prjfile)
        model.write_input()
        with open(inputfile, "rb") as f:
            inputfile_hash = hashlib.md5()
            while chunk := f.read(8192):
                inputfile_hash.update(chunk)
        with open(prjfile, "rb") as f:
            prjfile_hash = hashlib.md5()
            while chunk := f.read(8192):
                prjfile_hash.update(chunk)
        self.assertEqual(inputfile_hash.hexdigest(), prjfile_hash.hexdigest())
    def test_replace_phase_property(self):
        prjfile = "tunnel_ogs6py_replace.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.replace_phase_property(mediumid=0, phase="Solid", name="thermal_expansivity", value=5)
        model.write_input()
        root = ET.parse(prjfile)
        find = root.findall("./media/medium/phases/phase[type='Solid']/properties/property[name='thermal_expansivity']/value")
        self.assertEqual("5", find[0].text)
    def test_replace_medium_property(self):
        prjfile = "tunnel_ogs6py_replace.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.replace_medium_property(mediumid=0, name="porosity", value=42)
        model.write_input()
        root = ET.parse(prjfile)
        find = root.findall("./media/medium/properties/property[name='porosity']/value")
        self.assertEqual("42", find[0].text)
    def test_replace_parameter(self):
        prjfile = "tunnel_ogs6py_replace.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.replace_parameter(name="E", value=32)
        model.write_input()
        root = ET.parse(prjfile)
        find = root.findall("./parameters/parameter[name='E']/value")
        self.assertEqual("32", find[0].text)
    def test_replace_mesh(self):
        prjfile = "tunnel_ogs6py_replacemesh.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.replace_mesh(oldmesh="tunnel_inner.vtu", newmesh="tunnel_inner_new.vtu")
        model.write_input()
        root = ET.parse(prjfile)
        find = root.findall("./meshes/mesh")
        self.assertEqual("tunnel_inner_new.vtu", find[-1].text)
        find = root.findall("./process_variables/process_variable/boundary_conditions/boundary_condition/mesh")
        self.assertEqual("tunnel_right", find[0].text)
        self.assertEqual("tunnel_left", find[1].text)
        self.assertEqual("tunnel_bottom", find[2].text)
        self.assertEqual("tunnel_top", find[3].text)
        self.assertEqual("tunnel_right", find[4].text)
        self.assertEqual("tunnel_left", find[5].text)
        self.assertEqual("tunnel_top", find[6].text)
        self.assertEqual("tunnel_bottom", find[7].text)
        self.assertEqual("tunnel_right", find[9].text)
        self.assertEqual("tunnel_left", find[10].text)
        self.assertEqual("tunnel_top", find[11].text)
        self.assertEqual("tunnel_bottom", find[12].text)
        self.assertEqual("tunnel_inner_new", find[8].text)
        self.assertEqual("tunnel_inner_new", find[13].text)
    def test_add_entry(self):
        prjfile = "tunnel_ogs6py_add_entry.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.add_entry(tag="geometry", parent_xpath=".", text="geometry.gml")
        model.write_input()
        root = ET.parse(prjfile)
        find = root.findall("./geometry")
        self.assertEqual("geometry.gml", find[0].text)
    def test_add_block(self):
        prjfile = "tunnel_ogs6py_add_block.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.add_block("parameter", parent_xpath="./parameters", taglist=["name", "type", "value"],
                textlist=["mu","Constant","0.001"])
        model.write_input()
        root = ET.parse(prjfile)
        find = root.findall("./parameters/parameter[name='mu']/value")
        self.assertEqual("0.001", find[0].text)
    def test_remove_element(self):
        prjfile = "tunnel_ogs6py_remove_element.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.remove_element(xpath="./parameters/parameter[name='E']")
        model.write_input()
        root = ET.parse(prjfile)
        find = root.findall("./parameters/parameter[name='E']/value")
        self.assertEqual(0, len(find))
    def test_replace_block_by_include(self):
        prjfile = "tunnel_ogs6py_solid_inc.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/tunnel_ogs6py.prj", PROJECT_FILE=prjfile)
        model.replace_block_by_include(xpath="./media/medium/phases/phase[type='Solid']", filename="solid.xml")
        model.write_input(keep_includes=True)
        with open(prjfile, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        self.assertEqual(file_hash.hexdigest(), '68ff996f4e6bfbe6fffd5e156275ac08')
        with open("solid.xml", "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        self.assertEqual(file_hash.hexdigest(), '83bd4df36ac148eff94c36da4b7fc27f')
    def test_replace_property_in_include(self):
        prjfile = "tunnel_ogs6py_includetest.prj"
        model = ogs6py.OGS(INPUT_FILE="tests/includetest.prj", PROJECT_FILE=prjfile)
        model.replace_phase_property(mediumid=0, phase="Solid", name="thermal_expansivity", value=1e-3)
        model.write_input(keep_includes=True)
        with open(prjfile, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        self.assertEqual(file_hash.hexdigest(), '4196c13e54dad2026e4f8283d7faf141')
        with open("tests/solid_inc.xml", "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        self.assertEqual(file_hash.hexdigest(), '0e80d35b207c07abb0af020d864b277b')

    def test_model_run(self):
        prjfile = "tests/tunnel_ogs6py.prj"
        # dummy *.SIF file
        sif_file = tempfile.NamedTemporaryFile(suffix=".sif")
        # dummy *.notSIF file
        x_file = tempfile.NamedTemporaryFile(suffix=".x")
        # dummy directory
        sing_dir = tempfile.TemporaryDirectory()

        # case: path is not a dir
        model = ogs6py.OGS(INPUT_FILE=prjfile, PROJECT_FILE=prjfile)
        with self.assertRaises(RuntimeError) as cm:
            model.run_model(path="not/a/dir", container_path=sif_file.name)
        self.assertEqual('The specified path is not a directory. Please provide a directory containing the Singularity executable.',
            str(cm.exception))
        # case: container_path is not a file:
        with self.assertRaises(RuntimeError) as cm:
            model.run_model(container_path="not/a/file")
        self.assertEqual('The specific container-path is not a file. Please provide a path to the OGS container.',
            str(cm.exception))
        # case: container_path is not a *.sif file
        with self.assertRaises(RuntimeError) as cm:
            model.run_model(container_path=x_file.name)
        self.assertEqual('The specific file is not a Singularity container. Please provide a *.sif file containing OGS.',
            str(cm.exception))
        # case Singularity executable not found without path
        if shutil.which(os.path.join("singularity")) is None:
            with self.assertRaises(RuntimeError) as cm:
                model.run_model(container_path=sif_file.name)
            self.assertEqual('The Singularity executable was not found. See https://www.opengeosys.org/docs/userguide/basics/container/ for installation instructions.',
                str(cm.exception))
        # case Singularity executable not found in path
        with self.assertRaises(RuntimeError) as cm:
            model.run_model(path=sing_dir.name, container_path=sif_file.name)
        self.assertEqual('The Singularity executable was not found. See https://www.opengeosys.org/docs/userguide/basics/container/ for installation instructions.',
            str(cm.exception))

        # clean up the temporary dir
        sing_dir.cleanup()

### Log parser:

    def test_parallel_1_compare_serial_info(self):
        filename_p = 'tests/parser/parallel_1_info.txt'
        # Only for MPI execution with 1 process we need to tell the log parser by force_parallel=True!
        records_p = parse_file(filename_p, force_parallel=True)
        num_of_record_type_p = [len(i) for i in log_types(records_p).values()]

        filename_s = 'tests/parser/serial_info.txt'
        records_s = parse_file(filename_s)
        num_of_record_type_s = [len(i) for i in log_types(records_s).values()]

        self.assertSequenceEqual(num_of_record_type_s, num_of_record_type_p,
                                 'The number of logs for each type must be equal for parallel log and serial log')

    def test_parallel_3_debug(self):
        filename = 'tests/parser/parallel_3_debug.txt'
        records = parse_file(filename)
        mpi_processes = 3

        self.assertEqual(len(records) % mpi_processes, 0,
                         'The number of logs should by a multiple of the number of processes)')

        num_of_record_type = [len(i) for i in log_types(records).values()]
        self.assertEqual(all(i % mpi_processes == 0 for i in num_of_record_type), True,
                         'The number of logs of each type should be a multiple of the number of processes')

        df = pd.DataFrame(records)
        df = fill_ogs_context(df)
        dfe = analysis_time_step(df)

        # some specific values
        record_id = namedtuple('id', 'mpi_process time_step')
        digits = 6
        self.assertAlmostEqual(dfe.at[record_id(mpi_process=0.0, time_step=1.0), 'output_time'], 0.001871, digits)
        self.assertAlmostEqual(dfe.at[record_id(mpi_process=1.0, time_step=1.0), 'output_time'], 0.001833, digits)
        self.assertAlmostEqual(dfe.at[record_id(mpi_process=0.0, time_step=1.0), 'linear_solver_time'], 0.004982,
                               digits)
        self.assertAlmostEqual(dfe.at[record_id(mpi_process=0.0, time_step=1.0), 'assembly_time'], 0.002892, digits)
        self.assertAlmostEqual(dfe.at[record_id(mpi_process=1.0, time_step=1.0), 'dirichlet_time'], 0.000250, digits)
        self.assertAlmostEqual(dfe.at[record_id(mpi_process=2.0, time_step=1.0), 'time_step_solution_time'], 0.008504,
                               digits)

    def test_serial_convergence_newton_iteration_long(self):
        filename = 'tests/parser/serial_convergence_long.txt'
        records = parse_file(filename)
        df = pd.DataFrame(records)
        df = fill_ogs_context(df)
        dfe = analysis_convergence_newton_iteration(df)

        # some specific values
        record_id = namedtuple('id', 'time_step coupling_iteration process iteration_number component')
        digits = 6
        self.assertAlmostEqual(
            dfe.at[record_id(time_step=1.0, coupling_iteration=0, process=0, iteration_number=1, component=-1), 'dx'],
            9.906900e+05, digits)
        self.assertAlmostEqual(
            dfe.at[record_id(time_step=10.0, coupling_iteration=5, process=1, iteration_number=1, component=1), 'x'],
            1.066500e+00, digits)

    def test_serial_convergence_coupling_iteration_long(self):
        filename = 'tests/parser/serial_convergence_long.txt'
        records = parse_file(filename)
        df = pd.DataFrame(records)
        dfe = analysis_simulation_termination(df)
        status = dfe.empty  # No errors assumed
        self.assertEqual(status, True)  #
        if (not (status)):
            print(dfe)
        self.assertEqual(status, True)  #
        df = fill_ogs_context(df)
        dfe = analysis_convergence_coupling_iteration(df)

        # some specific values
        record_id = namedtuple('id', 'time_step coupling_iteration coupling_iteration_process component')
        digits = 6
        self.assertAlmostEqual(
            dfe.at[record_id(time_step=1.0, coupling_iteration=1, coupling_iteration_process=0, component=-1), 'dx'],
            1.696400e+03, digits)
        self.assertAlmostEqual(
            dfe.at[record_id(time_step=10.0, coupling_iteration=5, coupling_iteration_process=1, component=-1), 'x'],
            1.066500e+00, digits)

    def test_serial_critical(self):
        filename = 'tests/parser/serial_critical.txt'
        records = parse_file(filename)
        self.assertEqual(len(records),4)
        df = pd.DataFrame(records)
        self.assertEqual(len(df), 4)
        dfe = analysis_simulation_termination(df)
        has_errors = not (dfe.empty)
        self.assertEqual(has_errors, True)
        if has_errors:
            print(dfe)


    def test_serial_warning_only(self):
        filename = 'tests/parser/serial_warning_only.txt'
        records = parse_file(filename)
        self.assertEqual(len(records),1)
        df = pd.DataFrame(records)
        self.assertEqual(len(df), 1)
        dfe = analysis_simulation_termination(df)
        has_errors = not (dfe.empty)
        self.assertEqual(has_errors, True)
        if has_errors:
            print(dfe)


    def test_serial_time_vs_iterations(self):
        filename = 'tests/parser/serial_convergence_long.txt'
        records = parse_file(filename)
        df = pd.DataFrame(records)
        df = fill_ogs_context(df)
        dfe = time_step_vs_iterations(df)
        # some specific values
        self.assertEqual(
            dfe.at[0, 'iteration_number'], 1)
        self.assertEqual(
            dfe.at[1, 'iteration_number'], 6)
        self.assertEqual(
            dfe.at[10, 'iteration_number'], 5)


if __name__ == '__main__':
    unittest.main()
