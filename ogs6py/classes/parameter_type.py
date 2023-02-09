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
try:
    import vtuIO
    has_vtuinterface = True
except ImportError:
    has_vtuinterface = False
try:
    import cexprtk
    has_cexprtk = True
except ImportError:
    has_cexprtk = False

# pylint: disable=C0103, R0902, R0914, R0913

class Parameter_type:
    def __init__(self, xmlobject:object=None, curvesobj=None) -> None:
        self.__dict__ = {}
        self.xmlobject = xmlobject
        self.curvesobj = curvesobj
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
                    parameter_property.text = str(item)

    def __getitem__(self, key):
        if not (key in ["xmlobject", "curvesobj"]):
            return self.__dict__[key]

    def __repr__(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["xmlobject", "curvesobj"]):
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
        if not (k in ["xmlobject", "curvesobj"]):
            return k in self.__dict__

    def update(self, *args, **kwargs):
        pass
        # return self.__dict__.update(*args, **kwargs)

    def keys(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["xmlobject", "curvesobj"]):
                newdict[k] = v
        return newdict.keys()

    def values(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["xmlobject", "curvesobj"]):
                newdict[k] = v
        return newdict.values()

    def items(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["xmlobject", "curvesobj"]):
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
            if not (k in ["xmlobject", "curvesobj"]):
                newdict[k] = v
        return item in newdict

    def __iter__(self):
        newdict = {}
        for k, v in self.__dict__.items():
            if not (k in ["xmlobject", "curvesobj"]):
                newdict[k] = v
        return iter(newdict)

class Constant(Parameter_type):
    def evaluate_values(self):
        if "values" in self.__dict__:
            return self.__dict__["values"]
        else:
            return self.__dict__["value"]

class Function(Parameter_type):
    def evaluate_values(self, t=0):
        if has_vtuinterface is False:
            raise RuntimeError("VTUinterface is not installed")
        if has_cexprtk is False:
            raise RuntimeError("cexprtk is not installed")
        try:
            mesh = self.__dict__["mesh"]
            meshfiles = self.xmlobject.getparent().getparent().findall("./mesh")
            for file in meshfiles:
                if mesh in file.text:
                    meshfile = file.text
        except KeyError:
            meshfile = self.xmlobject.getparent().getparent().find("./mesh").text
        m = vtuIO.VTUIO(meshfile)
        st = cexprtk.Symbol_Table({'x': 0.0, 'y': 0.0, 'z': 0.0, 't': t}, add_constants=True)
        try:
            for curve in self.curvesobj.keys():
                st.functions[curve] = self.curvesobj[curve].evaluate_values
        except:
            pass
        dim1 = len(m.points)
        dim2 = len(self.__dict__["expression"])
        if dim2 == 1:
            array = np.zeros(dim1)
            evaluate = cexprtk.Expression(self.__dict__["expression"][0], st)
            for  i in range(dim1):
                st.variables["x"] = m.points[i][0]
                st.variables["y"] = m.points[i][1]
                st.variables["z"] = m.points[i][2]
                array[i] = evaluate()
        else:
            array = np.zeros((dim1, dim2))
            evaluate = []
            for i in range(dim2):
                evaluate.append(cexprtk.Expression(self.__dict__["expression"][i], st))
            for i in range(dim1):
                for j in range(dim2):
                    st.variables["x"] = m.points[i][0]
                    st.variables["y"] = m.points[i][1]
                    st.variables["z"] = m.points[i][2]
                    array[i,j]=evaluate[j]()
        return m.points, array, m


class MeshNode(Parameter_type):
    def evaluate_values(self):
        if has_vtuinterface is False:
            raise RuntimeError("vtuIO is not installed")
        try:
            mesh = self.__dict__["mesh"]
            meshfiles = self.xmlobject.getparent().getparent().findall("./mesh")
            for file in meshfiles:
                if mesh in file.text:
                    meshfile = file.text
        except KeyError:
            meshfile = self.xmlobject.getparent().getparent().find("./mesh")
        m = vtuIO.VTUIO(meshfile)
        array = m.get_point_field(self.__dict__["field_name"])
        return m.points, array, m

class MeshElement(Parameter_type):
    def evaluate_values(self):
        if has_vtuinterface is False:
            raise RuntimeError("vtuIO is not installed")
        try:
            mesh = self.__dict__["mesh"]
            meshfiles = self.xmlobject.getparent().getparent().findall("./mesh")
            for file in meshfiles:
                if mesh in file.text:
                    meshfile = file.text
        except KeyError:
            meshfile = self.xmlobject.getparent().getparent().find("./mesh")
        m = vtuIO.VTUIO(meshfile)
        array = m.get_cell_field(self.__dict__["field_name"])
        return m.cell_center_points, array, m

class CurveScaled(Parameter_type):
    def evaluate_values(self, curve_coords=None):
        if curve_coords is None:
            t_start = self.xmlobject.getparent().getparent().find("./time_loop/processes/process/time_stepping/t_initial")
            t_end = self.xmlobject.getparent().getparent().find("./time_loop/processes/process/time_stepping/t_end")
            curve_coords = np.linspace(t_start, t_end, 1000, endpoint=True)
        return

#class TimeDependentHeterogeneousParameter(Parameter_type):
#    pass

class RandomFieldMeshElementParameter(Parameter_type):
    pass
#class Group(Parameter_type):
#    pass