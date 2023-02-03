# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2023, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
from fastcore.utils import *
import numpy as np
from lxml import etree as ET
# pylint: disable=C0103, R0902, R0914, R0913

class Curve:
    def __init__(self, xmlobject:object=None) -> None:
        self.__dict__ = {}
        self.xmlobject = xmlobject
        if not self.xmlobject is None:
            for curve_property in self.xmlobject:
                if curve_property.tag == "name":
                    self.__dict__[curve_property.tag] = curve_property.text
                else:
                    self.__dict__[curve_property.tag] = curve_property.text.split(" ")
            assert(len(self.__dict__["coords"])==len(self.__dict__["values"]))

    def __setitem__(self, key, item):
        if not key in self.__dict__:
            raise RuntimeError("property is not existing")
        expression_counter = -1
        if key in ["coords", "values"]:
            for i, entry in enumerate(item):
                item[i] = str(entry)
            for curve_property in self.xmlobject:
                if curve_property.tag == key:
                    curve_property.text = ' '.join(item)
        else:
            for curve_property in self.xmlobject:
                if curve_property.tag == key:
                    curve_property.text = item

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

    def evaluate_values(self,x):
        coords = np.array([float(val) for val in self.__dict__["coords"]])
        values = np.array([float(val) for val in self.__dict__["values"]])
        return np.interp(x, coords, values)
