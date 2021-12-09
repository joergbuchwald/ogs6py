import pandas as pd
import numpy as np

def analysis_by_time_step(df):
    dfe_ts = df.pivot_table(['output_time', 'time_step_solution_time'], ['mpi_process', 'time_step'])
    dfe_tsi = df.pivot_table(['assembly_time', 'linear_solver_time', 'dirichlet_time'],
                             ['mpi_process', 'time_step', 'iteration_number']).groupby(
        level=['mpi_process', 'time_step']).sum()
    dfe = dfe_ts.merge(dfe_tsi, left_index=True, right_index=True)
    return dfe


def analysis_convergence_newton_iteration(df):
    dfe_newton_iteration = df.copy()
    if 'coupling_iteration' in df:
        # Eliminate all entries for coupling iteration (not of interest in this study)
        dfe_newton_iteration['coupling_iteration'] = dfe_newton_iteration.groupby('mpi_process')[
            ['coupling_iteration']].fillna(method='bfill')
        dfe_newton_iteration = dfe_newton_iteration[~dfe_newton_iteration['coupling_iteration_process'].notna()]
        dfe_newton_iteration = dfe_newton_iteration.dropna(subset=['x'])
        pt = dfe_newton_iteration.pivot_table(['dx', 'x', 'dx_x'],
                                                               ['time_step', 'coupling_iteration', 'process',
                                                                'iteration_number', 'component'])
    else:
        pt = dfe_newton_iteration.pivot_table(['dx', 'x', 'dx_x'],
                                                               ['time_step', 'process',
                                                                'iteration_number', 'component'])
    return pt


def analysis_convergence_coupling_iteration(df):
    # Coupling iteration column will be modified specific for coupling iteration analysis, modified data can not be used for other analysis ->copy!
    dfe_convergence_coupling_iteration = df.copy()
    #
    dfe_convergence_coupling_iteration['coupling_iteration'] = \
        dfe_convergence_coupling_iteration.groupby('mpi_process')[['coupling_iteration']].fillna(method='ffill')
    # All context log lines (iteration_number) have no values for dx, dx_x, x . From now on not needed -> dropped
    dfe_convergence_coupling_iteration = dfe_convergence_coupling_iteration.dropna(
        subset=['coupling_iteration_process']).dropna(subset=['x'])

    pt = dfe_convergence_coupling_iteration.pivot_table(['dx', 'x', 'dx_x'],
                                                   ['time_step', 'coupling_iteration', 'coupling_iteration_process',
                                                    'component'])
    return pt

def time_step_vs_iterations(df):
    df = df.pivot_table(["iteration_number"],["time_step"], aggfunc=np.max)
    return df

def pandas_from_records(records):
    df = pd.DataFrame(records)

    # Some columns that contain actual integer values are converted to float
    # See https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html
    # ToDo list of columns with integer values are know from regular expression
    for column in df.columns:
        try:
            df[column] = df[column].astype('Int64')
        except:
            pass


    # Some logs do not contain information about time_step and iteration
    # These information must be collected by context (by surrounding log lines from same mpi_process)
    # Logs are grouped by mpi_process to get only surrounding log lines from same mpi_process

    # There are log lines that give the current time step (when time step starts).
    # It can be assumed that in all following lines belong to this time steps, until next collected value of time step
    df['time_step'] = df.groupby('mpi_process')[['time_step']].fillna(method='ffill').fillna(value=0)

    # Back fill, because iteration number can be found in logs at the END of the iteration
    df['iteration_number'] = df.groupby('mpi_process')[['iteration_number']].fillna(method='bfill')

    # ToDo Comment
    if 'component' in df:
        df['component'] = df.groupby('mpi_process')[['component']].fillna(value=-1)
    # Forward fill because process will be printed in the beginning - applied to all subsequent
    if 'process' in df:
        df['process'] = df.groupby('mpi_process')[['process']].fillna(method='bfill')
    # Attention - coupling iteration applies to successor line and to all other predecessors - it needs further processing for specific analysis
    if 'coupling_iteration_process' in df:
        df['coupling_iteration_process'] = df.groupby('mpi_process')[['coupling_iteration_process']].fillna(
            method='ffill',
            limit=1)
    return df
