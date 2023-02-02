# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2023, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
from fastcore.utils import *
from lxml import etree as ET


# pylint: disable=C0103, R0902, R0914, R0913

class Parameter_type:
    def __init__(self, xmlobject:object=None) -> None:
        self.__dict__ = {}
        self.xmlobject = xmlobject
        if not self.xmlobject is None:
            for parameter_property in self.xmlobject:
                if parameter_property.tag == "expression":
                    try:
                        self.__dict__["expression"].append(parameter_property.text)
                    except:
                        self.__dict__["expression"] = []
                        self.__dict__["expression"].append(parameter_property.text)
                else:
                    self.__dict__[parameter_property.tag] = parameter_property.text
    def __setitem__(self, key, item):
        if not key in self.__dict__:
            raise RuntimeError("property is not existing")
        if key == "type":
            raise RuntimeError("The Type can't be changed.")
        expression_counter = -1
        for parameter_property in self.xmlobject:
            if parameter_property.tag == key:
                if key == "expression":
                    expression_counter += 1
                    parameter_property.text = str(item[expression_counter])
                else:
                    parameter_property.text = (item)

    def __getitem__(self, key):
        if not (key == "xmlobject"):
            return self.__dict__[key]

    def __repr__(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k == "xmlobject"):
                newdict[k] = v
        return repr(newdict)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        pass
        #del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        if not (k == "xmlobject"):
            return k in self.__dict__

    def update(self, *args, **kwargs):
        pass
        # return self.__dict__.update(*args, **kwargs)

    def keys(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k == "xmlobject"):
                newdict[k] = v
        return newdict.keys()

    def values(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k == "xmlobject"):
                newdict[k] = v
        return newdict.values()

    def items(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k == "xmlobject"):
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
            if not (k == "xmlobject"):
                newdict[k] = v
        return item in newdict

    def __iter__(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k == "xmlobject"):
                newdict[k] = v
        return iter(newdict)

class Constant(Parameter_type):
    pass

class Function(Parameter_type):
    pass

class MeshNode(Parameter_type):
    pass

class MeshElement(Parameter_type):
    pass

class CurveScaled(Parameter_type):
    pass

class TimeDependentHeterogeneousParameter(Parameter_type):
    pass

class RandomFieldMeshElementParameter(Parameter_type):
    pass
class Group(Parameter_type):
    pass