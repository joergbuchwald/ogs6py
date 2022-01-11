# -*- coding: utf-8 -*-
"""
ogs6py is a python-API for the OpenGeoSys finite element sofware.
Its main functionalities include creating and altering OGS6 input files as well as executing OGS.

Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""

# pylint: disable=C0103, R0902, R0914, R0913
import sys
import os
import subprocess
import time
import shutil
import pandas as pd
from lxml import etree as ET
from ogs6py.classes import (geo, mesh, python_script, processes, media, timeloop,
        local_coordinate_system, parameters, curves, processvars, linsolvers, nonlinsolvers)
import ogs6py.log_parser.log_parser as parser
import ogs6py.log_parser.common_ogs_analyses as parse_fcts

class OGS:
    """Class for an OGS6 model.

    In this class everything for an OGS5 model can be specified.

    Parameters
    ----------
    PROJECT_FILE : `str`, optional
        Filename of the output project file
        Default: default.prj
    INPUT_FILE : `str`, optional
        Filename of the input project file
    XMLSTRING : `str`,optional
    OMP_NUM_THREADS : `int`, optional
        Sets the envirornvariable befaure OGS execution to restrict number of OMP Threads
    """
    def __init__(self, **args):
        self.geo = geo.Geo()
        self.mesh = mesh.Mesh()
        self.pyscript = python_script.PythonScript()
        self.processes = processes.Processes()
        self.media = media.Media()
        self.timeloop = timeloop.TimeLoop()
        self.local_coordinate_system = local_coordinate_system.LocalCoordinateSystem()
        self.parameters = parameters.Parameters()
        self.curves = curves.Curves()
        self.processvars = processvars.ProcessVars()
        self.linsolvers = linsolvers.LinSolvers()
        self.nonlinsolvers = nonlinsolvers.NonLinSolvers()
        sys.setrecursionlimit(10000)
        self.tag = []
        self.logfile = "out.log"
        self.tree = None
        self.include_elements = []
        self.include_files = []
        self.add_blocks = []
        self.add_entries = []
        self.add_includes = []
        if "OMP_NUM_THREADS" in args:
            self.threads = args["OMP_NUM_THREADS"]
        else:
            self.threads = None
        if "PROJECT_FILE" in args:
            self.prjfile = args['PROJECT_FILE']
        else:
            print("PROJECT_FILE not given. Calling it default.prj.")
            self.prjfile = "default.prj"
        if "INPUT_FILE" in args:
            if os.path.isfile(args['INPUT_FILE']) is True:
                self.inputfile = args['INPUT_FILE']
                _ = self._get_root()
            else:
                raise RuntimeError(f"Input project file {args['INPUT_FILE']} not found.")
        else:
            self.inputfile = None
        if "XMLSTRING" in args:
            root = ET.fromstring(args['XMLSTRING'])
            self.tree = ET.ElementTree(root)

    def __dict2xml(self, parent, dictionary):
        for entry in dictionary:
            self.tag.append(ET.SubElement(parent, dictionary[entry]['tag']))
            self.tag[-1].text = str(dictionary[entry]['text'])
            for attr in dictionary[entry]['attr']:
                self.tag[-1].set(attr, dictionary[entry]['attr'][attr])
            if len(dictionary[entry]['children']) > 0:
                self.__dict2xml(self.tag[-1], dictionary[entry]['children'])

    def __replace_blocks_by_includes(self):
        for i, file in enumerate(self.include_files):
            parent_element = self.include_elements[i].getparent()
            include_element = ET.SubElement(parent_element, "include")
            include_element.set("file", file)
            parse = ET.XMLParser(remove_blank_text=True)
            include_string = ET.tostring(self.include_elements[i], pretty_print=True)
            include_parse = ET.fromstring(include_string, parser=parse)
            include_tree = ET.ElementTree(include_parse)
            ET.indent(include_tree, space="    ")
            include_tree.write(file,
                            encoding="ISO-8859-1",
                            xml_declaration=False,
                            pretty_print=True)
            parent_element.remove(self.include_elements[i])

    def _get_root(self):
        if self.tree is None:
            if self.inputfile is not None:
                self.tree = ET.parse(self.inputfile)
            else:
                raise RuntimeError("No input file given.")
        root = self.tree.getroot()
        all_occurrences = root.findall(".//include")
        for occurrence in all_occurrences:
            self.include_files.append(occurrence.attrib["file"])
        for i, occurrence in enumerate(all_occurrences):
            _tree = ET.parse(self.include_files[i])
            _root = _tree.getroot()
            parentelement = all_occurrences[i].getparent()
            children_before = parentelement.getchildren()
            parentelement.append(_root)
            parentelement.remove(all_occurrences[i])
            children_after = parentelement.getchildren()
            for child in children_after:
                if child not in children_before:
                    self.include_elements.append(child)
        return root

    @classmethod
    def _get_parameter_pointer(cls, root, name, xpath):
        params = root.findall(xpath)
        parameterpointer = None
        for parameter in params:
            for paramproperty in parameter:
                if paramproperty.tag == "name":
                    if paramproperty.text == name:
                        parameterpointer = parameter
        if parameterpointer is None:
            print("Parameter/Property not found")
            raise RuntimeError
        return parameterpointer

    @classmethod
    def _get_medium_pointer(cls, root, mediumid):
        xpathmedia = "./media/medium"
        mediae = root.findall(xpathmedia)
        mediumpointer = None
        for medium in mediae:
            try:
                if medium.attrib['id'] == str(mediumid):
                    mediumpointer = medium
            except KeyError:
                if len(mediae) == 1:
                    if str(mediumid) == "0":
                        mediumpointer = medium
        if mediumpointer is None:
            print("Medium not found")
            raise RuntimeError
        return mediumpointer

    @classmethod
    def _get_phase_pointer(cls, root, phase):
        phases = root.findall("./phases/phase")
        phasetypes = root.findall("./phases/phase/type")
        phasecounter = None
        for i, phasetype in enumerate(phasetypes):
            if phasetype.text == phase:
                phasecounter = i
        phasepointer = phases[phasecounter]
        if phasepointer is None:
            print("Phase not found")
            raise RuntimeError
        return phasepointer

    @classmethod
    def _set_type_value(cls, parameterpointer, value, parametertype, valuetag=None):
        for paramproperty in parameterpointer:
            if paramproperty.tag == valuetag:
                if not value is None:
                    paramproperty.text = str(value)
            elif paramproperty.tag == "type":
                if not parametertype is None:
                    paramproperty.text = str(parametertype)

    def add_entry(self, parent_xpath="./", tag=None, text=None, attrib=None, attrib_value=None):
        """General method to add an Entry

        Entry contains of a single tag containing 'text',
        attributes and anttribute values

        Parameters
        ----------
        parent_xpath : `str`, optional
            XPath of the parent tag
        tag : `str`
            tag name
        text : `str`
            content
        attrib : `str`
            attribute keyword
        attrib_value : `str`
            value of the attribute keyword
        """
        self.add_entries.append({'parent_xpath': parent_xpath, 'tag': tag,
        'text': text, 'attrib': attrib, 'attrib_value': attrib_value})

    def _add_entries(self, root):
        for add_entry in self.add_entries:
            parent = root.findall(add_entry['parent_xpath'])
            if not add_entry['tag'] is None:
                newelement = []
                for i, entry in enumerate(parent):
                    newelement.append(ET.SubElement(entry, add_entry['tag']))
                    if not add_entry['text'] is None:
                        newelement[i].text = str(add_entry['text'])
                    if (add_entry['attrib'] is not None and add_entry['attrib_value'] is not None):
                        newelement[i].set(add_entry['attrib'], add_entry['attrib_value'])

    def add_include(self, parent_xpath="./", file=""):
        """add include element

        Parameters
        ----------
        parent_xpath : `str`, optional
            XPath of the parent tag
        file : `str`
            file name
        """
        self.add_includes.append({'parent_xpath': parent_xpath, 'file': file})

    def _add_includes(self, root):
        for add_include in self.add_includes:
            parent = root.findall(add_include['parent_xpath'])
            newelement = []
            for i, entry in enumerate(parent):
                newelement.append(ET.SubElement(entry, "include"))
                newelement[i].set("file", add_include['file'])

    def add_block(self, blocktag, parent_xpath="./", taglist=None, textlist=None):
        """General method to add a Block

        A block consists of an enclosing tag containing a number of
        subtags retaining a key-value structure

        Parameters
        ----------
        blocktag : `str`
            name of the enclosing tag
        parent_xpath : `str`, optional
            XPath of the parent tag
        taglist : `list`
            list of strings containing the keys
        textlist : `list`
            list of strings retaining the corresponding values
        """
        self.add_blocks.append({'blocktag': blocktag, 'parent_xpath': parent_xpath,
        'taglist': taglist, 'textlist': textlist})

    def _add_blocks(self, root):
        for add_block in self.add_blocks:
            parent = root.findall(add_block['parent_xpath'])
            if not add_block['blocktag'] is None:
                newelement = []
                for i, entry in enumerate(parent):
                    newelement.append(ET.SubElement(entry, add_block['blocktag']))
            subtaglist = []
            for blocktagentry in newelement:
                for i, taglistentry in enumerate(add_block['taglist']):
                    subtaglist.append(ET.SubElement(blocktagentry, taglistentry))
                    subtaglist[-1].text = str(add_block['textlist'][i])

    def remove_element(self, xpath):
        """Removes an element

        Parameters
        ----------
        xpath : `str`
        """
        root = self._get_root()
        elements = root.findall(xpath)
        for element in elements:
            element.getparent().remove(element)

    def replace_text(self, value, xpath=".", occurrence=-1):
        """General method for replacing text between obening and closing tags


        Parameters
        ----------
        value : `str`/`any`
            Text
        xpath : `str`, optional
            XPath of the tag
        occurrence : `int`, optional
            Easy way to adress nonunique XPath addresses by their occurence
            from the top of the XML file
            Default: -1
        """
        root = self._get_root()
        find_xpath = root.findall(xpath)
        for i, entry in enumerate(find_xpath):
            if occurrence < 0:
                entry.text = str(value)
            elif i == occurrence:
                entry.text = str(value)

    def replace_block_by_include(self, xpath="./", filename="include.xml", occurrence=0):
        """General method for replacing a block by an include


        Parameters
        ----------
        xpath : `str`, optional
            XPath of the tag
        filename : `str`, optional
        occurrence : `int`, optional
            Addresses nonunique XPath by their occurece
            Default: 0
        """
        print("Note: Includes are only written if write_input(keep_includes=True) is called.")
        root = self._get_root()
        find_xpath = root.findall(xpath)
        for i, entry in enumerate(find_xpath):
            if i == occurrence:
                self.include_elements.append(entry)
                self.include_files.append(filename)

    def replace_mesh(self, oldmesh, newmesh):
        """ Method to replace meshes

        Parameters
        ----------
        oldmesh : `str`
        newmesh : `str`
        """
        root = self._get_root()
        all_occurrences = root.findall(".//mesh")
        switch = False
        for occurrence in all_occurrences:
            if switch is False:
                if occurrence.text == oldmesh:
                    occurrence.text = newmesh
                    switch = True
            else:
                oldmesh_stripped = os.path.split(oldmesh)[1].split(".")[0]
                newmesh_stripped = os.path.split(newmesh)[1].split(".")[0]
                if occurrence.text == oldmesh_stripped:
                    occurrence.text = newmesh_stripped

    def replace_parameter(self, name=None, value=None, parametertype=None, valuetag="value"):
        """Replacing parameter types and values

        Parameters
        ----------
        name : `str`
            parametername
        value : `str`
            value
        parametertype : `str`
            parameter type
        valuetag : `str`, optional
            name of the tag containing the value, e.g., values
            Default: value
        """
        root = self._get_root()
        parameterpath = "./parameters/parameter"
        parameterpointer = self._get_parameter_pointer(root, name, parameterpath)
        self._set_type_value(parameterpointer, value, parametertype, valuetag=valuetag)

    def replace_phase_property(self, mediumid=None, phase="AqueousLiquid", name=None, value=None,
            propertytype=None, valuetag="value"):
        """Replaces properties in medium phases

        Parameters
        ----------
        mediumid : `int`
            id of the medium
        phase : `str`
            name of the phase
        name : `str`
            property name
        value : `str`/any
            value
        propertytype : `str`
            type of the property
        valuetag : `str`/any
            name of the tag containing the value, e.g., values
            Default: value
        """
        root = self._get_root()
        mediumpointer = self._get_medium_pointer(root, mediumid)
        phasepointer = self._get_phase_pointer(mediumpointer, phase)
        xpathparameter = "./properties/property"
        parameterpointer = self._get_parameter_pointer(phasepointer, name, xpathparameter)
        self._set_type_value(parameterpointer, value, propertytype, valuetag=valuetag)

    def replace_medium_property(self, mediumid=None, name=None, value=None, propertytype=None,
            valuetag="value"):
        """Replaces properties in medium (not belonging to any phase)

        Parameters
        ----------
        mediumid : `int`
            id of the medium
        name : `str`
            property name
        value : `str`/any
            value
        propertytype : `str`
            type of the property
        valuetag : `str`/any
            name of the tag containing the value, e.g., values
            Default: value
        """
        root = self._get_root()
        mediumpointer = self._get_medium_pointer(root, mediumid)
        xpathparameter = "./properties/property"
        parameterpointer = self._get_parameter_pointer(mediumpointer, name, xpathparameter)
        self._set_type_value(parameterpointer, value, propertytype, valuetag=valuetag)

    def run_model(self, logfile="out.log", path=None, args=None, container_path=None, wrapper=None, write_logs=True):
        """Command to run OGS.

        Runs OGS with the project file specified as PROJECT_FILE

        Parameters
        ----------
        logfile : `str`, optional
            Name of the file to write STDOUT of ogs
            Default: out
        path : `str`, optional
            Path of the directory in which the ogs executable can be found.
            If ``container_path`` is given: Path to the directory in which the
            Singularity executable can be found
        args : `str`, optional
            additional arguments for the ogs executable
        container_path : `str`, optional
            Path of the OGS container file.
        wrapper : `str`, optional
            add a wrapper command. E.g. mpirun
        write_logs: `bolean`, optional
            set False to omit logging
        """

        ogs_path = ""
        if self.threads is None:
            env_export = ""
        else:
            env_export = f"export OMP_NUM_THREADS={self.threads} && "
        if not container_path is None:
            container_path = os.path.expanduser(container_path)
            if os.path.isfile(container_path) is False:
                raise RuntimeError('The specific container-path is not a file. Please provide a path to the OGS container.')
            if not container_path.endswith(".sif"):
                raise RuntimeError('The specific file is not a Singularity container. Please provide a *.sif file containing OGS.')
        if not path is None:
            path = os.path.expanduser(path)
            if os.path.isdir(path) is False:
                if not container_path is None:
                    raise RuntimeError('The specified path is not a directory. Please provide a directory containing the Singularity executable.')
                raise RuntimeError('The specified path is not a directory. Please provide a directory containing the OGS executable.')
            ogs_path += path
        if not logfile is None:
            self.logfile = logfile
        if not container_path is None:
            if sys.platform == "win32":
                raise RuntimeError('Running OGS in a Singularity container is only possible in Linux. See https://sylabs.io/guides/3.0/user-guide/installation.html for Windows solutions.')
            ogs_path = os.path.join(ogs_path, "singularity")
            if shutil.which(ogs_path) is None:
                raise RuntimeError('The Singularity executable was not found. See https://www.opengeosys.org/docs/userguide/basics/container/ for installation instructions.')
        else:
            if sys.platform == "win32":
                ogs_path = os.path.join(ogs_path, "ogs.exe")
            else:
                ogs_path = os.path.join(ogs_path, "ogs")
            if shutil.which(ogs_path) is None:
                raise RuntimeError('The OGS executable was not found. See https://www.opengeosys.org/docs/userguide/basics/introduction/ for installation instructions.')
        cmd = env_export
        if not wrapper is None:
            cmd += wrapper + " "
        cmd += f"{ogs_path} "
        if not container_path is None:
            cmd += "exec " + f"{container_path} " + "ogs "
        if not args is None:
            cmd += f"{args} "
        if write_logs is True:
            cmd += f"{self.prjfile} > {self.logfile}"
        else:
            cmd += f"{self.prjfile}"
        startt = time.time()
        if sys.platform == "win32":
            returncode = subprocess.run([cmd], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        else:
            returncode = subprocess.run([cmd], shell=True, executable="/bin/bash", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        stopt = time.time()
        self.exec_time = stopt - startt
        if returncode.returncode == 0:
            print(f"OGS finished with project file {self.prjfile}.")
            print(f"Execution took {self.exec_time} s")
        else:
            print(f"Error code: {returncode.returncode}")
            if write_logs is False:
                raise RuntimeError('OGS execution was not successful. Please set write_logs to True to obtain more information.')
            num_lines = sum(1 for line in open(self.logfile))
            with open(self.logfile) as file:
                for i, line in enumerate(file):
                    if i > num_lines-10:
                        print(line)
            raise RuntimeError('OGS execution was not successful.')

    def write_input(self, keep_includes=False):
        """Writes the projectfile to disk

        Parameters
        ----------
        keep_includes : `boolean`, optional
        """
        if not self.tree is None:
            if keep_includes is True:
                self.__replace_blocks_by_includes()
            root = self.tree.getroot()
            self._add_blocks(root)
            self._add_entries(root)
            self._add_includes(root)
            parse = ET.XMLParser(remove_blank_text=True)
            self.tree_string = ET.tostring(root, pretty_print=True)
            self.tree_ = ET.fromstring(self.tree_string, parser=parse)
            self.tree = ET.ElementTree(self.tree_)
            ET.indent(self.tree, space="    ")
            self.tree.write(self.prjfile,
                            encoding="ISO-8859-1",
                            xml_declaration=True,
                            pretty_print=True)
            return True
        self.root = ET.Element("OpenGeoSysProject")
        if len(self.geo.tree['geometry']['text']) > 0:
            self.__dict2xml(self.root, self.geo.tree)
        self.__dict2xml(self.root, self.mesh.tree)
        if len(self.pyscript.tree['pythonscript']['text']) > 0:
            self.__dict2xml(self.root, self.pyscript.tree)
        self.__dict2xml(self.root, self.processes.tree)
        if len(self.media.tree['media']['children']) > 0:
            self.__dict2xml(self.root, self.media.tree)
        self.__dict2xml(self.root, self.timeloop.tree)
        if len(self.local_coordinate_system.tree['local_coordinate_system']['children']) > 0:
            self.__dict2xml(self.root, self.local_coordinate_system.tree)
        self.__dict2xml(self.root, self.parameters.tree)
        if len(self.curves.tree['curves']['children']) > 0:
            self.__dict2xml(self.root, self.curves.tree)
        self.__dict2xml(self.root, self.processvars.tree)
        self.__dict2xml(self.root, self.nonlinsolvers.tree)
        self.__dict2xml(self.root, self.linsolvers.tree)
        self._add_blocks(self.root)
        self._add_entries(self.root)
        self._add_includes(self.root)
        # Reparsing for pretty_print to work properly
        parse = ET.XMLParser(remove_blank_text=True)
        self.tree_string = ET.tostring(self.root, pretty_print=True)
        self.tree_ = ET.fromstring(self.tree_string, parser=parse)
        self.tree = ET.ElementTree(self.tree_)
        ET.indent(self.tree, space="    ")
        self.tree.write(self.prjfile,
                         encoding="ISO-8859-1",
                         xml_declaration=True,
                         pretty_print=True)
        return True

    def parse_out(self, logfile=None, filter=None, maximum_lines=None, force_parallel=False):
        """Parses the logfile

        Parameters
        ----------
        logfile : `str`, optional
            name of the log file
            Default: File specified already as logfile by runmodel
        maximum_lines : `int`
            maximum number of lines to be evaluated
        force_parallel : `boolean`
            enforce analysis of parallel output
        filter : `str`, optional
            can be "by_time_step". "convergence_newton_iteration",
            "convergence_coupling_iteration", or "time_step_vs_iterations"
            if filter is None, the raw dataframe is returned.
        """
        if logfile is None:
            logfile = self.logfile
        records = parser.parse_file(logfile, maximum_lines=maximum_lines, force_parallel=False)
        df = pd.DataFrame(records)

        df = parse_fcts.fill_ogs_context(df)
        if filter == "by_time_step":
            df = parse_fcts.analysis_time_step(df)
        elif filter == "convergence_newton_iteration":
            df = parse_fcts.analysis_convergence_newton_iteration(df)
        elif filter == "convergence_coupling_iteration":
            try:
                df = parse_fcts.analysis_convergence_coupling_iteration(df)
            except KeyError:
                print("Filter can only be applied for files generated with a staggered scheme.")
                print("Returning the raw dataframe only.")
        elif filter == "time_step_vs_iterations":
            df = parse_fcts.time_step_vs_iterations(df)
        return df
