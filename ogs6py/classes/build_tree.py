"""
Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
            Distributed under a Modified BSD License.
              See accompanying file LICENSE or
              http://www.opengeosys.org/project/license

"""


from lxml import etree as ET

# pylint: disable=C0103, R0902, R0914, R0913
class BuildTree:
    """helper class to create a nested dictionary
    representing the xml structure
    """

    def __init__(self, tree: ET.ElementTree) -> None:
        self.tree = tree

    def _get_root(self) -> ET.Element:
        return self.tree.getroot()

    @classmethod
    def _convertargs(cls, args: dict) -> None:
        """
        convert arguments that are not lists or dictionaries to strings
        """
        for item, value in args.items():
            if not isinstance(value, list | dict):
                args[item] = str(value)

    @classmethod
    def populate_tree(
        cls,
        parent: ET.Element,
        tag: str,
        text: str | None = None,
        attr: dict[str, str] | None = None,
        overwrite: bool = False,
    ) -> ET.Element:
        """
        method to create dictionary from an xml entity
        """
        q = None
        if tag is not None:
            if overwrite is True:
                for child in parent:
                    if child.tag == tag:
                        q = child
            if q is None:
                q = ET.SubElement(parent, tag)
            if text is not None:
                q.text = str(text)
            if attr is not None:
                for key, val in attr.items():
                    q.set(key, str(val))
        return q

    @classmethod
    def get_child_tag(
        cls,
        parent: ET.Element,
        tag: str,
        attr: dict[str, str] | None = None,
        attr_val: str | None = None,
    ) -> ET.Element:
        """
        search for child tag based on tag and possible attributes
        """
        q = None
        for child in parent:
            if child.tag == tag:
                if not ((attr is None) and (attr_val is None)):
                    if child.get(attr) == attr_val:
                        q = child
                else:
                    q = child
        return q

    @classmethod
    def get_child_tag_for_type(
        cls, parent: ET.Element, tag: str, subtagval: str, subtag: str = "type"
    ) -> ET.Element:
        """
        search for child tag based on subtag type
        """
        q = None
        for child in parent:
            if child.tag == tag:
                for subchild in child:
                    if (subchild.tag == subtag) and (
                        subchild.text == subtagval
                    ):
                        q = child
        return q
