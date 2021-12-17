import unittest

import pandas as pd

from ogs6py.log_parser.log_parser import parse_file
# this needs to be replaced with regexes from specific ogs version
from collections import namedtuple, defaultdict
from ogs6py.log_parser.common_ogs_analyses import fill_ogs_context, analysis_time_step, \
    analysis_convergence_newton_iteration, analysis_convergence_coupling_iteration, analysis_simulation_termination


def log_types(records):
    d = defaultdict(list)
    for record in records:
        d[type(record)].append(record)
    return d


class OGSParserTest(unittest.TestCase):
    def test_parallel_1_compare_serial_info(self):
        filename_p = 'parser/parallel_1_info.txt'
        # Only for MPI execution with 1 process we need to tell the log parser by force_parallel=True!
        records_p = parse_file(filename_p, force_parallel=True)
        num_of_record_type_p = [len(i) for i in log_types(records_p).values()]

        filename_s = 'parser/serial_info.txt'
        records_s = parse_file(filename_s)
        num_of_record_type_s = [len(i) for i in log_types(records_s).values()]

        self.assertSequenceEqual(num_of_record_type_s, num_of_record_type_p,
                                 'The number of logs for each type must be equal for parallel log and serial log')

    def test_parallel_3_debug(self):
        filename = 'parser/parallel_3_debug.txt'
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
        filename = 'parser/serial_convergence_long.txt'
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
        filename = 'parser/serial_convergence_long.txt'
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

    def test_serial_bad(self):
        filename = 'parser/serial_bad.txt'
        records = parse_file(filename)
        self.assertEqual(len(records),4)
        df = pd.DataFrame(records)
        self.assertEqual(len(df), 4)
        dfe = analysis_simulation_termination(df)
        has_errors = not (dfe.empty)
        self.assertEqual(has_errors, True)
        if has_errors:
            print(dfe)


if __name__ == '__main__':
    unittest.main()
