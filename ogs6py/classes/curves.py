# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2023, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from lxml import etree as ET
from ogs6py.classes import build_tree
from ogs6py.classes import curve

class Curves(build_tree.BuildTree):
    """
    Class to create the curve section of the project file.
    """
    def __init__(self, xmlobject=None):
        self.tree = {
            'curves': {
                'tag': 'curves',
                'text': '',
                'attr': {},
                'children': {}
            }
        }
        self.xmlobject = xmlobject
        if not (xmlobject is None):
            for curve_obj in xmlobject:
                for curve_property in curve_obj:
                    if curve_property.tag == "name":
                        curve_name = curve_property.text
                self.__dict__[curve_name] = curve.Curve(curve_obj)

    def __checkcurve(self, dictionary):
        required = ["coords", "values"]
        optional = ["name"]
        for k, v in dictionary.items():
            if not k in (required+optional):
                raise RuntimeError(f"{k} is not a valid property field for a curve.")
        for entry in required:
            if not entry in dictionary:
                raise RuntimeError(f"{entry} is required for creating a curve.")

    def __setitem__(self, key, item):
        if not isinstance(item, dict):
            raise RuntimeError("Item must be a dictionary")
        if len(item) == 0:
            self.__delitem__(key)
            return
        self.__checkcurve(item)
        if key in self.__dict__:
            self.__delitem__(key)
        curve_obj = ET.SubElement(self.xmlobject, "curve")
        assert(len(item["coords"])==len(item["values"]))
        for i, entry in enumerate(item["coords"]):
           item["coords"][i] = str(entry)
           item["values"][i] = str(item["values"][i])
        q = ET.SubElement(curve_obj, "name")
        q.text = key
        q = ET.SubElement(curve_obj, "coords")
        q.text = ' '.join(item["coords"])
        q = ET.SubElement(curve_obj, "values")
        q.text = ' '.join(item["values"])
        return curve_obj


    def __getitem__(self, key):
        if not (key in ["tree", "xmlobject"]):
            return self.__dict__[key]

    def __repr__(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "name", "xmlobject"]):
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
        if not (k in ["tree","xmlobject"]):
            return k in self.__dict__

    def update(self, *args, **kwargs):
        pass
        # return self.__dict__.update(*args, **kwargs)

    def keys(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree","xmlobject"]):
                newdict[k] = v
        return newdict.keys()

    def values(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "xmlobject"]):
                newdict[k] = v
        return newdict.values()

    def items(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "xmlobject"]):
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
            if not (k in ["tree", "xmlobject"]):
                newdict[k] = v
        return item in newdict

    def __iter__(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["tree", "xmlobject"]):
                newdict[k] = v
        return iter(newdict)

    def add_curve(self, **args):
        """
        Adds a new curve.

        Parameters
        ----------
        name : `str`
        coords : `list`
        values : `list`
        """
        if "name" not in args:
            raise KeyError("No curve name given.")
        if "coords" not in args:
            raise KeyError("No coordinates given.")
        if "values" not in args:
            raise KeyError("No values given.")
        if len(args["coords"]) != len(args["values"]):
            raise ValueError("Number of time coordinate points differs from number of values")
        entries = len(self.tree['curves']['children'])
        self.tree['curves']['children']['curve' + str(entries)] = self.populate_tree('curve',
                children={})
        parameter = self.tree['curves']['children']['curve' + str(entries)]
        parameter['children']['name'] = self.populate_tree('name', text=args['name'], children={})
        coord_str = ""
        value_str = ""
        for i, coord in enumerate(args["coords"]):
            if i < (len(args["coords"])-1):
                coord_str = coord_str + str(coord) + " "
                value_str = value_str + str(args["values"][i]) + " "
            if i == (len(args["coords"])-1):
                coord_str = coord_str + str(coord)
                value_str = value_str + str(args["values"][i])
        parameter['children']['coords'] = self.populate_tree('coords', text=coord_str, children={})
        parameter['children']['values'] = self.populate_tree('values', text=value_str, children={})
