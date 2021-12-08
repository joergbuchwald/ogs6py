#!/usr/bin/env python

# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
#            Distributed under a Modified BSD License.
#              See accompanying file LICENSE.txt or
#              http://www.opengeosys.org/project/license

import re
import sys
import pandas as pd
from ogs6py.log_parser.ogs_regexes import ogs_regexes


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


def mpi_processes(file_name):
    occurrences = 0
    with open(file_name) as file:
        lines = iter(file)
        # There is no synchronisation barrier between both info, we count both and divide
        while re.search("info: This is OpenGeoSys-6 version|info: OGS started on", next(lines)):
            occurrences = occurrences + 1
        processes = int(occurrences / 2)
        return processes


def parse_file(file_name, maximum_lines=None, force_parallel=False):
    ogs_res = ogs_regexes()
    parallel_log = force_parallel or mpi_processes(file_name) > 1

    if parallel_log:
        process_regex = '\\[(\\d+)\\]\\ '
        try_match = try_match_parallel_line
    else:
        process_regex = ''
        try_match = try_match_serial_line

    def compile_re_fn(mpi_process_regex):
        return lambda regex: re.compile(mpi_process_regex + regex)

    compile_re = compile_re_fn(process_regex)
    patterns = [(compile_re(k), v) for k, v in ogs_res]

    number_of_lines_read = 0
    with open(file_name) as file:
        lines = iter(file)
        records = list()
        for line in lines:
            number_of_lines_read += 1

            if (maximum_lines is not None) and (maximum_lines > number_of_lines_read):
                break

            for key, value in patterns:
                if r := try_match(line, number_of_lines_read, key, value):
                    records.append(value(*r))
                    break

    return records

