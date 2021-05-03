# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class PROCESSES(build_tree.BUILD_TREE):
    def __init__(self, **args):
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

    def addProcessVariable(self, **args):
        self._convertargs(args)
        if "process_variable" in args:
            if not "process_variable_name" in args:
                raise KeyError("process_variable_name missing.")
            else:
                self.tree['processes']['children']['process']['children'][
                    'process_variables'] = self.proc_vartree
                self.proc_vartree['children'][args['process_variable']] = {
                    'tag': args['process_variable'],
                    'text': args['process_variable_name'],
                    'attr': {},
                    'children': {}
                }
        elif not "secondary_variable" in args:
            raise KeyError("No process_variable/secondary_variable given.")
        else:
            if not "output_name" in args:
                raise KeyError("No output_name given.")
            else:
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

    def setProcess(self, **args):
        self._convertargs(args)
        if not "name" in args:
            raise KeyError("No process name given.")
        else:
            if not "type" in args:
                raise KeyError("type missing.")
            else:
                if not "integration_order" in args:
                    raise KeyError("integration_order missing.")
                else:
                    if "darcy_gravity" in args:
                        for i, entry in enumerate(args["darcy_gravity"]):
                            if entry != 0.0:
                                self.tree['processes']['children']['process'][
                                    'children']['darcy_gravity'] = self.populateTree('darcy_gravity')
                                darcy_vel = self.tree['processes']['children']['process'][
                                    'children']['darcy_gravity']
                                darcy_vel['children']['axis'] = self.populateTree('axis_id', text=str(i))
                                darcy_vel['children']['g'] = self.populateTree('g', text=str(entry))

                    for key, value in args.items():
                        if type(value) == str:
                            self.tree['processes']['children']['process'][
                                'children'][key] = self.populateTree(
                                key, text=args[key])


    def setConstitutiveRelation(self, **args):
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

    def setFluid(self, **args):
        pass

    def addPorousMedium(self, **args):
        pass
