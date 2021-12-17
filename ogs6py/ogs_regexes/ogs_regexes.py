#!/usr/bin/env python

# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
#            Distributed under a Modified BSD License.
#              See accompanying file LICENSE.txt or
#              http://www.opengeosys.org/project/license

from dataclasses import dataclass

class Info:
    @staticmethod
    def type_str():
        return 'Info'


class WarningType:
    @staticmethod
    def type_str():
        return 'Warning'


class ErrorType:
    @staticmethod
    def type_str():
        return 'Error'


class CriticalType:
    @staticmethod
    def type_str():
        return 'Critical'


@dataclass
class Log:
    type:str
    line: int



@dataclass
class MPIProcess(Log):
    mpi_process: int


@dataclass
class AssemblyTime(MPIProcess,Info):
    assembly_time: float


@dataclass
class TimeStep(MPIProcess, Info):
    time_step: int


@dataclass
class Iteration(TimeStep,Info):
    iteration_number: int


@dataclass
class IterationTime(MPIProcess,Info):
    iteration_number: int
    iteration_time: float


@dataclass
class TimeStepStartTime(MPIProcess,Info):
    time_step: int
    step_start_time: float
    step_size: float


@dataclass
class TimeStepOutputTime(MPIProcess,Info):
    time_step: int
    output_time: float


@dataclass
class TimeStepSolutionTime(MPIProcess,Info):
    process: int
    time_step_solution_time: float
    time_step: int


@dataclass
class TimeStepSolutionTimeCoupledScheme(MPIProcess,Info):
    process: int
    time_step_solution_time: float
    time_step: int
    coupling_iteration: int


@dataclass
class TimeStepFinishedTime(MPIProcess,Info):
    time_step: int
    time_step_finished_time: float


@dataclass
class DirichletTime(MPIProcess,Info):
    dirichlet_time: float


@dataclass
class LinearSolverTime(MPIProcess,Info):
    linear_solver_time: float


@dataclass
class MeshReadTime(MPIProcess,Info):
    mesh_read_time: float


@dataclass
class SimulationExecutionTime(MPIProcess,Info):
    execution_time: float


@dataclass
class ComponentConvergenceCriterion(MPIProcess,Info):
    component: int
    dx: float
    x: float
    dx_x: float


@dataclass
class TimeStepConvergenceCriterion(MPIProcess,Info):
    dx: float
    x: float
    dx_x: float


@dataclass
class CouplingIterationConvergence(MPIProcess,Info):
    coupling_iteration_process: int
    

@dataclass
class GenericCodePoint(MPIProcess,Info):
    message: str


@dataclass
class ErrorMessage(MPIProcess, ErrorType):
    message: str

@dataclass
class CriticalMessage(MPIProcess, CriticalType):
    message: str

@dataclass
class WarningMessage(MPIProcess, WarningType):
    message: str


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
            ("critical: (.*)", CriticalMessage),
            ("error: (.*)", ErrorMessage),
            ("warning: (.*)", WarningMessage)
            ]