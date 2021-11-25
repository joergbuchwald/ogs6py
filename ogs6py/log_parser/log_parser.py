#!/usr/bin/env python

# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
#            Distributed under a Modified BSD License.
#              See accompanying file LICENSE.txt or
#              http://www.opengeosys.org/project/license

import re
import sys
import pandas as pd
from dataclasses import dataclass


def try_match_serial(line: str, regex: re.Pattern, *types):
    if match := regex.match(line):
        match_with_process_0 = tuple('0')+match.groups()
        types_with_process_0 = tuple([int] + list(types))
        return [ctor(s) for ctor, s in zip(types_with_process_0, match_with_process_0)]
    return None


def try_match_parallel(line: str, regex: re.Pattern, *types):
    if match := regex.match(line):
        types = (int, *types)
        return [ctor(s) for ctor, s in zip(types, match.groups())]
    return None


@dataclass
class Log(object):
    line: int


@dataclass
class MPIProcess(Log):
    mpi_process: int


@dataclass
class TimeStep(MPIProcess):
    time_step: int


@dataclass
class Iteration(TimeStep):
    iteration_number: int


@dataclass
class IterationTime(Iteration):
    iteration_time: float


@dataclass
class IterationTime_N(MPIProcess):
    iteration_time: float
    iteration_number: int


@dataclass
class TimeStepStartTime(TimeStep):
    step_start_time: float
    step_size: float



@dataclass
class TimeStepOutputTime(TimeStep):
    output_time: float


@dataclass
class TimeStepSolutionTime(TimeStep):
    time_step_solution_time: float
    process: int


@dataclass
class TimeStepFinishedTime(TimeStep):
    time_step_finished_time: float



@dataclass
class AssemblyTime(MPIProcess):
    assembly_time: float



@dataclass
class DirichletTime(MPIProcess):
    dirichlet_time: float



@dataclass
class LinearSolverTime(MPIProcess):
    linear_solver_time: float



@dataclass
class MeshReadTime(MPIProcess):
    mesh_read_time: float



@dataclass
class SimulationExecutionTime(MPIProcess):
    execution_time: float

@dataclass
class ComponentConvergenceCriterion(Iteration):
    component: int
    dx: float
    x: float
    dx_x: float



@dataclass
class TimeStepConvergenceCriterion(TimeStep):
    dx: float
    x: float
    dx_x: float



def parse_file(file_name, maximum_time_steps=None, maximum_lines=None, petsc=True):

    if petsc:
        process_regex = '\\[(\\d+)\\]\\ '
        try_match = try_match_parallel
    else:
        process_regex = ''
        try_match = try_match_serial

    _re_assembly_time = [re.compile(process_regex + "info: \[time\] Assembly took ([\d\.e+-]+) s"), float]

    _re_execution_time = [re.compile(process_regex + "info: \[time\] Execution took ([\d\.e+-]+) s"), float]



    _re_convergence = [
        re.compile(process_regex +
                   "info: Convergence criterion: \|dx\|=([\d\.e+-]+), \|x\|=([\d\.e+-]+), \|dx\|/\|x\|=([\d\.e+-]+)$"
                   ),
        float,
        float,
        float,
    ]

    # Examples simple CodePoints (no extra information is gathered)
    _re_initial_residuum = [
        re.compile(process_regex +
                   "info: Calculate non-equilibrium initial residuum$"
                   )
    ]

    _re_warning_use_multiple_meshes_input = [
        re.compile(process_regex + "warning: Consider switching from mesh and geometry input to multiple meshes input.$"
                   )
    ]

    _re_component_convergence = [
        re.compile(process_regex +
                   "info: Convergence criterion, component (\d+): \|dx\|=([\d\.e+-]+), \|x\|=([\d\.e+-]+), \|dx\|/\|x\|=([\d\.e+-]+)$"
                   ),
        int,
        float,
        float,
        float,
    ]

    _re_linear_solver_time = [
        re.compile(process_regex + "info: \[time\] Linear solver took ([\d\.e+-]+) s"),
        float,
    ]

    _re_reading_mesh = [re.compile(process_regex + "info: \[time\] Reading the mesh took ([\d\.e+-]+) s"), float]

    _re_dirichlet_bc_time = [
        re.compile(process_regex + "info: \[time\] Applying Dirichlet BCs took ([\d\.e+-]+) s"),
        float,
    ]

    _re_iteration = [
        re.compile(process_regex + "info: \[time\] Iteration #(\d+) took ([\d\.e+-]+) s"),
        int,
        float,
    ]

    _re_time_step_start = [
        re.compile(process_regex +
                   "info: === Time stepping at step #(\d+) and time ([\d\.e+-]+) with step size (.*)"
                   ),
        int,
        float,
        float,
    ]

    _re_time_step_output = [
        re.compile(process_regex + "info: \[time\] Output of timestep (\d+) took ([\d\.e+-]+) s"),
        int,
        float,
    ]

    _re_time_step_solution_time = [
        re.compile(process_regex + "info: \[time\] Solving process #(\d+) took ([\d\.e+-]+) s in time step #(\d+)"
                   ),
        int,
        float,
        int,
    ]

    _re_time_step_finished = [
        re.compile(process_regex + "info: \[time\] Time step #(\d+) took ([\d\.e+-]+) s"),
        int,
        float,
    ]

    number_of_lines_read = 0
    with open(file_name) as file:
        lines = iter(file)
        processes = get_mpi_processes(lines)

        records = list()
        for line in lines:
            number_of_lines_read += 1

            if (maximum_lines is not None) and (maximum_lines > number_of_lines_read):
                break

            if r := try_match(line, *_re_iteration):
                [mpi_process, iteration, time] = r
                records.append(IterationTime_N(mpi_process=mpi_process,iteration_number=iteration, iteration_time=time,line=number_of_lines_read))
                continue

            if r := try_match(line, *_re_assembly_time):
                [mpi_process, time] = r
                records.append(
                    AssemblyTime(mpi_process=mpi_process, assembly_time=time, line=number_of_lines_read))
                continue

            if r := try_match(line, *_re_dirichlet_bc_time):
                [mpi_process, time] = r
                records.append(
                    DirichletTime(mpi_process=mpi_process, dirichlet_time=time, line=number_of_lines_read))
                continue

            if r := try_match(line, *_re_linear_solver_time):
                [mpi_process, time] = r
                records.append(LinearSolverTime(mpi_process=mpi_process, linear_solver_time=time, line=number_of_lines_read))
                continue

            if r := try_match(line, *_re_component_convergence):
                [mpi_process, number, dx, x, dx_relative] = r
                records.append(
                    ComponentConvergenceCriterion(mpi_process=mpi_process, time_step=step, iteration_number=iteration,
                                                  component=number, dx=dx, x=x, dx_x=dx_relative, line=number_of_lines_read))
                continue

            if r := try_match(line, *_re_convergence):
                [mpi_process, dx, x, dx_x] = r
                records.append(
                    TimeStepConvergenceCriterion(mpi_process=mpi_process, time_step=step, dx=dx, x=x, dx_x=dx_x, line=number_of_lines_read)
                )
                continue

            if r := try_match(line, *_re_time_step_start):
                [mpi_process, step, start_time, step_size] = r
                records.append(TimeStepStartTime(mpi_process=mpi_process, time_step=step, step_start_time=start_time,
                                                 step_size=step_size, line=number_of_lines_read))
                continue

            if r := try_match(line, *_re_time_step_solution_time):
                [mpi_process, process, time, step] = r
                records.append(TimeStepSolutionTime(mpi_process=mpi_process, time_step=step, time_step_solution_time=time,
                                                    process=process, line=number_of_lines_read))
                continue

            if r := try_match(line, *_re_time_step_output):
                r= [number_of_lines_read, *r]
                records.append(TimeStepOutputTime(*r))
                continue

            if r := try_match(line, *_re_time_step_finished):
                r = [number_of_lines_read, *r ]
                records.append(TimeStepFinishedTime(*r))
                continue

            if r := try_match(line, *_re_reading_mesh):
                mpi_process, time = r
                records.append(MeshReadTime(mpi_process=mpi_process, mesh_read_time=time, line=number_of_lines_read))
                continue

            if r := try_match(line, *_re_execution_time):
                [mpi_process, time] = r
                records.append(SimulationExecutionTime(mpi_process=mpi_process,execution_time=time, line=number_of_lines_read))
                continue

        # TODO parse all DEBUG outputs in c++ sources and generate a full list
        # records.append(UnknownLine(line))
    return records


def get_mpi_processes(lines):
    processes = 0
    # There is no synchronisation barrier between both info, we count both and divide
    while re.search("info: This is OpenGeoSys-6 version|info: OGS started on", next(lines)):
        processes = processes + 1
    return int(processes / 2 + 0.5)


if __name__ == "__main__":
    filename = sys.argv[1]
    data = parse_file(sys.argv[1], maximum_time_steps=None, maximum_lines=None, petsc=True)
    df = pd.DataFrame(data)
    filename_prefix = filename.split('.')[0]
    df.to_csv(f"{filename_prefix}.csv")
