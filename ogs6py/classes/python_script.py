# -*- coding: utf-8 -*-
"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""
# pylint: disable=C0103, R0902, R0914, R0913
from ogs6py.classes import build_tree

class PYTHON_SCRIPT(build_tree.BUILD_TREE):
    """
    Class managing python script in the project file
    """
    def __init__(self):
        self.tree = {
            'pythonscript': {
                'tag': 'python_script',
                'text': "",
                'attr': {},
                'children': {}
            }
        }

    def setPyscript(self, **args):
        """
        Set a filename for a python script.

        Parameters
        ----------
        filename : `str`
        """
        self._convertargs(args)
        if "filename" not in args:
            raise KeyError("No filename given")
        self.tree['pythonscript']['text'] = args['filename']
