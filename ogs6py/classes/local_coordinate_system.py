# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
import numpy as np
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class LocalCoordinateSystem(build_tree.BuildTree):
    """
    Class for defining a local coordinate system in the project file"
    """
    def __init__(self, xmlobject=None):
        self.tree = {
            'local_coordinate_system': {
                'tag': 'local_coordinate_system',
                'text': "",
                'attr': {},
                'children': {}
            }
        }
        self.xmlobject = xmlobject
        self.R = None
        if not self.xmlobject is None:
            basis_vectors = self.xmlobject.getchildren()
            dim = len(basis_vectors)
            self.R = np.zeros((dim,dim))
            basis_vector_names = []
            for vec in basis_vectors:
                basis_vector_names.append(vec.text)
            basis_vector_values = []
            for vec in basis_vector_names:
                basis_vector_values.append(np.fromstring(self.xmlobject.getparent().find(f"./parameters/parameter[name='{vec}']/values").text, sep=' '))
            for i in range(dim):
                for j in range(dim):
                    self.R[i,j] = basis_vector_values[i][j]

    def add_basis_vec(self, **args):
        """
        Adds a basis

        Parameters
        ----------
        basis_vector_0 : `str`
                         name of the parameter containing the basis vector
        basis_vector_1 : `str`
                         name of the parameter containing the basis vector
        basis_vector_2 : `str`
                         name of the parameter containing the basis vector
        """
        self._convertargs(args)
        if "basis_vector_0" not in args:
            raise KeyError("no vector given")
        self.tree['local_coordinate_system']['children'] = {
                'basis_vector_0': {
                'tag': 'basis_vector_0',
                'text': args["basis_vector_0"],
                'attr': {},
                'children': {}}}
        if "basis_vector_1" in args:
            self.tree['local_coordinate_system']['children']['basis_vector_1'] = {
                    'tag': 'basis_vector_1',
                    'text': args["basis_vector_1"],
                    'attr': {},
                    'children': {}}
        if "basis_vector_2" in args:
            self.tree['local_coordinate_system']['children']['basis_vector_2'] = {
                'tag': 'basis_vector_2',
                'text': args["basis_vector_2"],
                'attr': {},
                'children': {}}
