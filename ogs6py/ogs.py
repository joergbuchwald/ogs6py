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
import pandas as pd
from lxml import etree as ET
from ogs6py.classes import (geo, mesh, python_script, processes, media, timeloop, local_coordinate_system,
        parameters, curves, processvars, linsolvers, nonlinsolvers)
import ogs6py.log_parser.log_parser as parser

class OGS(object):
    """Class for an OGS6 model.

    In this class everything for an OGS5 model can be specified.

    Parameters
    ----------
    PROJECT_FILE : :class:`str`, optional
        Filename of the output project file
        Default: default.prj
    INPUT_FILE : :class:`str`, optional
        Filename of the input project file
    XMLSTRING : :class:`str`,optional
    MKL : :class:`boolean`, optional
        Executes the MKL environment script
        Default: False
    MKL_SCRIPT : :class:`str`,optional
        MKL Environment command
        Default: source /opt/intel/mkl/bin/mklvars.sh intel64
    OMP_NUM_THREADS : :class:`int`, optional
        Sets the envirornvariable befaure OGS execution to restrict number of OMP Threads
    """
    def __init__(self, **args):
        self.geo = geo.GEO()
        self.mesh = mesh.MESH()
        self.pyscript = python_script.PYTHON_SCRIPT()
        self.processes = processes.PROCESSES()
        self.media = media.MEDIA()
        self.timeloop = timeloop.TIMELOOP()
        self.local_coordinate_system = local_coordinate_system.LOCAL_COORDINATE_SYSTEM()
        self.parameters = parameters.PARAMETERS()
        self.curves = curves.CURVES()
        self.processvars = processvars.PROCESSVARS()
        self.linsolvers = linsolvers.LINSOLVERS()
        self.nonlinsolvers = nonlinsolvers.NONLINSOLVERS()
        sys.setrecursionlimit(10000)
        self.tag = []
        self.logfile = "out.log"
        self.tree = None
        self.loadmkl = None
        if "MKL" in args:
            if args["MKL"] is True:
                if "MKL_SCRIPT" in args:
                    self.loadmkl = args["MKL_SCRIPT"]
                else:
                    self.loadmkl = "source /opt/intel/mkl/bin/mklvars.sh intel64"
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
            self.inputfile = args['INPUT_FILE']
        else:
            self.inputfile = "default.prj"
        if "XMLSTRING" in args:
            root = ET.fromstring(args['XMLSTRING'])
            self.tree = ET.ElementTree(root)

    def runModel(self, **args):
        """Command to run OGS.

        Runs OGS with the project file specified as PROJECT_FILE

        Parameters
        ----------
        LOGFILE : :class:`str`, optional
            Name of the file to write STDOUT of ogs
            Default: out
        path : :class:`str`, optional
            Path of the directory in which the ogs executable can be found
        """
        ogs_path = ""
        if self.threads is None:
            env_export = ""
        else:
            env_export = f"export OMP_NUM_THREADS={self.threads} && "
        if "path" in args:
            ogs_path = ogs_path + args["path"]
        if "LOGFILE" in args:
            self.logfile = args["LOGFILE"]
        else:
            self.logfile = "out"
        if sys.platform == "win32":
            ogs_path = os.path.join(ogs_path, "ogs.exe")
        else:
            ogs_path = os.path.join(ogs_path, "ogs")
        cmd = env_export
        if self.loadmkl is not None:
            cmd += self.loadmkl + " && "
        cmd += f"{ogs_path} {self.prjfile} > {self.logfile}"
        startt = time.time()
        returncode = subprocess.run([cmd], shell=True, executable="/bin/bash")
        stopt = time.time()
        difft = stopt - startt
        if returncode.returncode == 0:
            print(f"OGS finished with project file {self.prjfile}.")
            print(f"Execution took {difft} s")
        else:
            print(f"OGS execution not successfull. Error code: {returncode.returncode}")
            raise RuntimeError

    def __dict2xml(self, parent, dictionary):
        for entry in dictionary:
            self.tag.append(ET.SubElement(parent, dictionary[entry]['tag']))
            self.tag[-1].text = str(dictionary[entry]['text'])
            for attr in dictionary[entry]['attr']:
                self.tag[-1].set(attr, dictionary[entry]['attr'][attr])
            if len(dictionary[entry]['children']) > 0:
                self.__dict2xml(self.tag[-1], dictionary[entry]['children'])

    def replaceTxt(self, value, xpath=".", occurrence=-1):
        """General method for replacing text between obening and closing tags


        Parameters
        ----------
        value : :class:`str`/`any`
            Text
        xpath : :class:`str`, optional
            XPath of the tag
        occurrence : :class:`int`, optional
            Easy way to adress nonunique XPath addresses by their occurece
            from the top of the XML file
            Default: -1
        """
        if self.tree is None:
            self.tree = ET.parse(self.inputfile)
        root = self.tree.getroot()
        find_xpath = root.findall(xpath)
        for i, entry in enumerate(find_xpath):
            if occurrence < 0:
                entry.text = str(value)
            elif i == occurrence:
                entry.text = str(value)

    def _getParameterPointer(self, root, name, xpath):
        parameters = root.findall(xpath)
        parameterpointer = None
        for parameter in parameters:
            for paramproperty in parameter:
                if paramproperty.tag == "name":
                    if paramproperty.text == name:
                        parameterpointer = parameter
        if parameterpointer is None:
            print("Parameter/Property not found")
            raise RuntimeError
        return parameterpointer

    def _getMediumPointer(self, root, mediumid):
        xpathmedia = "./media/medium"
        media = root.findall(xpathmedia)
        mediumpointer = None
        for medium in media:
            if medium.attrib['id'] == str(mediumid):
                mediumpointer = medium
        if mediumpointer is None:
            print("Medium not found")
            raise RuntimeError
        return mediumpointer

    def _getPhasePointer(self, root, phase):
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

    def _setTypeValue(self, parameterpointer, value, parametertype, valuetag=None):
        for paramproperty in parameterpointer:
            if paramproperty.tag == valuetag:
                if not value is None:
                    paramproperty.text = str(value)
            elif paramproperty.tag == "type":
                if not parametertype is None:
                    paramproperty.text = str(parametertype)

    def addEntry(self, parent_xpath="./", tag=None, text=None, attrib=None, attrib_value=None):
        """General method to add an Entry

        Entry contains of a single tag containing 'text', attributes and anttribute values

        Parameters
        ----------
        parent_xpath : :class:`str`, optional
            XPath of the parent tag
        tag : :class:`str`
            tag name
        text : :class:`str`
            content
        attrib : :class:`str`
            attribute keyword
        attrib_value : :class:`str`
            value of the attribute keyword
        """
        if self.tree is None:
            self.tree = ET.parse(self.inputfile)
        root = self.tree.getroot()
        parent = root.findall(parent_xpath)
        if not tag is None:
            newelement = []
            for i, entry in enumerate(parent):
                newelement.append(ET.SubElement(entry, tag))
                if not text is None:
                    newelement[i].text = str(text)
                if (attrib is not None and attrib_value is not None):
                    newelement[i].set(attrib, attrib_value)

    def addBlock(self, blocktag, parent_xpath="./", taglist=None, textlist=None):
        """General method to add a Block

        A block consists of an enclosing tag containing a number of subtags retaining a key-value structure

        Parameters
        ----------
        blocktag : :class:`str`
            name of the enclosing tag
        parent_xpath : :class:`str`, optional
            XPath of the parent tag
        taglist : :class:`list`
            list of strings containing the keys
        textlist : :class:`list`
            list of strings retaining the corresponding values
        """
        if self.tree is None:
            self.tree = ET.parse(self.inputfile)
        root = self.tree.getroot()
        parent = root.findall(parent_xpath)
        if not blocktag is None:
            newelement = []
            for i, entry in enumerate(parent):
                newelement.append(ET.SubElement(entry, blocktag))
        subtaglist = []
        for blocktagentry in newelement:
            for i, taglistentry in enumerate(taglist):
                subtaglist.append(ET.SubElement(blocktagentry, taglistentry))
                subtaglist[i].text = str(textlist[i])

    def replaceParameter(self, name=None, value=None, parametertype=None, valuetag="value"):
        """Replacing parametertypes and values

        Parameters
        ----------
        name : :class:`str`
            parametername
        value : :class:`str`
            value
        parametertype : :class:`str`
            parameter type
        valuetag : :class:`str`, optional
            name of the tag containing the value, e.g., values
            Default: value
        """
        if self.tree is None:
            self.tree = ET.parse(self.inputfile)
        root = self.tree.getroot()
        parameterpath = "./parameters/parameter"
        parameterpointer = self._getParameterPointer(root, name, parameterpath)
        self._setTypeValue(parameterpointer, value, parametertype, valuetag=valuetag)

    def replacePhaseProperty(self, mediumid=None, phase="AqueousLiquid", name=None, value=None, propertytype=None, valuetag="value"):
        """Replaces properties in medium phases

        Parameters
        ----------
        mediumid : :class:`int`
            id of the medium
        phase : :class:`str`
            name of the phase
        name : :class:`str`
            property name
        value : :class:`str`/any
            value
        propertytype : :class:`str`
            type of the property
        valuetag : :class:`str`/any
            name of the tag containing the value, e.g., values
            Default: value
        """
        if self.tree is None:
            self.tree = ET.parse(self.inputfile)
        root = self.tree.getroot()
        mediumpointer = self._getMediumPointer(root, mediumid)
        phasepointer = self._getPhasePointer(mediumpointer, phase)
        xpathparameter = "./properties/property"
        parameterpointer = self._getParameterPointer(phasepointer, name, xpathparameter)
        self._setTypeValue(parameterpointer, value, propertytype, valuetag=valuetag)

    def replaceMediumProperty(self, mediumid=None, name=None, value=None, propertytype=None, valuetag="value"):
        """Replaces properties in medium (not belonging to any phase)

        Parameters
        ----------
        mediumid : :class:`int`
            id of the medium
        name : :class:`str`
            property name
        value : :class:`str`/any
            value
        propertytype : :class:`str`
            type of the property
        valuetag : :class:`str`/any
            name of the tag containing the value, e.g., values
            Default: value
        """
        if self.tree is None:
            self.tree = ET.parse(self.inputfile)
        root = self.tree.getroot()
        mediumpointer = self._getMediumPointer(root, mediumid)
        xpathparameter = "./properties/property"
        parameterpointer = self._getParameterPointer(mediumpointer, name, xpathparameter)
        self._setTypeValue(parameterpointer, value, propertytype, valuetag=valuetag)

    def writeInput(self):
        """Writes the projectfile to disk"""
        if not self.tree is None:
            root = self.tree.getroot()
            parser = ET.XMLParser(remove_blank_text=True)
            self.tree_string = ET.tostring(root, pretty_print=True)
            self.tree_ = ET.fromstring(self.tree_string, parser=parser)
            self.tree = ET.ElementTree(self.tree_)
            ET.indent(self.tree, space="    ")
            self.tree.write(self.prjfile,
                            encoding="ISO-8859-1",
                            xml_declaration=True,
                            pretty_print=True)
            return True
        else:
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
            # Reparsing for pretty_print to work properly
            parser = ET.XMLParser(remove_blank_text=True)
            self.tree_string = ET.tostring(self.root, pretty_print=True)
            self.tree_ = ET.fromstring(self.tree_string, parser=parser)
            self.tree = ET.ElementTree(self.tree_)
            ET.indent(self.tree, space="    ")
            self.tree.write(self.prjfile,
                         encoding="ISO-8859-1",
                         xml_declaration=True,
                         pretty_print=True)
            return True

    def parseOut(self, outfile="", maximum_timesteps=None, maximum_lines=None):
        """Parses the logfile

        Parameters
        ----------
        outfile : :class:`str`, optional
            name of the log file
            Default: File specified already as logfile by runmodel
        maximum_timesteps : :class:`int`
            maximum number of timesteps to be taken into account
        maximum_lines : :class:`int`
            maximum number of lines to be evaluated
        """
        data = parser.parse_file(outfile, maximum_timesteps=maximum_timesteps,
                maximum_lines=maximum_lines)
        if outfile=="":
            outfile=self.logfile
        df = pd.DataFrame(data)
        return df

