"""
ogs6py is a python-API for the OpenGeoSys finite element software.
Its main functionalities include creating and altering OGS6 input files as well as executing OGS.

Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""

# pylint: disable=C0103, R0902, R0914, R0913

import copy
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd
from lxml import etree as ET

from ogs6py.classes import (
    curves,
    display,
    geo,
    linsolvers,
    local_coordinate_system,
    media,
    mesh,
    nonlinsolvers,
    parameters,
    processes,
    processvars,
    python_script,
    timeloop,
)
from ogs6py.classes.properties import (
    Property,
    PropertySet,
    Value,
    expand_tensors,
    expand_van_genuchten,
    location_pointer,
    property_dict,
)
import ogs6py.log_parser.log_parser as parser
import ogs6py.log_parser.common_ogs_analyses as parse_fcts


class OGS:
    """Class for an OGS6 model.

    In this class everything for an OGS6 model can be specified.

    Parameters
    ----------
    PROJECT_FILE : `str`, optional
        Filename of the output project file
        Default: default.prj
    INPUT_FILE : `str`, optional
        Filename of the input project file
    XMLSTRING : `str`,optional
        String containing the XML tree
    OMP_NUM_THREADS : `int`, optional
        Sets the environmentvariable before OGS execution to restrict number of OMP Threads
    VERBOSE : `bool`, optional
        Default: False

    """

    def __init__(self, **args: Any) -> None:
        sys.setrecursionlimit(10000)
        self.logfile: Path = Path("out.log")
        self.tree = None
        self.include_elements: list[ET.Element] = []
        self.include_files: list[Path] = []
        self.add_includes: list[dict[str, str]] = []
        self.output_dir: Path = Path()  # default -> current dir
        self.verbose: bool = args.get("VERBOSE", False)
        self.threads: int = args.get("OMP_NUM_THREADS", None)
        self.asm_threads: int = args.get("OGS_ASM_THREADS", self.threads)
        self.inputfile: Path | None = None
        self.folder: Path = Path()

        if "PROJECT_FILE" in args:
            self.prjfile = Path(args["PROJECT_FILE"])
        else:
            print("PROJECT_FILE for output not given. Calling it default.prj.")
            self.prjfile = Path("default.prj")
        if "INPUT_FILE" in args:
            input_file = Path(args["INPUT_FILE"])
            if input_file.is_file():
                self.inputfile = input_file
                self.folder = input_file.parent
                _ = self._get_root()
                if self.verbose is True:
                    display.Display(self.tree)
            else:
                msg = f"Input project file {args['INPUT_FILE']} not found."
                raise FileNotFoundError(msg)
        else:
            self.inputfile = None
            self.root = ET.Element("OpenGeoSysProject")
            # Reparsing for pretty_print to work properly
            parse = ET.XMLParser(remove_blank_text=True, huge_tree=True)
            tree_string = ET.tostring(self.root, pretty_print=True)
            tree_ = ET.fromstring(tree_string, parser=parse)
            self.tree = ET.ElementTree(tree_)
        if "XMLSTRING" in args:
            root = ET.fromstring(args["XMLSTRING"])
            self.tree = ET.ElementTree(root)
        self.geometry = geo.Geo(self.tree)
        self.mesh = mesh.Mesh(self.tree)
        self.processes = processes.Processes(self.tree)
        self.python_script = python_script.PythonScript(self.tree)
        self.media = media.Media(self.tree)
        self.time_loop = timeloop.TimeLoop(self.tree)
        self.local_coordinate_system = (
            local_coordinate_system.LocalCoordinateSystem(self.tree)
        )
        self.parameters = parameters.Parameters(self.tree)
        self.curves = curves.Curves(self.tree)
        self.process_variables = processvars.ProcessVars(self.tree)
        self.nonlinear_solvers = nonlinsolvers.NonLinSolvers(self.tree)
        self.linear_solvers = linsolvers.LinSolvers(self.tree)

    def __replace_blocks_by_includes(self) -> None:
        for i, file in enumerate(self.include_files):
            parent_element = self.include_elements[i].getparent()
            include_element = ET.SubElement(parent_element, "include")
            file_ = file if self.folder.cwd() else file.relative_to(self.folder)
            include_element.set("file", str(file_))
            parse = ET.XMLParser(remove_blank_text=True)
            include_string = ET.tostring(
                self.include_elements[i], pretty_print=True
            )
            include_parse = ET.fromstring(include_string, parser=parse)
            include_tree = ET.ElementTree(include_parse)
            ET.indent(include_tree, space="    ")
            include_tree.write(
                file,
                encoding="ISO-8859-1",
                xml_declaration=False,
                pretty_print=True,
            )
            parent_element.remove(self.include_elements[i])

    def _get_root(
        self, remove_blank_text: bool = False, remove_comments: bool = False
    ) -> ET.Element:
        parser = ET.XMLParser(
            remove_blank_text=remove_blank_text,
            remove_comments=remove_comments,
            huge_tree=True,
        )
        if self.tree is None:
            if self.inputfile is not None:
                self.tree = ET.parse(str(self.inputfile), parser)
            else:
                msg = "This should not happen."
                raise RuntimeError(msg)
                # self.build_tree()
        root = self.tree.getroot()
        all_occurrences = root.findall(".//include")
        for occurrence in all_occurrences:
            self.include_files.append(occurrence.attrib["file"])
        for i, _ in enumerate(all_occurrences):
            _tree = ET.parse(str(self.folder / self.include_files[i]), parser)
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

    def _remove_empty_elements(self) -> None:
        root = self._get_root()
        empty_text_list = ["./geometry", "./python_script"]
        empty_el_list = [
            "./time_loop/global_process_coupling",
            "./curves",
            "./media",
            "./local_coordinate_system",
        ]
        for element in empty_text_list:
            entry = root.find(element)
            if entry is not None:
                self.remove_element(".", tag=entry.tag, text="")
            if entry is not None:
                self.remove_element(".", tag=entry.tag, text=None)
        for element in empty_el_list:
            entry = root.find(element)
            if (entry is not None) and (len(entry.getchildren()) == 0):
                entry.getparent().remove(entry)

    @classmethod
    def _get_parameter_pointer(
        cls, root: ET.Element, name: str, xpath: str
    ) -> ET.Element:
        params = root.findall(xpath)
        parameterpointer = None
        for parameter in params:
            for paramproperty in parameter:
                if (paramproperty.tag == "name") and (
                    paramproperty.text == name
                ):
                    parameterpointer = parameter
        if parameterpointer is None:
            msg = "Parameter/Property not found"
            raise RuntimeError(msg)
        return parameterpointer

    @classmethod
    def _get_medium_pointer(cls, root: ET.Element, mediumid: int) -> ET.Element:
        xpathmedia = "./media/medium"
        mediae = root.findall(xpathmedia)
        mediumpointer = None
        for medium in mediae:
            try:
                if medium.attrib["id"] == str(mediumid):
                    mediumpointer = medium
            except KeyError:
                if (len(mediae) == 1) and (str(mediumid) == "0"):
                    mediumpointer = medium
        if mediumpointer is None:
            msg = "Medium not found"
            raise RuntimeError(msg)
        return mediumpointer

    @classmethod
    def _get_phase_pointer(cls, root: ET.Element, phase: str) -> ET.Element:
        phases = root.findall("./phases/phase")
        phasetypes = root.findall("./phases/phase/type")
        phasecounter = None
        for i, phasetype in enumerate(phasetypes):
            if phasetype.text == phase:
                phasecounter = i
        phasepointer = phases[phasecounter]
        if phasepointer is None:
            msg = "Phase not found"
            raise RuntimeError(msg)
        return phasepointer

    @classmethod
    def _get_component_pointer(
        cls, root: ET.Element, component: str
    ) -> ET.Element:
        components = root.findall("./components/component")
        componentnames = root.findall("./components/component/name")
        componentcounter = None
        for i, componentname in enumerate(componentnames):
            if componentname.text == component:
                componentcounter = i
        componentpointer = components[componentcounter]
        if componentpointer is None:
            msg = "Component not found"
            raise RuntimeError(msg)
        return componentpointer

    @classmethod
    def _set_type_value(
        cls,
        parameterpointer: ET.Element,
        value: int,
        parametertype: Any | None,
        valuetag: str | None = None,
    ) -> None:
        for paramproperty in parameterpointer:
            if (paramproperty.tag == valuetag) and (value is not None):
                paramproperty.text = str(value)
            elif paramproperty.tag == "type" and parametertype is not None:
                paramproperty.text = str(parametertype)

    def add_element(
        self,
        parent_xpath: str = "./",
        tag: str | None = None,
        text: str | None = None,
        attrib_list: Any | None = None,
        attrib_value_list: Any | None = None,
    ) -> None:
        """General method to add an Entry

        An element is a single tag containing 'text',
        attributes and anttribute values

        Parameters
        ----------
        parent_xpath : `str`, optional
            XPath of the parent tag
        tag : `str`
            tag name
        text : `str`, `int` or `float`
            content
        attrib : `str`
            attribute keyword
        attrib_value : `str`, `int` or `float`
            value of the attribute keyword
        """
        root = self._get_root()
        parents = root.findall(parent_xpath)
        for parent in parents:
            if tag is not None:
                q = ET.SubElement(parent, tag)
                if text is not None:
                    q.text = str(text)
                if attrib_list is not None:
                    if attrib_value_list is None:
                        msg = "attrib_value_list is not given for add_element"
                        raise RuntimeError(msg)
                    if len(attrib_list) != len(attrib_value_list):
                        msg = "The size of attrib_list is not the same as that of attrib_value_list"
                        raise RuntimeError(msg)

                    for attrib, attrib_value in zip(
                        attrib_list, attrib_value_list, strict=False
                    ):
                        q.set(attrib, attrib_value)

    def add_include(self, parent_xpath: str = "./", file: str = "") -> None:
        """add include element

        Parameters
        ----------
        parent_xpath : `str`, optional
            XPath of the parent tag
        file : `str`
            file name
        """
        self.add_includes.append({"parent_xpath": parent_xpath, "file": file})

    def _add_includes(self, root: ET.Element) -> None:
        for add_include in self.add_includes:
            parent = root.findall(add_include["parent_xpath"])
            newelement = []
            for i, entry in enumerate(parent):
                newelement.append(ET.SubElement(entry, "include"))
                newelement[i].set("file", add_include["file"])

    def add_block(
        self,
        blocktag: str,
        block_attrib: Any | None = None,
        parent_xpath: str = "./",
        taglist: list[str] | None = None,
        textlist: list[str] | None = None,
    ) -> None:
        """General method to add a Block

        A block consists of an enclosing tag containing a number of
        subtags retaining a key-value structure

        Parameters
        ----------
        blocktag : `str`
            name of the enclosing tag
        block_attrib : 'dict', optional
            attributes belonging to the blocktag
        parent_xpath : `str`, optional
            XPath of the parent tag
        taglist : `list`
            list of strings containing the keys
        textlist : `list`
            list of strings, ints or floats retaining the corresponding values

        """
        root = self._get_root()
        parents = root.findall(parent_xpath)
        for parent in parents:
            q = ET.SubElement(parent, blocktag)
            if block_attrib is not None:
                for key, val in block_attrib.items():
                    q.set(key, val)
            if (taglist is not None) and (textlist is not None):
                for i, tag in enumerate(taglist):
                    r = ET.SubElement(q, tag)
                    if textlist[i] is not None:
                        r.text = str(textlist[i])

    def deactivate_property(
        self, name: str, mediumid: int = 0, phase: str | None = None
    ) -> None:
        """Replaces MPL properties by a comment

        Parameters
        ----------
        mediumid : `int`
            id of the medium
        phase : `str`
            name of the phase
        name : `str`
            property name
        """
        root = self._get_root()
        mediumpointer = self._get_medium_pointer(root, mediumid)
        xpathparameter = "./properties/property"
        if phase is None:
            parameterpointer = self._get_parameter_pointer(
                mediumpointer, name, xpathparameter
            )
        else:
            phasepointer = self._get_phase_pointer(mediumpointer, phase)
            parameterpointer = self._get_parameter_pointer(
                phasepointer, name, xpathparameter
            )
        parameterpointer.getparent().replace(
            parameterpointer, ET.Comment(ET.tostring(parameterpointer))
        )

    def deactivate_parameter(self, name: str) -> None:
        """Replaces parameters by a comment

        Parameters
        ----------
        name : `str`
            property name
        """
        root = self._get_root()
        parameterpath = "./parameters/parameter"
        parameterpointer = self._get_parameter_pointer(
            root, name, parameterpath
        )
        parameterpointer.getparent().replace(
            parameterpointer, ET.Comment(ET.tostring(parameterpointer))
        )

    def remove_element(
        self, xpath: str, tag: str | None = None, text: str | None = None
    ) -> None:
        """Removes an element

        Parameters
        ----------
        xpath : `str`
        """
        root = self._get_root()
        elements = root.findall(xpath)
        if tag is None:
            for element in elements:
                element.getparent().remove(element)
        else:
            for element in elements:
                sub_elements = element.getchildren()
                for sub_element in sub_elements:
                    if sub_element.tag == tag and sub_element.text == text:
                        sub_element.getparent().remove(sub_element)

    def replace_text(
        self, value: str | int, xpath: str = ".", occurrence: int = -1
    ) -> None:
        """General method for replacing text between opening and closing tags


        Parameters
        ----------
        value : `str`/`any`
            Text
        xpath : `str`, optional
            XPath of the tag
        occurrence : `int`, optional
            Easy way to address nonunique XPath addresses by their occurrence
            from the top of the XML file
            Default: -1
        """
        root = self._get_root()
        find_xpath = root.findall(xpath)
        for i, entry in enumerate(find_xpath):
            if occurrence < 0 or i == occurrence:
                entry.text = str(value)

    def replace_block_by_include(
        self,
        xpath: str = "./",
        filename: str = "include.xml",
        occurrence: int = 0,
    ) -> None:
        """General method for replacing a block by an include


        Parameters
        ----------
        xpath : `str`, optional
            XPath of the tag
        filename : `str`, optional
            name of the include file
        occurrence : `int`, optional
            Addresses nonunique XPath by their occurece
        """
        print(
            "Note: Includes are only written if write_input(keep_includes=True) is called."
        )
        root = self._get_root()
        find_xpath = root.findall(xpath)
        for i, entry in enumerate(find_xpath):
            if i == occurrence:
                self.include_elements.append(entry)
                self.include_files.append(self.prjfile.parent / filename)

    def replace_mesh(self, oldmesh: str, newmesh: str) -> None:
        """Method to replace meshes

        Parameters
        ----------
        oldmesh : `str`
        newmesh : `str`
        """
        root = self._get_root()
        bulkmesh = root.find("./mesh")
        if bulkmesh is not None:
            if bulkmesh.text == oldmesh:
                bulkmesh.text = newmesh
            else:
                msg = "Bulk mesh name and oldmesh argument don't agree."
                raise RuntimeError(msg)
        all_occurrences_meshsection = root.findall("./meshes/mesh")
        for occurrence in all_occurrences_meshsection:
            if occurrence.text == oldmesh:
                occurrence.text = newmesh
        all_occurrences = root.findall(".//mesh")
        for occurrence in all_occurrences:
            if occurrence not in all_occurrences_meshsection:
                oldmesh_stripped = os.path.split(oldmesh)[1].replace(".vtu", "")
                newmesh_stripped = os.path.split(newmesh)[1].replace(".vtu", "")
                if occurrence.text == oldmesh_stripped:
                    occurrence.text = newmesh_stripped

    def replace_parameter(
        self,
        name: str = "",
        parametertype: str = "",
        taglist: list[str] | None = None,
        textlist: list[str] | None = None,
    ) -> None:
        """Replacing parametertypes and values

        Parameters
        ----------
        name : `str`
            parametername
        parametertype : `str`
            parametertype
        taglist : `list`
            list of tags needed for parameter spec
        textlist : `list`
            values of parameter
        """
        root = self._get_root()
        parameterpath = "./parameters/parameter[name='" + name + "']"
        parent = root.find(parameterpath)
        children = parent.getchildren()
        for child in children:
            if child.tag not in ["name", "type"]:
                self.remove_element(f"{parameterpath}/{child.tag}")
        paramtype = root.find(f"{parameterpath}/type")
        paramtype.text = parametertype
        if (taglist is not None) and (textlist is not None):
            for i, tag in enumerate(taglist):
                if tag not in ["name", "type"]:
                    self.add_element(
                        parent_xpath=parameterpath, tag=tag, text=textlist[i]
                    )

    def replace_parameter_value(
        self, name: str = "", value: int = 0, valuetag: str = "value"
    ) -> None:
        """Replacing parameter values

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
        parameterpointer = self._get_parameter_pointer(
            root, name, parameterpath
        )
        self._set_type_value(parameterpointer, value, None, valuetag=valuetag)

    def replace_phase_property_value(
        self,
        mediumid: int = 0,
        phase: str = "AqueousLiquid",
        component: str | None = None,
        name: str = "",
        value: int = 0,
        propertytype: str = "Constant",
        valuetag: str = "value",
    ) -> None:
        """Replaces properties in medium phases

        Parameters
        ----------
        mediumid : `int`
            id of the medium
        phase : `str`
            name of the phase
        component : `str`
            name of the component
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
        if component is not None:
            phasepointer = self._get_component_pointer(phasepointer, component)
        xpathparameter = "./properties/property"
        parameterpointer = self._get_parameter_pointer(
            phasepointer, name, xpathparameter
        )
        self._set_type_value(
            parameterpointer, value, propertytype, valuetag=valuetag
        )

    def replace_medium_property_value(
        self,
        mediumid: int = 0,
        name: str = "",
        value: int = 0,
        propertytype: str = "Constant",
        valuetag: str = "value",
    ) -> None:
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
        parameterpointer = self._get_parameter_pointer(
            mediumpointer, name, xpathparameter
        )
        self._set_type_value(
            parameterpointer, value, propertytype, valuetag=valuetag
        )

    def set(self, **args: str | int) -> None:
        """
        Sets directly a uniquely defined property
        List of properties is given in the dictory below
        """
        property_db = {
            "t_initial": "./time_loop/processes/process/time_stepping/t_initial",
            "t_end": "./time_loop/processes/process/time_stepping/t_end",
            "output_prefix": "./time_loop/output/prefix",
            "reltols": "./time_loop/processes/process/convergence_criterion/reltols",
            "abstols": "./time_loop/processes/process/convergence_criterion/abstols",
            "mass_lumping": "./processes/process/mass_lumping",
            "eigen_solver": "./linear_solvers/linear_solver/eigen/solver_type",
            "eigen_precon": "./linear_solvers/linear_solver/eigen/precon_type",
            "eigen_max_iteration_step": "./linear_solvers/linear_solver/eigen/max_iteration_step",
            "eigen_error_tolerance": "./linear_solvers/linear_solver/eigen/error_tolerance",
            "eigen_scaling": "./linear_solvers/linear_solver/eigen/scaling",
            "petsc_prefix": "./linear_solvers/linear_solver/petsc/prefix",
            "petsc_parameters": "./linear_solvers/linear_solver/petsc/parameters",
            "compensate_displacement": "./process_variables/process_variable[name='displacement']/compensate_non_equilibrium_initial_residuum",
            "compensate_all": "./process_variables/process_variable/compensate_non_equilibrium_initial_residuum",
        }
        for key, val in args.items():
            self.replace_text(val, xpath=property_db[key])

    def restart(
        self,
        restart_suffix: str = "_restart",
        t_initial: float | None = None,
        t_end: float | None = None,
        zero_displacement: bool = False,
    ) -> None:
        """Prepares the project file for a restart.

        Takes the last time step from the PVD file mentioned in the PRJ file.
        Sets initial conditions accordingly.

        Parameters
        ----------
        restart_suffix : `str`,
            suffix by which the output prefix is appended
        t_initial : `float`, optional
            first time step, takes the last from previous simulation if None
        t_end : `float`, optional
            last time step, the same as in previous run if None
        zero_displacement: `bolean`, False
            sets the initial displacement to zero if True
        """

        root_prj = self._get_root()
        filetype = root_prj.find("./time_loop/output/type").text
        pvdfile = root_prj.find("./time_loop/output/prefix").text + ".pvd"
        pvdfile = self.output_dir / pvdfile
        if filetype != "VTK":
            msg = "Output file type unknown. Please use VTK."
            raise RuntimeError(msg)
        tree = ET.parse(pvdfile)
        xpath = "./Collection/DataSet"
        root_pvd = tree.getroot()
        find_xpath = root_pvd.findall(xpath)
        lastfile = find_xpath[-1].attrib["file"]
        last_time = find_xpath[-1].attrib["timestep"]
        try:
            bulk_mesh = root_prj.find("./mesh").text
        except AttributeError:
            try:
                bulk_mesh = root_prj.find("./meshes/mesh").text
            except AttributeError:
                print("Can't find bulk mesh.")
        self.replace_mesh(bulk_mesh, lastfile)
        root_prj.find("./time_loop/output/prefix").text = (
            root_prj.find("./time_loop/output/prefix").text + restart_suffix
        )
        t_initials = root_prj.findall(
            "./time_loop/processes/process/time_stepping/t_initial"
        )
        t_ends = root_prj.findall(
            "./time_loop/processes/process/time_stepping/t_end"
        )
        for i, t0 in enumerate(t_initials):
            if t_initial is None:
                t0.text = last_time
            else:
                t0.text = str(t_initial)
            if t_end is not None:
                t_ends[i].text = str(t_end)
        process_vars = root_prj.findall(
            "./process_variables/process_variable/name"
        )
        ic_names = root_prj.findall(
            "./process_variables/process_variable/initial_condition"
        )
        for i, process_var in enumerate(process_vars):
            if process_var.text == "displacement" and zero_displacement is True:
                print(
                    "Please make sure that epsilon_ip is removed from the VTU file before you run OGS."
                )
                zero = {"1": "0", "2": "0 0", "3": "0 0 0"}
                cpnts = root_prj.find(
                    "./process_variables/process_variable[name='displacement']/components"
                ).text
                self.replace_parameter(
                    name=ic_names[i].text,
                    parametertype="Constant",
                    taglist=["values"],
                    textlist=[zero[cpnts]],
                )
            else:
                self.replace_parameter(
                    name=ic_names[i].text,
                    parametertype="MeshNode",
                    taglist=["mesh", "field_name"],
                    textlist=[
                        lastfile.split("/")[-1].replace(".vtu", ""),
                        process_var.text,
                    ],
                )
        self.remove_element("./processes/process/initial_stress")

    def run_model(
        self,
        logfile: Path = Path("out.log"),
        path: Path | None = None,
        args: Any | None = None,
        container_path: Path | str | None = None,
        wrapper: Any | None = None,
        write_logs: bool = True,
        write_prj_to_pvd: bool = True,
    ) -> None:
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
        ogs_path: Path = Path()
        env_export = ""
        if self.threads is not None:
            env_export += f"export OMP_NUM_THREADS={self.threads} && "
        if self.asm_threads is not None:
            env_export += f"export OGS_ASM_THREADS={self.asm_threads} && "
        if container_path is not None:
            container_path = Path(container_path)
            container_path = container_path.expanduser()
            if not container_path.is_file():
                msg = "The specific container-path is not a file. Please provide a path to the OGS container."
                raise RuntimeError(msg)
            if str(container_path.suffix).lower() != ".sif":
                msg = "The specific file is not a Singularity container. Please provide a *.sif file containing OGS."
                raise RuntimeError(msg)
        if path:
            path = Path(path)
            path = path.expanduser()
            if not path.is_dir():
                if container_path is not None:
                    msg = "The specified path is not a directory. Please provide a directory containing the Singularity executable."
                    raise RuntimeError(msg)
                msg = "The specified path is not a directory. Please provide a directory containing the OGS executable."
                raise RuntimeError(msg)
            ogs_path = ogs_path / path
        if logfile is not None:
            self.logfile = Path(logfile)
        if container_path is not None:
            if sys.platform == "win32":
                msg = "Running OGS in a Singularity container is only possible in Linux. See https://sylabs.io/guides/3.0/user-guide/installation.html for Windows solutions."
                raise RuntimeError(msg)
            ogs_path = ogs_path / "singularity"
            if shutil.which(str(ogs_path)) is None:
                msg = "The Singularity executable was not found. See https://www.opengeosys.org/docs/userguide/basics/container/ for installation instructions."
                raise RuntimeError(msg)
        else:
            if sys.platform == "win32":
                ogs_path = ogs_path / "ogs.exe"
            else:
                ogs_path = ogs_path / "ogs"
            if shutil.which(str(ogs_path)) is None:
                msg = "The OGS executable was not found. See https://www.opengeosys.org/docs/userguide/basics/introduction/ for installation instructions."
                raise RuntimeError(msg)
        cmd = env_export
        if wrapper is not None:
            cmd += wrapper + " "
        cmd += f"{ogs_path} "
        if container_path is not None:
            if wrapper is not None:
                cmd = (
                    env_export
                    + "singularity exec "
                    + f"{container_path} "
                    + wrapper
                    + " "
                )
            else:
                cmd = (
                    env_export
                    + "singularity exec "
                    + f"{container_path} "
                    + "ogs "
                )
        if args is not None:
            argslist = args.split(" ")
            output_dir_flag = False
            for entry in argslist:
                if output_dir_flag is True:
                    self.output_dir = Path(entry)
                    output_dir_flag = False
                if "-o" in entry:
                    output_dir_flag = True
            cmd += f"{args} "
        if write_logs is True:
            cmd += f"{self.prjfile} > {self.logfile}"
        else:
            cmd += f"{self.prjfile}"
        startt = time.time()
        if sys.platform == "win32":
            returncode = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                check=False,
            )
        else:
            returncode = subprocess.run(
                cmd,
                shell=True,
                executable="bash",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                check=False,
            )
        stopt = time.time()
        self.exec_time = stopt - startt
        if returncode.returncode == 0:
            print(f"OGS finished with project file {self.prjfile}.")
            print(f"Execution took {self.exec_time} s")
            if write_prj_to_pvd is True:
                self.inputfile = self.prjfile
                # self.tree = None # TODO: check whether this line can be safely removed
                root = self._get_root(
                    remove_blank_text=True, remove_comments=True
                )
                prjstring = ET.tostring(root, pretty_print=True)
                prjstring = (
                    str(prjstring)
                    .replace("\r", " ")
                    .replace("\n", " ")
                    .replace("--", "")
                )
                if self.tree is None:
                    msg = "self.tree is empty."
                    raise AttributeError(msg)
                fn_type = self.tree.find("./time_loop/output/type").text
                fn = None
                if fn_type == "VTK":
                    fn = (
                        self.tree.find("./time_loop/output/prefix").text
                        + ".pvd"
                    )
                    fn = self.output_dir / fn
                elif fn_type == "XDMF":
                    prefix = self.tree.find("./time_loop/output/prefix").text
                    mesh = self.tree.find("./mesh")
                    if mesh is None:
                        mesh = self.tree.find("./meshes/mesh")
                    prefix = self.output_dir / prefix
                    if mesh is not None:
                        fn = (
                            str(prefix)
                            + "_"
                            + mesh.text.split(".vtu")[0]
                            + ".xdmf"
                        )
                    else:
                        msg = "No mesh found"
                        raise AttributeError(msg)
                if fn is not None:
                    tree_pvd = ET.parse(fn)
                    root_pvd = tree_pvd.getroot()
                    root_pvd.append(ET.Comment(prjstring))
                    tree_pvd.write(
                        fn,
                        encoding="ISO-8859-1",
                        xml_declaration=True,
                        pretty_print=True,
                    )
                    print("Project file written to output.")
        else:
            print(f"Error code: {returncode.returncode}")
            if write_logs is False:
                msg = "OGS execution was not successful. Please set write_logs to True to obtain more information."
                raise RuntimeError(msg)
            with self.logfile.open() as lf:
                num_lines = len(lf.readlines())
            with self.logfile.open() as file:
                for i, line in enumerate(file):
                    if i > num_lines - 10:
                        print(line)
            msg = "OGS execution was not successful."
            raise RuntimeError(msg)

    def write_input(self, keep_includes: bool = False) -> None:
        """Writes the projectfile to disk

        Parameters
        ----------
        keep_includes : `boolean`, optional
        """
        if self.tree is not None:
            self._remove_empty_elements()
            if keep_includes is True:
                self.__replace_blocks_by_includes()
            root = self.tree.getroot()
            self._add_includes(root)
            parse = ET.XMLParser(remove_blank_text=True)
            self.tree_string = ET.tostring(root, pretty_print=True)
            self.tree_ = ET.fromstring(self.tree_string, parser=parse)
            self.tree = ET.ElementTree(self.tree_)
            ET.indent(self.tree, space="    ")
            if self.verbose is True:
                display.Display(self.tree)
            self.tree.write(
                self.prjfile,
                encoding="ISO-8859-1",
                xml_declaration=True,
                pretty_print=True,
            )
        else:
            msg = "No tree has been build."
            raise RuntimeError(msg)

    def parse_out(self, logfile: str | None = None,
                  filter: str | None = None,
                  maximum_lines: int | None = None,
                  reset_index: bool = True,
                  return_records: bool = False) -> pd.DataFrame:
        """Parses the logfile

        Parameters
        ----------
        logfile : `str`, optional
            name of the log file
            Default: File specified already as logfile by runmodel
        maximum_lines : `int`
            maximum number of lines to be evaluated
        filter : `str`, optional
            can be "by_time_step". "convergence_newton_iteration",
            "convergence_coupling_iteration", or "time_step_vs_iterations"
            if filter is None, the raw dataframe is returned.
        """
        if logfile is None:
            logfile = self.logfile
        records, _ = parser.parse_file(logfile, maximum_lines=maximum_lines, force_parallel=False)
        if return_records is True:
            return records
        df = pd.DataFrame(records)

        df = parse_fcts.fill_ogs_context(df)
        filterdict = {"by_time_step":parse_fcts.analysis_time_step,
                "convergence_newton_iteration":parse_fcts.analysis_convergence_newton_iteration,
                "convergence_coupling_iteration": parse_fcts.analysis_convergence_coupling_iteration,
                "time_step_vs_iterations":  parse_fcts.time_step_vs_iterations,
                "analysis_simulation": parse_fcts.analysis_simulation,
                "fill_ogs_context": parse_fcts.fill_ogs_context
                }
        if filter is not None:
            try:
                df = filterdict[filter](df)
            except KeyError:
                print("Filter not available")
        if reset_index is True:
            return df.reset_index()
        return df

    def property_dataframe(
        self, mediamapping: dict[int, str] | None = None
    ) -> pd.DataFrame:
        newtree = copy.deepcopy(self.tree)
        if (newtree is None) or (self.tree is None):
            msg = "No tree existing."
            raise AttributeError(msg)
        root = newtree.getroot()
        property_list: list[Property] = []
        multidim_prop: dict[int, dict] = {}
        numofmedia = len(self.tree.findall("./media/medium"))
        if mediamapping is None:
            mediamapping = {}
            for i in range(numofmedia):
                mediamapping[i] = f"medium {i}"
        for i in range(numofmedia):
            multidim_prop[i] = {}
        ## preprocessing
        # write elastic properties to MPL
        for entry in newtree.findall(
            "./processes/process/constitutive_relation"
        ):
            medium = self._get_medium_pointer(root, entry.attrib.get("id", "0"))
            parent = medium.find("./phases/phase[type='Solid']/properties")
            taglist = ["name", "type", "parameter_name"]
            for subentry in entry:
                if subentry.tag in [
                    "youngs_modulus",
                    "poissons_ratio",
                    "youngs_moduli",
                    "poissons_ratios",
                    "shear_moduli",
                ]:
                    textlist = [subentry.tag, "Parameter", subentry.text]
                    q = ET.SubElement(parent, "property")
                    for i, tag in enumerate(taglist):
                        r = ET.SubElement(q, tag)
                        if textlist[i] is not None:
                            r.text = str(textlist[i])

        for location in location_pointer:
            # resolve parameters
            parameter_names_add = newtree.findall(
                f"./media/medium/{location_pointer[location]}properties/property[type='Parameter']/parameter_name"
            )
            parameter_names = [name.text for name in parameter_names_add]
            for parameter_name in parameter_names:
                param_type = newtree.find(
                    f"./parameters/parameter[name='{parameter_name}']/type"
                ).text
                if param_type == "Constant":
                    param_value = newtree.findall(
                        f"./parameters/parameter[name='{parameter_name}']/value"
                    )
                    param_value.append(
                        newtree.find(
                            f"./parameters/parameter[name='{parameter_name}']/values"
                        )
                    )
                    property_type = newtree.findall(
                        f"./media/medium/{location_pointer[location]}properties/property[parameter_name='{parameter_name}']/type"
                    )
                    for entry in property_type:
                        entry.text = "Constant"
                    property_value = newtree.findall(
                        f"./media/medium/{location_pointer[location]}properties/property[parameter_name='{parameter_name}']/parameter_name"
                    )
                    for entry in property_value:
                        entry.tag = "value"
                        entry.text = param_value[0].text
            # expand tensors
            expand_tensors(self, numofmedia, multidim_prop, root, location)
            expand_van_genuchten(self, numofmedia, root, location)
            property_names = [
                name.text
                for name in newtree.findall(
                    f"./media/medium/{location_pointer[location]}properties/property/name"
                )
            ]
            property_names = list(dict.fromkeys(property_names))
            values: dict[str, list] = {}
            for name in property_names:
                values[name] = []
                orig_name = "".join(c for c in name if not c.isnumeric())
                number_suffix = "".join(c for c in name if c.isnumeric())
                if orig_name in property_dict[location]:
                    for medium_id in range(numofmedia):
                        if medium_id in mediamapping:
                            medium = self._get_medium_pointer(root, medium_id)
                            proptytype = medium.find(
                                f"./{location_pointer[location]}properties/property[name='{name}']/type"
                            )
                            if proptytype is None:
                                values[name].append(
                                    Value(mediamapping[medium_id], None)
                                )
                            else:
                                if proptytype.text == "Constant":
                                    value_entry = medium.find(
                                        f"./{location_pointer[location]}properties/property[name='{name}']/value"
                                    ).text
                                    value_entry_list = value_entry.split(" ")
                                    if len(value_entry_list) == 1:
                                        values[name].append(
                                            Value(
                                                mediamapping[medium_id],
                                                float(value_entry),
                                            )
                                        )
                                else:
                                    values[name].append(
                                        Value(mediamapping[medium_id], None)
                                    )
                    if number_suffix != "":
                        new_symbol = (
                            property_dict[location][orig_name]["symbol"][:-1]
                            + "_"
                            + number_suffix
                            + "$"
                        )
                    else:
                        new_symbol = property_dict[location][orig_name][
                            "symbol"
                        ]
                    property_list.append(
                        Property(
                            property_dict[location][orig_name]["title"],
                            new_symbol,
                            property_dict[location][orig_name]["unit"],
                            values[name],
                        )
                    )
        properties = PropertySet(property=property_list)
        return pd.DataFrame(properties)

    def write_property_latextable(
        self,
        latexfile: Path = Path("property_dataframe.tex"),
        mediamapping: dict[int, str] | None = None,
        float_format: str = "{:.2e}",
    ) -> None:
        with latexfile.open("w") as tf:
            tf.write(
                self.property_dataframe(mediamapping).to_latex(
                    index=False, float_format=float_format.format
                )
            )
