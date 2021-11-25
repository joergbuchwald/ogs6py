#!/usr/bin/env python

# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
#            Distributed under a Modified BSD License.
#              See accompanying file LICENSE.txt or
#              http://www.opengeosys.org/project/license

import re
import sys
import pandas as pd


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


def parse_file(file_name, ogs_res, maximum_lines=None, petsc=True):
    if petsc:
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

            for k, v in patterns:
                if r := try_match(line, number_of_lines_read, k, v):
                    records.append(v(*r))
                    break

        # TODO parse all DEBUG outputs in c++ sources and generate a full list
        # records.append(UnknownLine(line))
    return records


if __name__ == "__main__":
    import ogs_regexes
    filename = sys.argv[1]
    data = parse_file(sys.argv[1], ogs_regexes.ogs_regexes(), maximum_lines=None, petsc=True)
    df = pd.DataFrame(data)
    filename_prefix = filename.split('.')[0]
    df.to_csv(f"{filename_prefix}.csv")
