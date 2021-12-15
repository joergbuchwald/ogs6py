#!/usr/bin/env python

# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
#            Distributed under a Modified BSD License.
#              See accompanying file LICENSE.txt or
#              http://www.opengeosys.org/project/license

from dataclasses import dataclass


@dataclass
class Log:
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
class TimeStepSolutionTimeCoupledScheme(MPIProcess):
    process: int
    time_step_solution_time: float
    time_step: int
    coupling_iteration: int


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


@dataclass
class CouplingIterationConvergence(MPIProcess):
    coupling_iteration_process: int
    

@dataclass
class GenericCodePoint(MPIProcess):
    message: str


@dataclass
class Error(MPIProcess):
    error_message: str

@dataclass
class Critical(MPIProcess):
    critical_message: str

@dataclass
class Warning(MPIProcess):
    warning_message: str


def ogs_regexes():
    return [("info: \[time\] Output of timestep (\d+) took ([\d\.e+-]+) s", TimeStepOutputTime),
            ("info: \[time\] Time step #(\d+) took ([\d\.e+-]+) s", TimeStepFinishedTime),
            ("info: \[time\] Reading the mesh took ([\d\.e+-]+) s", MeshReadTime),
            ("info: \[time\] Execution took ([\d\.e+-]+) s", SimulationExecutionTime),
            ("info: \[time\] Solving process #(\d+) took ([\d\.e+-]+) s in time step #(\d+)  coupling iteration #(\d+)",
             TimeStepSolutionTimeCoupledScheme),
            ("info: \[time\] Solving process #(\d+) took ([\d\.e+-]+) s in time step #(\d+)", TimeStepSolutionTime),
            ("info: === Time stepping at step #(\d+) and time ([\d\.e+-]+) with step size (.*)", TimeStepStartTime),
            ("info: \[time\] Assembly took ([\d\.e+-]+) s", AssemblyTime),
            ("info: \[time\] Applying Dirichlet BCs took ([\d\.e+-]+) s", DirichletTime),
            ("info: \[time\] Linear solver took ([\d\.e+-]+) s", LinearSolverTime),
            ("info: \[time\] Iteration #(\d+) took ([\d\.e+-]+) s", IterationTime),
            ("info: Convergence criterion: \|dx\|=([\d\.e+-]+), \|x\|=([\d\.e+-]+), \|dx\|/\|x\|=([\d\.e+-]+|nan|inf)$",
             TimeStepConvergenceCriterion),
            ("info: ------- Checking convergence criterion for coupled solution of process #(\d+)",
             CouplingIterationConvergence),
            (
                "info: Convergence criterion, component (\d+): \|dx\|=([\d\.e+-]+), \|x\|=([\d\.e+-]+), \|dx\|/\|x\|=([\d\.e+-]+|nan|inf)$",
                ComponentConvergenceCriterion),
            ("critical: (.*)",Critical ),
            ("error: (.*)", Error),
            ("warning: (.*)", Warning)
            ]