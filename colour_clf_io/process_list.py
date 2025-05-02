"""
*ProcessList*
============

Defines the top level *ProcessList* object that represents a *CLF* process.
"""

from __future__ import annotations

from dataclasses import dataclass

import lxml.etree
from _warnings import warn

from colour_clf_io.elements import Info
from colour_clf_io.errors import ParsingError
from colour_clf_io.parsing import (
    Namespaces,
    ParserConfig,
    UnknownNamespace,
    check_none,
    detect_namespace,
    element_as_text,
    elements_as_text_list,
    set_attr_if_not_none,
    set_element_if_not_none,
)
from colour_clf_io.process_nodes import (
    ProcessNode,
    assert_bit_depth_compatibility,
    parse_process_node,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["ProcessList"]


@dataclass
class ProcessList:
    """
    Represent a *ProcessList*, the root element for any *CLF* file. It is
    composed of one or more :class:`colour_clf_io.ProcessNodes` class instances.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.ProcessList.id`
    -   :attr:`~colour_clf_io.ProcessList.compatible_CLF_version`
    -   :attr:`~colour_clf_io.ProcessList.name`
    -   :attr:`~colour_clf_io.ProcessList.inverse_of`
    -   :attr:`~colour_clf_io.ProcessList.description`
    -   :attr:`~colour_clf_io.ProcessList.input_descriptor`
    -   :attr:`~colour_clf_io.ProcessList.output_descriptor`
    -   :attr:`~colour_clf_io.ProcessList.info`
    -   :attr:`~colour_clf_io.ProcessList.process_nodes`

    Methods
    -------
    -   :meth:`~colour_clf_io.ProcessList.from_xml`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processList
    """

    id: str | None
    """A string to serve as a unique identifier of the *ProcessList*."""

    compatible_CLF_version: str | None
    """
    A string indicating the minimum compatible CLF specification version
    required to read this file. The compCLFversion corresponding to this
    version of the specification is be "3.0".
    """

    name: str | None
    """
    A concise string used as a text name of the *ProcessList* for display or
    selection from an application's user interface.
    """

    inverse_of: str | None
    """
    A string for linking to another *ProcessList* id (unique) which is the
    inverse of this one.
    """

    description: list[str]
    """
    A list for comments describing the function, usage, or any notes about
    the *ProcessList*.
    """

    input_descriptor: str | None
    """
    An arbitrary string used to describe the intended source code values of the
    *ProcessList*.
    """

    output_descriptor: str | None
    """
    An arbitrary string used to describe the intended output target of the
    *ProcessList* (e.g., target display).
    """

    process_nodes: list[ProcessNode]
    """
    A list of colour operators. The *ProcessList* must contain at least one
    *ProcessNode*.
    """

    info: Info | None
    """
    Optional element for including additional custom metadata not needed to
    interpret the transforms.
    """
    """"""

    @staticmethod
    def from_xml(xml: lxml.etree._Element | None) -> ProcessList | None:
        """
        Parse and return a :class:`colour_clf_io.ProcessList` class instance
        from the given XML element. Returns ``None`` if the given XML element is
        ``None``.

        Expects the XML element to be a valid element, according to the *CLF*
        specification.

        Parameters
        ----------
        xml
            XML element to parse.

        Returns
        -------
        class:`colour_clf_io.ProcessList` or :py:data:`None`
            Parsed XML node.

        Raises
        ------
        :class:`colour_clf_io.errors.ParsingError`
            If the node does not conform to the specification, a ``ParsingError``
            exception will be raised. The error message will indicate the
            details of the issue that was encountered.
        """

        if xml is None:
            return None

        detected_namespace = detect_namespace(xml)
        document_namespace: Namespaces | None = None
        match detected_namespace:
            case None:
                document_namespace = None
            case UnknownNamespace(value):
                exception = f"Found invalid xmlns attribute in *ProcessList*: {value}"
                raise ParsingError(exception)
            case Namespaces():
                document_namespace = detected_namespace

        if document_namespace == Namespaces.SMTP:
            error = (
                "SMPTE ST 2136-1 files are not fully supported. See "
                "https://github.com/colour-science/colour-clf-io/issues/6 "
                "for more information. "
            )
            raise ParsingError(error)

        config = ParserConfig(namespace=document_namespace)

        id_ = xml.get("id")
        check_none(id_, "ProcessList must contain an `id` attribute")

        compatible_clf_version = xml.get("compCLFversion")
        check_none(
            compatible_clf_version,
            'ProcessList must contain a "compCLFversion" attribute',
        )

        name = xml.get("name")
        inverse_of = xml.get("inverseOf")
        info = Info.from_xml(xml, config)

        description = elements_as_text_list(xml, "Description", config)
        input_descriptor = element_as_text(xml, "InputDescriptor", config)
        output_descriptor = element_as_text(xml, "OutputDescriptor", config)

        ignore_nodes = ["Description", "InputDescriptor", "OutputDescriptor", "Info"]
        process_nodes = filter(
            lambda node: lxml.etree.QName(node).localname not in ignore_nodes, xml
        )

        if not process_nodes:
            warn("Got empty process node.")

        process_nodes = [
            parse_process_node(xml_node, config) for xml_node in process_nodes
        ]
        assert_bit_depth_compatibility(process_nodes)

        return ProcessList(
            id=id_,
            compatible_CLF_version=compatible_clf_version,
            process_nodes=process_nodes,
            name=name,
            inverse_of=inverse_of,
            input_descriptor=input_descriptor,
            output_descriptor=output_descriptor,
            info=info,
            description=description,
        )

    def to_xml(self, name_space: Namespaces = Namespaces.AMPAS) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Parameters
        ----------
        name_space
            :class:`colour_clf_io.Namespaces` instance to be used for the namespace
            of the document.

        Returns
        -------
        :class:`lxml.etree._Element`
        """
        xml = lxml.etree.Element("ProcessList")

        xml.set("xmlns", name_space.value)

        for description_text in self.description:
            description_element = lxml.etree.SubElement(xml, "Description")
            description_element.text = description_text

        set_attr_if_not_none(xml, "id", self.id)
        set_attr_if_not_none(xml, "compCLFversion", self.compatible_CLF_version)
        set_attr_if_not_none(xml, "name", self.name)
        set_attr_if_not_none(xml, "inverseOf", self.inverse_of)
        set_element_if_not_none(xml, "InputDescriptor", self.input_descriptor)
        set_element_if_not_none(xml, "OutputDescriptor", self.output_descriptor)

        if self.info:
            xml.append(self.info.to_xml())

        for process_node in self.process_nodes:
            xml.append(process_node.to_xml())
        return xml
