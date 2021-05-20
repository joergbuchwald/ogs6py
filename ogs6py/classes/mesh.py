# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class Mesh(build_tree.BuildTree):
    """
    Class for defining meshes in the project file.
    """
    def __init__(self):
        self.meshfiles = []
        self.axially_symmetric = []

    @classmethod
    def _check_ax_sym(cls, args):
        axsym = "false"
        if "axially_symmetric" in args:
            if isinstance(args["axially_symmetric"], bool):
                if args["axially_symmetric"] is True:
                    axsym = "true"
            else:
                axsym = args["axially_symmetric"]
        return axsym

    def add_mesh(self, **args):
        """
        adds a mesh to the project file

        Parameters
        ----------
        filename : `str`
        axially_syymetric : `bool` or `str`
        """
        if "filename" not in args:
            raise KeyError("No filename given")
        self.meshfiles.append((args["filename"], self._check_ax_sym(args)))


    @property
    def tree(self):
        baum = {'meshes': {}}
        if len(self.meshfiles) == 1:
            if self.meshfiles[0][1] == "false":
                baum['meshes'] = self.populate_tree('mesh', text=self.meshfiles[0][0])
            else:
                baum['meshes'] = self.populate_tree('mesh', text=self.meshfiles[0][0],
                        attr={'axially_symmetric': 'true'})
        else:
            baum['meshes'] = self.populate_tree('meshes')
            for i, meshfile in enumerate(self.meshfiles):
                if meshfile[1] == "false":
                    baum['meshes']['children'][i] = self.populate_tree('mesh', text=meshfile[0],
                            children={})
                else:
                    baum['meshes']['children'][i] = self.populate_tree('mesh', text=meshfile[0],
                            attr={'axially_symmetric': 'true'}, children={})
        return baum
