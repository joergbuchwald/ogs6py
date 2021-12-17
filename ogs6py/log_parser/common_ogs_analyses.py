import pandas as pd
import numpy as np


# Helper functions
def check_input(df, interest, context):
    diff = set(interest) - set(df.columns)
    if diff:
        raise Exception('Column(s) of interest ({}) is/are not present in table'.format(','.join(diff)))
    diff = set(context) - set(df.columns)
    if diff:
        raise Exception('Column(s) of context ({}) is/are not present in table', ','.format(','.join(diff)))


def check_output(pt, interest, context):
    if pt.empty:
        raise Exception(
            'The values of {} are not associated to all of {}. Call or see fill_ogs_context'.format(','.join(interest),','.join(context)))



# decorator for analyses
def pre_post_check(interest, context):
    def wrap(f):
        def wrapped_f(df):
            check_input(df, interest, context)
            pt = f(df)
            check_output(pt, interest, context)
            return pt
        return wrapped_f
    return wrap


def analysis_time_step(df):
    interest1 = ['output_time', 'time_step_solution_time']
    interest2 = ['assembly_time', 'linear_solver_time', 'dirichlet_time']
    interest = [*interest1, *interest2]
    context = ['mpi_process', 'time_step']
    check_input(df, interest, context)

    dfe_ts = df.pivot_table(interest1, context)
    # accumulates coupling iterations and newton iterations
    dfe_tsi = df.pivot_table(interest2, context, aggfunc='sum')

    dfe = dfe_ts.merge(dfe_tsi, left_index=True, right_index=True)
    check_output(dfe, interest, context)
    return dfe


def analysis_simulation(df):
    interest = ['execution_time']   #  'start_time'
    context = ['mpi_process']
    check_input(df, interest, context)

    pt = df.pivot_table(interest, context)
    check_output(pt, interest, context)
    return pt


def analysis_convergence_newton_iteration(df):
    dfe_newton_iteration = df.copy()
    interest = ['dx', 'x', 'dx_x']
    if 'coupling_iteration' in df:
        context = ['time_step', 'coupling_iteration', 'process',
                   'iteration_number', 'component']
        check_input(df, interest, context)
        # Eliminate all entries for coupling iteration (not of interest in this study)
        dfe_newton_iteration['coupling_iteration'] = dfe_newton_iteration.groupby('mpi_process')[
            ['coupling_iteration']].fillna(method='bfill')
        dfe_newton_iteration = dfe_newton_iteration[~dfe_newton_iteration['coupling_iteration_process'].notna()]
        dfe_newton_iteration = dfe_newton_iteration.dropna(subset=['x'])

        pt = dfe_newton_iteration.pivot_table(interest, context)

    else:
        context = ['time_step', 'process', 'iteration_number', 'component']
        check_input(df, interest, context)
        pt = dfe_newton_iteration.pivot_table(interest, context)

    check_output(pt, interest, context)
    return pt


@pre_post_check(interest=['dx', 'x', 'dx_x'], \
                context=['time_step', 'coupling_iteration', 'coupling_iteration_process',
                         'component'])
def analysis_convergence_coupling_iteration(df):
    # Coupling iteration column will be modified specific for coupling iteration analysis, modified data can not be used for other analysis ->copy!
    dfe_convergence_coupling_iteration = df.copy()
    interest = ['dx', 'x', 'dx_x']
    context = ['time_step', 'coupling_iteration', 'coupling_iteration_process',
               'component']
    check_input(df, interest, context)

    dfe_convergence_coupling_iteration['coupling_iteration'] = \
        dfe_convergence_coupling_iteration.groupby('mpi_process')[['coupling_iteration']].fillna(method='ffill')
    # All context log lines (iteration_number) have no values for dx, dx_x, x . From now on not needed -> dropped
    dfe_convergence_coupling_iteration = dfe_convergence_coupling_iteration.dropna(
        subset=['coupling_iteration_process']).dropna(subset=['x'])

    pt = dfe_convergence_coupling_iteration.pivot_table(interest, context)
    check_output(pt, interest, context)
    return pt


def time_step_vs_iterations(df):
    interest = 'iteration_number'
    context = 'time_step'
    check_input(df, interest, context)
    pt = df.pivot_table(["iteration_number"], ["time_step"], aggfunc=np.max)
    check_output(pt, interest, context)
    return pt


def analysis_simulation_termination(df):
    # For full print of messages consider setup jupyter notebook:
    # pd.set_option('display.max_colwidth', None)
    messages = ['error_message', 'critical_message', 'warning_message']
    if any(message in df for message in messages):
        df2 = df.dropna(subset=messages, how='all')[messages + ['line', 'mpi_process']]
        # ToDo Merge columns together a add a column for type (warning, error, critical)
        return df2
    else:
        return pd.DataFrame()


def fill_ogs_context(df):
    # Some columns that contain actual integer values are converted to float
    # See https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html
    # ToDo list of columns with integer values are known from regular expression
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
