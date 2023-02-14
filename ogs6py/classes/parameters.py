# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
import numpy as np
from lxml import etree as ET
from ogs6py.classes import build_tree
from ogs6py.classes import parameter_type

class Parameters(build_tree.BuildTree):
    """
    Class for managing the parameters section of the project file.
    """
    def __init__(self, xmlobject=None, curvesobj=None, trafo_matrix=None):
        self.tree = {
            'parameters': {
                'tag': 'parameters',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.parameter = {}
        self.xmlobject = xmlobject
        self.curvesobj = curvesobj
        self.trafo_matrix = trafo_matrix
        if not (xmlobject is None):
            for prmt in xmlobject:
                for parameter_property in prmt:
                    if parameter_property.tag == "type":
                        param_type = parameter_property.text
                    elif parameter_property.tag == "name":
                        param_name = parameter_property.text
                if param_type == "Constant":
                    self.__dict__[param_name] = parameter_type.Constant(prmt, self, curvesobj, trafo_matrix)
                elif param_type == "Function":
                    self.__dict__[param_name] = parameter_type.Function(prmt, self, curvesobj, trafo_matrix)
                elif param_type == "MeshNode":
                    self.__dict__[param_name] = parameter_type.MeshNode(prmt, self, curvesobj,  trafo_matrix)
                elif param_type == "MeshElement":
                    self.__dict__[param_name] = parameter_type.MeshElement(prmt, self, curvesobj,  trafo_matrix)
                elif param_type == "CurveScaled":
                    self.__dict__[param_name] = parameter_type.CurveScaled(prmt, self, curvesobj, trafo_matrix)
#                elif param_type == "TimeDependentHeterogeneousParameter":
#                    self.__dict__[param_name] = parameter_type.TimeDependentHeterogeneousParameter(prmt)
                elif param_type == "RandomFieldMeshElementParameter":
                    self.__dict__[param_name] = parameter_type.RandomFieldMeshElementParameter(prmt, self, curvesobj, trafo_matrix)
#                elif param_type == "Group":
#                    self.__dict__[param_name] = parameter_type.Group(prmt)

    def __checkparameter(self, dictionary):
        required = {"Constant": ["name", "type"],
               "Function": ["name", "type", "expression"],
               "MeshNode": ["name", "type", "field_name"],
               "MeshElement": ["name", "type", "field_name"],
               "CurvedScaled": ["name", "type", "curve", "parameter"],
               "TimeDependentHeterogeneousParameter": ["name", "type", "time_series"],
               "RandomFieldMeshElementParameter": ["name", "type","field_name", "range", "seed"],
               "Group": ["name", "type", "group_id_property"]}
        optional =  {"Constant": ["value", "values"],
               "Function": ["mesh"],
               "MeshNode": ["mesh"],
               "MeshElement": ["mesh"],
               "CurvedScaled": ["mesh"],
               "TimeDependentHeterogeneousParameter": ["mesh"],
               "RandomFieldMeshElementParameter": ["mesh"],
               "Group": ["mesh"]}
        for k, v in dictionary.items():
            if not k in (required[dictionary["type"]]+optional[dictionary["type"]]):
                raise RuntimeError(f"{k} is not a valid property field for the specified type.")
        for entry in required[dictionary["type"]]:
            if not entry in dictionary:
                raise RuntimeError(f"{entry} is required for the specified type.")
        if dictionary["type"] == "Constant":
            if not (("value" in dictionary) or ("values" in dictionary)):
                raise RuntimeError("The Constant parameter requires value or values to be specified.")


    def __setitem__(self, key, item):
        if not isinstance(item, dict):
            raise RuntimeError("Item must be a dictionary")
        if len(item) == 0:
            self.__delitem__(key)
            return
        self.__checkparameter(item)
        if key in self.__dict__:
            self.__delitem__(key)
        prmt_obj = ET.SubElement(self.xmlobject, "parameter")
        for k, v  in item.items():
            if k == "expression":
                q = []
                for subentry in v:
                    q.append(ET.SubElement(prmt_obj, "expression"))
                    q[-1].text = subentry
            else:
                q = ET.SubElement(prmt_obj, k)
                q.text = v
        if item["type"] == "Constant":
            self.__dict__[key] = parameter_type.Constant(prmt_obj, self, self.curvesobj, self.trafo_matrix)
        elif item["type"] == "Function":
            self.__dict__[key] = parameter_type.Function(prmt_obj, self, self.curvesobj, self.trafo_matrix)
        elif item["type"] == "MeshNode":
            self.__dict__[key] = parameter_type.MeshNode(prmt_obj, self, self.curvesobj, self.trafo_matrix)
        elif item["type"] == "MeshElement":
            self.__dict__[key] = parameter_type.MeshElement(prmt_obj,self, self.curvesobj, self.trafo_matrix)
        elif item["type"] == "CurveScaled":
            self.__dict__[key] = parameter_type.CurveScaled(prmt_obj, self, self.curvesobj, self.trafo_matrix)
#       elif item["type"] == "TimeDependentHeterogeneousParameter":
#           self.__dict__[param_name] = parameter_type.TimeDependentHeterogeneousParameter(prmt)
        elif item["type"] == "RandomFieldMeshElementParameter":
            self.__dict__[key] = parameter_type.RandomFieldMeshElementParameter(prmt_obj, self, self.curvesobj, self.trafo_matrix)
#       elif item["type"] == "Group":
#           self.__dict__[param_name] = parameter_type.Group(prmt)
        return prmt_obj


    def __getitem__(self, key):
        if not (key in ["tree", "parameter", "xmlobject", "curvesobj", "trafo_matrix"]):
            return self.__dict__[key]

    def __repr__(self):
        newdict = dict()
        for k, v in self.__dict__.items():
            if not (k in ["tree", "parameter", "name", "xmlobject", "curvesobj", "trafo_matrix"]):
                newdict[k] = v
        return repr(newdict)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        obj = self.__dict__[key].xmlobject
        obj.getparent().remove(obj)
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        if not (k in ["tree", "parameter", "xmlobject", "curvesobj", "trafo_matrix"]):
            return k in self.__dict__

    def update(self, *args, **kwargs):
        pass
        # return self.__dict__.update(*args, **kwargs)

    def keys(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "parameter", "xmlobject", "curvesobj", "trafo_matrix"]):
                newdict[k] = v
        return newdict.keys()

    def values(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "parameter", "xmlobject", "curvesobj", "trafo_matrix"]):
                newdict[k] = v
        return newdict.values()

    def items(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "parameter", "xmlobject", "curvesobj", "trafo_matrix"]):
                newdict[k] = v
        return newdict.items()

    def pop(self, *args):
        pass
        #return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "parameter", "xmlobject", "curvesobj", "trafo_matrix"]):
                newdict[k] = v
        return item in newdict

    def __iter__(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "parameter", "xmlobject", "curvesobj", "trafo_matrix"]):
                newdict[k] = v
        return iter(newdict)

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
        entries = len(self.tree['parameters']['children'])
        self.tree['parameters']['children'][
                'param' + str(entries)] = self.populate_tree('parameter',
                                                                children={})
        parameter = self.tree['parameters']['children']['param' +
                                                                str(entries)]
        parameter['children']['name'] = self.populate_tree(
                    'name', text=args['name'], children={})
        parameter['children']['type'] = self.populate_tree(
                    'type', text=args['type'], children={})
        if args["type"] == "Constant":
            if "value" in args:
                parameter['children']['value'] = self.populate_tree(
                        'value', text=args['value'], children={})
            elif "values" in args:
                parameter['children']['values'] = self.populate_tree(
                        'values', text=args['values'], children={})
        elif args["type"] == "MeshElement" or args["type"] == "MeshNode":
            parameter['children']['mesh'] = self.populate_tree(
                        'mesh', text=args['mesh'], children={})
            parameter['children']['field_name'] = self.populate_tree(
                        'field_name', text=args['field_name'], children={})
        elif args["type"] == "Function":
            if "mesh" in args:
                parameter['children']['mesh'] = self.populate_tree(
                        'mesh', text=args['mesh'], children={})
            if isinstance(args['expression'],str) is True:
                parameter['children']['expression'] = self.populate_tree(
                        'expression', text=args['expression'], children={})
            elif isinstance(args['expression'],list) is True:
                for i, entry in enumerate(args['expression']):
                    parameter['children'][f'expression{i}'] = self.populate_tree(
                        'expression', text=entry, children={})
        elif args["type"] == "CurveScaled":
            if "curve" in args:
                parameter['children']['curve'] = self.populate_tree(
                        'curve', text=args['curve'], children={})
            if "parameter" in args:
                parameter['children']['parameter'] = self.populate_tree(
                        'parameter', text=args['parameter'], children={})
        elif args["type"] == "TimeDependentHeterogeneousParameter":
            if "time" not in args:
                raise KeyError("time missing.")
            if "parameter_name" not in args:
                raise KeyError("Parameter name missing.")
            if not len(args["time"]) == len(args["parameter_name"]):
                raise KeyError("parameter_name and time lists have different length.")
            parameter['children']['time_series'] = self.populate_tree('time_series', children={})
            ts_pair = parameter['children']['time_series']['children']
            for i, _ in enumerate(args["parameter_name"]):
                ts_pair['pair' + str(i)] = self.populate_tree('pair', children={})
                ts_pair['pair' + str(i)]['children']['time'] = self.populate_tree(
                        'time', text=str(args["time"][i]), children={})
                ts_pair['pair' + str(i)]['children']['parameter_name'] = self.populate_tree(
                        'parameter_name', text=args["parameter_name"][i], children={})
        else:
            raise KeyError("Parameter type not supported (yet).")
        if "use_local_coordinate_system" in args:
            if (args["use_local_coordinate_system"] == "true") or (
                    args["use_local_coordinate_system"] is True):
                parameter['children']['use_local_coordinate_system'] = self.populate_tree(
                      'use_local_coordinate_system', text='true', children={})
