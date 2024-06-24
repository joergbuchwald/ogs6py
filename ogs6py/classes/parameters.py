# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class Parameters(build_tree.BuildTree):
    """
    Class for managing the parameters section of the project file.
    """
    def __init__(self, tree):
        self.tree = tree
        self.root = self._get_root()
        self.parameters = self.populate_tree(self.root, 'parameters', overwrite=True)

    def add_parameter(self, **args):
        """
        Adds a parameter

        Parameters
        ----------
        name : `str`
        type : `str`
        value : `float` or `str`
        values : `float` or `str`
        expression : `str`
        curve : `str`
        parameter : `str`
        mesh : `str`
        field_name : `str`
        time : `list`
        parameter_name : `list`
        use_local_coordinate_system : `bool` or `str`
        """
        self._convertargs(args)
        if "name" not in args:
            raise KeyError("No parameter name given.")
        if "type" not in args:
            raise KeyError("Parameter type not given.")
        parameter = self.populate_tree(self.parameters, 'parameter')
        self.populate_tree(parameter, 'name', text=args['name'])
        self.populate_tree(parameter, 'type', text=args['type'])
        #entries = len(self.tree['parameters']['children'])
        #self.tree['parameters']['children'][
        #        'param' + str(entries)] = self.populate_tree('parameter',
        #                                                        children={})
        #parameter = self.tree['parameters']['children']['param' +
        #                                                        str(entries)]
        #parameter['children']['name'] = self.populate_tree(
        #            'name', text=args['name'], children={})
        #parameter['children']['type'] = self.populate_tree(
        #            'type', text=args['type'], children={})
        if args["type"] == "Constant":
            if "value" in args:
                self.populate_tree(parameter, 'value', text=args['value'])
            elif "values" in args:
                self.populate_tree(parameter, 'values', text=args['values'])
        elif args["type"] == "MeshElement" or args["type"] == "MeshNode":
            if 'mesh' in args:
                self.populate_tree(parameter, 'mesh', text=args['mesh'])
            self.populate_tree(parameter, 'field_name', text=args['field_name'])
        elif args["type"] == "Function":
            if "mesh" in args:
                self.populate_tree(parameter, 'mesh', text=args['mesh'])
            if isinstance(args['expression'], str) is True:
                self.populate_tree(parameter, 'expression', text=args['expression'])
            elif isinstance(args['expression'], list) is True:
                for i, entry in enumerate(args['expression']):
                    self.populate_tree(parameter, 'expression', text=entry)
        elif args["type"] == "CurveScaled":
            if "curve" in args:
                self.populate_tree(parameter, 'curve', text=args['curve'])
            if "parameter" in args:
                self.populate_tree(parameter, 'parameter', text=args['parameter'])
        elif args["type"] == "TimeDependentHeterogeneousParameter":
            if "time" not in args:
                raise KeyError("time missing.")
            if "parameter_name" not in args:
                raise KeyError("Parameter name missing.")
            if not len(args["time"]) == len(args["parameter_name"]):
                raise KeyError("parameter_name and time lists have different length.")
            time_series = self.populate_tree(parameter, 'time_series')
            for i, _ in enumerate(args["parameter_name"]):
                ts_pair = self.populate_tree(time_series, 'pair')
                self.populate_tree(ts_pair, 'time', text=args['time'][i])
                self.populate_tree(ts_pair, 'time', text=args['parameter_name'][i])
        else:
            raise KeyError("Parameter type not supported (yet).")
        if "use_local_coordinate_system" in args:
            if (args["use_local_coordinate_system"] == "true") or (
                    args["use_local_coordinate_system"] is True):
                self.populate_tree(parameter,
                      'use_local_coordinate_system', text='true')
