#!/usr/bin/env python

# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
#            Distributed under a Modified BSD License.
#              See accompanying file LICENSE.txt or
#              http://www.opengeosys.org/project/license

import re
import sys
import pandas as pd
from dataclasses import dataclass


def try_match_parallel_line(line: str, line_nr: int, regex: re.Pattern, pattern_class):
    if match := regex.match(line):
        # Line , Process, Type specific
        types = (int, int,) + tuple(pattern_class.__annotations__.values())
        match_with_line = (line_nr,) + match.groups()
        return [ctor(s) for ctor, s in zip(types, match_with_line)]
    return None


def try_match_serial_line(line: str, line_nr: int, regex: re.Pattern, pattern_class):
    if match := regex.match(line):
        # Line , Process, Type specific
        types = (int, int,) + tuple(pattern_class.__annotations__.values())
        match_with_line = (line_nr, 0,) + match.groups()
        return [ctor(s) for ctor, s in zip(types, match_with_line)]
    return None


@dataclass
class Log(object):
    line: int


@dataclass
class MPIProcess(Log):
    mpi_process: int


@dataclass
class AssemblyTime(MPIProcess):
    assembly_time: float


@dataclass
class TimeStep(MPIProcess):
    time_step: int


@dataclass
class Iteration(TimeStep):
    iteration_number: int


@dataclass
class IterationTime(MPIProcess):
    iteration_number: int
    iteration_time: float


@dataclass
class TimeStepStartTime(MPIProcess):
    time_step: int
    step_start_time: float
    step_size: float


@dataclass
class TimeStepOutputTime(MPIProcess):
    time_step: int
    output_time: float


@dataclass
class TimeStepSolutionTime(MPIProcess):
    process: int
    time_step_solution_time: float
    time_step: int


@dataclass
class TimeStepFinishedTime(MPIProcess):
    time_step: int
    time_step_finished_time: float


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
class ComponentConvergenceCriterion(MPIProcess):
    component: int
    dx: float
    x: float
    dx_x: float


@dataclass
class TimeStepConvergenceCriterion(MPIProcess):
    dx: float
    x: float
    dx_x: float


r1 = [("info: \[time\] Output of timestep (\d+) took ([\d\.e+-]+) s", TimeStepOutputTime),
      ("info: \[time\] Time step #(\d+) took ([\d\.e+-]+) s", TimeStepFinishedTime),
      ("info: \[time\] Reading the mesh took ([\d\.e+-]+) s", MeshReadTime),
      ("info: \[time\] Execution took ([\d\.e+-]+) s", SimulationExecutionTime),
      ("info: \[time\] Solving process #(\d+) took ([\d\.e+-]+) s in time step #(\d+)", TimeStepSolutionTime),
      ("info: === Time stepping at step #(\d+) and time ([\d\.e+-]+) with step size (.*)", TimeStepStartTime),
      ("info: \[time\] Assembly took ([\d\.e+-]+) s", AssemblyTime),
      ("info: \[time\] Applying Dirichlet BCs took ([\d\.e+-]+) s", DirichletTime),
      ("info: \[time\] Linear solver took ([\d\.e+-]+) s", LinearSolverTime),
      ("info: \[time\] Iteration #(\d+) took ([\d\.e+-]+) s", IterationTime),
      ("info: Convergence criterion: \|dx\|=([\d\.e+-]+), \|x\|=([\d\.e+-]+), \|dx\|/\|x\|=([\d\.e+-]+)$",
       TimeStepConvergenceCriterion),
      # Examples simple CodePoints (no extra information is gathered)
      ("info: Calculate non-equilibrium initial residuum$", MPIProcess),
      (
      "info: Convergence criterion, component (\d+): \|dx\|=([\d\.e+-]+), \|x\|=([\d\.e+-]+), \|dx\|/\|x\|=([\d\.e+-]+)$",
      ComponentConvergenceCriterion)

      ]


def parse_file(file_name, maximum_lines=None, petsc=True):
    if petsc:
        process_regex = '\\[(\\d+)\\]\\ '
        try_match = try_match_parallel_line
    else:
        process_regex = ''
        try_match = try_match_serial_line

    def compile_re_fn(mpi_process_regex):
        return lambda regex: re.compile(mpi_process_regex + regex)

    compile_re = compile_re_fn(process_regex)
    patterns = [(compile_re(k), v) for k, v in r1]

    number_of_lines_read = 0
    with open(file_name) as file:
        lines = iter(file)
        records = list()
        for line in lines:
            number_of_lines_read += 1

            if (maximum_lines is not None) and (maximum_lines > number_of_lines_read):
                break

            for k, v in patterns:
                if r := try_match(line, number_of_lines_read, k, v):
                    records.append(v(*r))
                    break

        # TODO parse all DEBUG outputs in c++ sources and generate a full list
        # records.append(UnknownLine(line))
    return records


if __name__ == "__main__":
    filename = sys.argv[1]
    data = parse_file(sys.argv[1], maximum_lines=None, petsc=True)
    df = pd.DataFrame(data)
    filename_prefix = filename.split('.')[0]
    df.to_csv(f"{filename_prefix}.csv")
