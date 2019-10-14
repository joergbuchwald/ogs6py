import numpy as np


class PROCESSES(object):
    def __init__(self, **args):
        self.tree = { 'processes': { 'tag': 'processes', 'text': '', 'attr': {}, 'children': {} } }
        self.tree['processes']['children'] = { 'process': { 'tag': 'process', 'text': '', 'attr': {}, 'children': {} } }
        self.constreltree = { 'tag': 'constitutive_relation', 'text': '', 'attr': {}, 'children': {} }
        self.proc_vartree = { 'tag': 'process_variables', 'text': '', 'attr': {}, 'children': {} }
        self.sec_vartree = { 'tag': 'secondary_variables', 'text': '', 'attr': {}, 'children': {} }

    def populateTree(self, tag, text='', attr={}, children={}):
        return { 'tag': tag, 'text': text, 'attr': attr, 'children': children }
    def addProcessVariable(self, **args):
        if "process_variable" in args:
            if "process_variable_name" in args:
                self.tree['processes']['children']['process']['children']['process_variables'] = self.proc_vartree
                self.proc_vartree['children'][args['process_variable']] = { 'tag': args['process_variable'], 'text': args['process_variable_name'], 'attr': {}, 'children': {} }
            else:
                raise KeyError("process_variable_name missing.")
        elif "secondary_variable" in args:
            if "type" in args:
                if "output_name" in args:
                    self.tree['processes']['children']['process']['children']['secondary_variables'] = self.sec_vartree
                    self.sec_vartree['children'][args['output_name']] = { 'tag': 'secondary_variable', 'text': '', 'attr': { 'type': args['type'], 'internal_name': args['secondary_variable'], 'output_name': args['output_name'] }, 'children': {} }

                else:
                    raise KeyError("No output_name given.")
            else:
                raise KeyError("type missing")
        else:
            raise KeyError("No process_variable/secondary_variable given.")

    def setProcess(self, **args):
        if "name" in args:
            if "type" in args:
                if "integration_order" in args:
                    for key in args:
                        self.tree['processes']['children']['process']['children'][key] = self.populateTree(
                                    key, text=args[key])

                else:
                    raise KeyError("integration_order missing.")
            else:
                raise KeyError("type missing.")
        else:
            raise KeyError("No process name given.")

    def setConstitutiveRelation(self, **args):
        self.tree['processes']['children']['process']['children']['constitutive_relation'] = self.constreltree
        for key in args:
            self.constreltree['children'][key] = { 'tag': key, 'text': args[key], 'attr': {}, 'children': {} }

    def setFluid(self, **args):
        pass

    def addPorousMedium(self, **args):
        pass
