"""
Process List
============

Defines the top level Process List object that represents a CLF process.

"""

from __future__ import annotations

from dataclasses import dataclass

import lxml.etree
from _warnings import warn

from colour_clf_io.elements import Info
from colour_clf_io.errors import ParsingError
from colour_clf_io.parsing import (
    ParserConfig,
    element_as_text,
    elements_as_text_list,
    must_have,
)
from colour_clf_io.process_nodes import (
    ProcessNode,
    assert_bit_depth_compatibility,
    parse_process_node,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__ALL__ = ["ProcessList"]


@dataclass
class ProcessList:
    """
    Represents a Process List.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#processList
    """

    id: str
    compatible_CLF_version: str
    process_nodes: list[ProcessNode]

    name: str | None
    inverse_of: str | None

    description: list[str]
    input_descriptor: str | None
    output_descriptor: str | None

    info: Info | None

    @staticmethod
    def from_xml(xml):
        """
        Parse and return the Process List from the given XML node. Returns None if the
        given element is None.

        Expects the xml element to be a valid element according to the CLF
        specification.

        Raises
        ------
        :class: ParsingError
            If the node does not conform to the specification, a `ParsingError`
            will be raised. The error message will indicate the details of the issue
            that was encountered.

        """
        if xml is None:
            return None
        id = xml.get("id")  # noqa: A001
        must_have(id, "ProcessList must contain an `id` attribute")
        compatible_clf_version = xml.get("compCLFversion")
        must_have(
            compatible_clf_version,
            "ProcessList must contain an `compCLFversion` attribute",
        )

        # By default, we would expect the correct namespace as per the specification.
        # But if it is not present, we will still try to parse the document anyway.
        # We won't accept a wrong namespace through.
        config = ParserConfig()
        namespace = xml.xpath("namespace-uri(.)")
        if not namespace:
            config.namespace_name = None
        elif namespace != config.namespace_name:
            raise ParsingError(
                f"Found invalid xmlns attribute in process list: {namespace}"
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
            id=id,
            compatible_CLF_version=compatible_clf_version,
            process_nodes=process_nodes,
            name=name,
            inverse_of=inverse_of,
            input_descriptor=input_descriptor,
            output_descriptor=output_descriptor,
            info=info,
            description=description,
        )
