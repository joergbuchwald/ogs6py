import unittest

from ogs6py.log_parser.log_parser import parse_file
# this needs to be replaced with regexes from specific ogs version
from ogs6py.log_parser.ogs_regexes import ogs_regexes
import pandas as pd
from collections import namedtuple, defaultdict


def filter_time_analysis_by_time_step(df):
    dfe_ts = df.pivot_table(['output_time', 'time_step_solution_time'], ['mpi_process', 'time_step'])
    dfe_tsi = df.pivot_table(['assembly_time', 'linear_solver_time', 'dirichlet_time'],
                             ['mpi_process', 'time_step', 'iteration_number']).groupby(
        level=['mpi_process', 'time_step']).sum()
    dfe = dfe_ts.merge(dfe_tsi, left_index=True, right_index=True)
    return dfe


def pandas_from_records(records):
    df = pd.DataFrame(records)
    # Some logs do not contain information about time_step and iteration
    # These information must be collected by context (by surrounding log lines from same mpi_process)
    # Logs are grouped by mpi_process to get only surrounding log lines from same mpi_process

    # There are log lines that give the current time step (when time step starts).
    # It can be assumed that in all following lines belong to this time steps, until next collected value of time step
    df['time_step'] = df.groupby('mpi_process')[['time_step']].fillna(method='ffill').fillna(value=0)

    # Back fill, because iteration number can be found in logs at the END of the iteration
    df['iteration_number'] = df.groupby('mpi_process')[['iteration_number']].fillna(method='bfill')
    return df


def log_types(records):
    d = defaultdict(list)
    for i in records:
        d[type(i)].append(i)
    return d


class OGSParserTest(unittest.TestCase):
    def test_parallel_1_compare_serial_info(self):
        filename_p = 'parser/parallel_1_info.txt'
        records_p = parse_file(filename_p, ogs_regexes(), petsc=True)
        num_of_record_type_p = [len(i) for i in log_types(records_p).values()]

        filename_s = 'parser/serial_info.txt'
        records_s = parse_file(filename_s, ogs_regexes(), petsc=False)
        num_of_record_type_s = [len(i) for i in log_types(records_s).values()]

        self.assertSequenceEqual(num_of_record_type_s, num_of_record_type_p,
                                 'The number of logs for each type must be equal for parallel log and serial log')

    def test_parallel_3_debug(self):
        filename = 'parser/parallel_3_debug.txt'
        records = parse_file(filename, ogs_regexes(), petsc=True)
        mpi_processes = 3

        self.assertEqual(len(records) % mpi_processes, 0,
                         'The number of logs should by a multiple of the number of processes)')

        num_of_record_type = [len(i) for i in log_types(records).values()]
        self.assertEqual(all(i % mpi_processes == 0 for i in num_of_record_type), True,
                         'The number of logs of each type should be a multiple of the number of processes')

        df = pandas_from_records(records)
        dfe = filter_time_analysis_by_time_step(df)

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

    def test_seriel_convergence_short(self):
        filename = 'parser/serial_convergence_short.txt'
        records = parse_file(filename, ogs_regexes(), petsc=False)
        df = pandas_from_records(records)
        # component-wise
        dfe_sic = df.pivot_table(['dx', 'x', 'dx_x'], ['time_step', 'iteration_number', 'component'])
        # iteration - wise
        dfe_si = df.pivot_table(['dx', 'x', 'dx_x'], ['time_step', 'iteration_number'])

        # some specific values
        record_id = namedtuple('id', 'time_step iteration_number component')
        digits = 6
        self.assertAlmostEqual(dfe_sic.at[record_id(time_step=1.0, iteration_number=1, component=1), 'dx'],
                               9.694038e-02, digits)


if __name__ == '__main__':
    unittest.main()
