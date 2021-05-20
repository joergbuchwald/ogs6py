# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class Processes(build_tree.BuildTree):
    """
    Class for managing the processes section in the project file.
    """
    def __init__(self):
        self.tree = {
            'processes': {
                'tag': 'processes',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.tree['processes']['children'] = {
            'process': {
                'tag': 'process',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.constreltree = {
            'tag': 'constitutive_relation',
            'text': '',
            'attr': {},
            'children': {}
        }
        self.proc_vartree = {
            'tag': 'process_variables',
            'text': '',
            'attr': {},
            'children': {}
        }
        self.sec_vartree = {
            'tag': 'secondary_variables',
            'text': '',
            'attr': {},
            'children': {}
        }

    def add_process_variable(self, **args):
        """
        Adds a process variable.

        Parameters
        ----------
        process_variable : `str`
        process_variable_name : `str`
        secondary_variable : `str`
        output_name : `str`
        """
        self._convertargs(args)
        if "process_variable" in args:
            if "process_variable_name" not in args:
                raise KeyError("process_variable_name missing.")
            self.tree['processes']['children']['process']['children'][
                    'process_variables'] = self.proc_vartree
            self.proc_vartree['children'][args['process_variable']] = {
                    'tag': args['process_variable'],
                    'text': args['process_variable_name'],
                    'attr': {},
                    'children': {}
                    }
        elif "secondary_variable" in args:
            if "output_name" not in args:
                raise KeyError("No output_name given.")
            self.tree['processes']['children']['process']['children'][
                    'secondary_variables'] = self.sec_vartree
            self.sec_vartree['children'][args['output_name']] = {
                    'tag': 'secondary_variable',
                    'text': '',
                    'attr': {
                        'internal_name': args['secondary_variable'],
                        'output_name': args['output_name']
                        },
                    'children': {}
                    }
        else:
            raise KeyError("No process_variable/secondary_variable given.")

    def set_process(self, **args):
        """
        Set basic process properties.

        Parameters
        ----------
        name : `str`
        type : `str`
        integration_order : `str`
        darcy_gravity : `list` or `tuple`
                        holding darcy accelleration as vector
        any pair tag="value" translates to
        <tag>value</tag> in process section
        """
        self._convertargs(args)
        if "name" not in args:
            raise KeyError("No process name given.")
        if "type" not in args:
            raise KeyError("type missing.")
        if "integration_order" not in args:
            raise KeyError("integration_order missing.")
        if "darcy_gravity" in args:
            for i, entry in enumerate(args["darcy_gravity"]):
                if entry != 0.0:
                    self.tree['processes']['children']['process'][
                        'children']['darcy_gravity'] = self.populate_tree('darcy_gravity')
                    darcy_vel = self.tree['processes']['children']['process'][
                                    'children']['darcy_gravity']
                    darcy_vel['children']['axis'] = self.populate_tree('axis_id', text=str(i))
                    darcy_vel['children']['g'] = self.populate_tree('g', text=str(entry))

        for key, value in args.items():
            if isinstance(value, str):
                self.tree['processes']['children']['process'][
                    'children'][key] = self.populate_tree(key, text=args[key])


    def set_constitutive_relation(self, **args):
        """
        Sets constituitive relation

        Parameters
        ----------

        any pair tag="value" translates to
        <tag>value</tag> in process section
        """
        self._convertargs(args)
        self.tree['processes']['children']['process']['children'][
            'constitutive_relation'] = self.constreltree
        for key in args:
            self.constreltree['children'][key] = {
                'tag': key,
                'text': args[key],
                'attr': {},
                'children': {}
            }
