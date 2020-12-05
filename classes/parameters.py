class PARAMETERS(object):
    def __init__(self, **args):
        self.tree = {
            'parameters': {
                'tag': 'parameters',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def _convertargs(self, args):
        for item in args:
            args[item] = str(args[item])

    def populateTree(self, tag, text='', attr={}, children={}):
        return {'tag': tag, 'text': text, 'attr': attr, 'children': children}

    def addParameter(self, **args):
        self._convertargs(args)
        if not "name" in args:
            raise KeyError("No parameter name given.")
        else:
            if not "type" in args:
                raise KeyError("Parameter type not given.")
            else:
                entries = len(self.tree['parameters']['children'])
                self.tree['parameters']['children'][
                    'param' + str(entries)] = self.populateTree('parameter',
                                                                children={})
                parameter = self.tree['parameters']['children']['param' +
                                                                str(entries)]
                parameter['children']['name'] = self.populateTree(
                    'name', text=args['name'], children={})
                parameter['children']['type'] = self.populateTree(
                    'type', text=args['type'], children={})
                if args["type"] == "Constant":
                    if "value" in args:
                        parameter['children']['value'] = self.populateTree(
                            'value', text=args['value'], children={})
                    elif "values" in args:
                        parameter['children']['values'] = self.populateTree(
                            'values', text=args['values'], children={})
                elif args["type"] == "MeshElement" \
                        or args["type"] == "MeshNode":
                    parameter['children']['mesh'] = self.populateTree(
                        'mesh', text=args['mesh'], children={})
                    parameter['children']['field_name'] = self.populateTree(
                        'field_name', text=args['field_name'], children={})
                elif args["type"] == "Function":
                    parameter['children']['expression'] = self.populateTree(
                        'expression', text=args['expression'], children={})
                elif args["type"] == "CurveScaled":
                    if "curve" in args:
                        parameter['children']['curve'] = self.populateTree(
                        'curve', text=args['curve'], children={})
                    if "parameter" in args:
                        parameter['children']['parameter'] = self.populateTree(
                        'parameter', text=args['parameter'], children={})
                elif args["type"] == "TimeDependentHeterogeneousParameter":
                    if "time" in args:
                        if "parameter_name" in args:
                            if len(args["time"]) == len(args["parameter_name"]):
                                parameter['children']['time_series'] = self.populateTree('time_series', children={})
                                ts_pair = parameter['children']['time_series']['children']
                                for i, repeat in enumerate(args["parameter_name"]):
                                    ts_pair['pair' + str(i)] = self.populateTree('pair',
                                                             children={})
                                    ts_pair['pair' + str(i)]['children']['time'] = self.populateTree(
                                        'time', text=str(args["time"][i]), children={})
                                    ts_pair['pair' + str(i)]['children']['parameter_name'] = self.populateTree(
                                                        'parameter_name', text=args["parameter_name"][i],
                                        children={})
                            else:
                                raise KeyError("parameter_name and time lists have different length.")
                        else:
                            raise KeyError("Parameter name missing.")
                    else:
                        raise KeyError("time missing.")
                else:
                    raise KeyError("Parameter type not supported (yet).")
                if "use_local_coordinate_system" in args:
                    if (args["use_local_coordinate_system"] == "true") or (args["use_local_coordinate_system"] == True):
                        parameter['children']['use_local_coordinate_system'] = self.populateTree(
                      'use_local_coordinate_system', text='true', children={})
