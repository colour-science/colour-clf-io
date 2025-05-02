"""
Process Nodes
============

Defines the available process nodes in a *CLF* file.
"""

from __future__ import annotations

import typing
from abc import ABC
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from collections.abc import Callable

import lxml.etree

from colour_clf_io.elements import (
    Array,
    ExponentParams,
    LogParams,
    SatNode,
    SOPNode,
)
from colour_clf_io.errors import ParsingError, ValidationError
from colour_clf_io.parsing import (
    ParserConfig,
    XMLParsable,
    XMLWritable,
    child_element,
    child_elements,
    element_as_float,
    elements_as_text_list,
    map_optional,
    retrieve_attributes,
    set_attr_if_not_none,
    set_element_if_not_none,
    sliding_window,
)
from colour_clf_io.values import (
    ASC_CDLStyle,
    BitDepth,
    ExponentStyle,
    Interpolation1D,
    Interpolation3D,
    LogStyle,
    RangeStyle,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "PROCESSING_NODE_CONSTRUCTORS",
    "register_process_node_xml_constructor",
    "ProcessNode",
    "assert_bit_depth_compatibility",
    "parse_process_node",
    "LUT1D",
    "LUT3D",
    "Matrix",
    "Range",
    "Log",
    "Exponent",
    "ASC_CDL",
]

PROCESSING_NODE_CONSTRUCTORS: dict = {}
"""
Hold the processing node constructors.
"""


def register_process_node_xml_constructor(name: str) -> Callable:
    """
    Add the constructor method to the :attr:`PROCESSING_NODE_CONSTRUCTORS`
    dictionary. Adds the wrapped function as value with the given name as key.

    Parameters
    ----------
    name
        Name to use as key for adding.
    """

    def register(constructor: Callable) -> Callable:
        """Register the given callable."""

        PROCESSING_NODE_CONSTRUCTORS[name] = constructor

        return constructor

    return register


@dataclass
class ProcessNode(XMLParsable, XMLWritable, ABC):
    """
    Represent a *ProcessNode*, an operation to be applied to the image data.

    At least one *ProcessNode* sub-class must be included in a
    :class:`colour_clf_io.ProcessList` class instance. The base *ProcessNode*
    class contains attributes and elements that are common to and inherited
    by the specific sub-types of the *ProcessNode* class.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processNode
    """

    id: str | None
    """A unique identifier for the *ProcessNode*."""

    name: str | None
    """
    A concise string defining a name for the *ProcessNode* that can be used
    by an application for display in a user interface.
    """

    in_bit_depth: BitDepth
    """
    A string that is used by some *ProcessNodes* to indicate how array or
    parameter values have been scaled.
    """

    out_bit_depth: BitDepth
    """
    A string that is used by some *ProcessNodes* to indicate how array or
    parameter values have been scaled.
    """

    description: list[str] | None
    """
    An arbitrary string for describing the function, usage, or notes about the
    *ProcessNode*.
    """

    @staticmethod
    def parse_attributes(xml: lxml.etree._Element, config: ParserConfig) -> dict:
        """
        Parse the default attributes of a *ProcessNode* and return them as a
        dictionary of names and their values.

        Parameters
        ----------
        xml
            XML element to parse.
        config
            XML parser config.

        Returns
        -------
        :class:`dict`
            *dict* of attribute names and their values.
        """

        attributes = retrieve_attributes(
            xml,
            {
                "id": "id",
                "name": "name",
            },
        )
        in_bit_depth = BitDepth(xml.get("inBitDepth"))
        out_bit_depth = BitDepth(xml.get("outBitDepth"))
        description = elements_as_text_list(xml, "Description", config)

        return {
            "in_bit_depth": in_bit_depth,
            "out_bit_depth": out_bit_depth,
            "description": description,
            **attributes,
        }

    def write_process_node_attributes(self, node: lxml.etree._Element) -> None:
        """
        Add the data of the *ProcessNode* as attributes to the given XML node.

        Parameters
        ----------
        node
            Target node that will receive the new attributes.
        """
        set_attr_if_not_none(node, "id", self.id)
        set_attr_if_not_none(node, "name", self.name)
        set_attr_if_not_none(node, "inBitDepth", self.in_bit_depth.value)
        set_attr_if_not_none(node, "outBitDepth", self.out_bit_depth.value)
        if self.description is None:
            return
        for description_text in self.description:
            description_element = lxml.etree.SubElement(node, "Description")
            description_element.text = description_text


def assert_bit_depth_compatibility(process_nodes: list[ProcessNode]) -> bool:
    """
    Check that the input and output values of adjacent process nodes are
    compatible. Return true if all nodes are compatible, false otherwise.

    Examples
    --------
    >>> from colour_clf_io.process_nodes import assert_bit_depth_compatibility, LUT1D
    >>> from colour_clf_io.elements import Array
    >>> lut = Array(values=[0, 1], dim=(2, 1))
    >>> node_i8 = LUT1D(
    ...     id=None,
    ...     name=None,
    ...     description=None,
    ...     half_domain=False,
    ...     raw_halfs=False,
    ...     interpolation=None,
    ...     array=lut,
    ...     in_bit_depth=BitDepth.i8,
    ...     out_bit_depth=BitDepth.i8,
    ... )
    >>> node_f16 = LUT1D(
    ...     id=None,
    ...     name=None,
    ...     description=None,
    ...     half_domain=False,
    ...     raw_halfs=False,
    ...     interpolation=None,
    ...     array=lut,
    ...     in_bit_depth=BitDepth.f16,
    ...     out_bit_depth=BitDepth.f16,
    ... )
    >>> assert_bit_depth_compatibility([node_i8, node_i8])
    True
    >>> assert_bit_depth_compatibility(
    ...     [node_i8, node_f16]
    ... )  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValidationError: ...
    """

    for node_a, node_b in sliding_window(process_nodes, 2):
        is_compatible = node_a.out_bit_depth == node_b.in_bit_depth
        if not is_compatible:
            exception = (
                f"Encountered incompatible bit depth between two processing nodes: "
                f"{node_a} and {node_b}"
            )

            raise ValidationError(exception)

    return True


def parse_process_node(xml: lxml.etree._Element, config: ParserConfig) -> ProcessNode:
    """
    Return the *ProcessNode* that corresponds to given XML element.

    Parameters
    ----------
    xml
        XML element to parse.
    config
        XML parser config.

    Returns
    -------
    :class: colour.clf.ProcessNode
        A subclass of `ProcessNode` that represents the given Process Node.

    Raises
    ------
    :class: ParsingError
        If the given element does not match any valid process node, or the node does not
        correctly correspond to the specification.
    """

    tag = lxml.etree.QName(xml).localname
    constructor = PROCESSING_NODE_CONSTRUCTORS.get(tag)

    if constructor is not None:
        return PROCESSING_NODE_CONSTRUCTORS[tag](xml, config)

    exception = f"Encountered invalid processing node with tag '{xml.tag}'"

    raise ParsingError(exception)


@dataclass
class LUT1D(ProcessNode):
    """
    Represent a *LUT1D* element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#lut1d
    """

    array: Array
    half_domain: bool
    raw_halfs: bool
    interpolation: Interpolation1D | None

    @staticmethod
    @register_process_node_xml_constructor("LUT1D")
    def from_xml(xml: lxml.etree._Element | None, config: ParserConfig) -> LUT1D | None:
        """
        Parse and return a :class:`colour_clf_io.LUT1D` class instance from the
        given XML element. Returns `None`` if the given XML element is ``None``.

        Expects the XML element to be a valid element according to the *CLF*
        specification.

        Parameters
        ----------
        xml
            XML element to parse.
        config
            XML parser config.

        Returns
        -------
        class:`colour_clf_io.LUT1D` or :py:data:`None`
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

        super_args = ProcessNode.parse_attributes(xml, config)
        array = Array.from_xml(child_element(xml, "Array", config), config)

        if array is None:
            exception = "LUT1D processing node does not have an Array element."

            raise ParsingError(exception)

        half_domain = xml.get("halfDomain") == "true"
        raw_halfs = xml.get("rawHalfs") == "true"
        interpolation = map_optional(Interpolation1D, xml.get("interpolation"))
        return LUT1D(
            array=array,
            half_domain=half_domain,
            raw_halfs=raw_halfs,
            interpolation=interpolation,
            **super_args,
        )

    def to_xml(self) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Returns
        -------
        :class:`lxml.etree._Element`
        """
        xml = lxml.etree.Element("LUT1D")
        self.write_process_node_attributes(xml)
        if self.half_domain:
            xml.set("halfDomain", "true")
        if self.raw_halfs:
            xml.set("rawHalfs", "true")
        if self.interpolation is not None:
            xml.set("interpolation", self.interpolation.value)
        xml.append(self.array.to_xml())
        return xml


@dataclass
class LUT3D(ProcessNode):
    """
    Represent a *LUT3D* element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#lut3d
    """

    array: Array
    half_domain: bool
    raw_halfs: bool
    interpolation: Interpolation3D | None

    @staticmethod
    @register_process_node_xml_constructor("LUT3D")
    def from_xml(xml: lxml.etree._Element | None, config: ParserConfig) -> LUT3D | None:
        """
        Parse and return a :class:`colour_clf_io.LUT3D` class instance from the
        given XML element. Returns `None`` if the given XML element is ``None``.

        Expects the XML element to be a valid element according to the *CLF*
        specification.

        Parameters
        ----------
        xml
            XML element to parse.
        config
            XML parser config.

        Returns
        -------
        class:`colour_clf_io.LUT3D` or :py:data:`None`
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

        super_args = ProcessNode.parse_attributes(xml, config)
        array = Array.from_xml(child_element(xml, "Array", config), config)

        if array is None:
            exception = "LUT3D processing node does not have an Array element."

            raise ParsingError(exception)

        half_domain = xml.get("halfDomain") == "true"
        raw_halfs = xml.get("rawHalfs") == "true"
        interpolation = Interpolation3D(xml.get("interpolation"))

        return LUT3D(
            array=array,
            half_domain=half_domain,
            raw_halfs=raw_halfs,
            interpolation=interpolation,
            **super_args,
        )

    def to_xml(self) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Returns
        -------
        :class:`lxml.etree._Element`
        """
        xml = lxml.etree.Element("LUT3D")
        self.write_process_node_attributes(xml)
        if self.half_domain:
            xml.set("halfDomain", "true")
        if self.raw_halfs:
            xml.set("rawHalfs", "true")
        if self.interpolation is not None:
            xml.set("interpolation", self.interpolation.value)
        xml.append(self.array.to_xml())
        return xml


@dataclass
class Matrix(ProcessNode):
    """
    Represent a *Matrix* element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#matrix
    """

    array: Array

    @staticmethod
    @register_process_node_xml_constructor("Matrix")
    def from_xml(
        xml: lxml.etree._Element | None, config: ParserConfig
    ) -> Matrix | None:
        """
        Parse and return a :class:`colour_clf_io.Matrix` class instance from
        the given XML element. Returns `None`` if the given XML element is ``None``.

        Expects the XML element to be a valid element according to the *CLF*
        specification.

        Parameters
        ----------
        xml
            XML element to parse.
        config
            XML parser config.

        Returns
        -------
         class:`colour_clf_io.Matrix` or :py:data:`None`
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

        super_args = ProcessNode.parse_attributes(xml, config)
        array = Array.from_xml(child_element(xml, "Array", config), config)

        if array is None:
            exception = "Matrix processing node does not have an Array element."
            raise ParsingError(exception)

        return Matrix(array=array, **super_args)

    def to_xml(self) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Returns
        -------
        :class:`lxml.etree._Element`
        """
        xml = lxml.etree.Element("Matrix")
        self.write_process_node_attributes(xml)
        xml.append(self.array.to_xml())
        return xml


@dataclass
class Range(ProcessNode):
    """
    Represent a *Range* element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#range
    """

    min_in_value: float | None
    max_in_value: float | None
    min_out_value: float | None
    max_out_value: float | None

    style: RangeStyle | None

    @staticmethod
    @register_process_node_xml_constructor("Range")
    def from_xml(xml: lxml.etree._Element | None, config: ParserConfig) -> Range | None:
        """
        Parse and return a :class:`colour_clf_io.Range` class instance from the
        given XML element. Returns `None`` if the given XML element is ``None``.

        Expects the XML element to be a valid element according to the *CLF*
        specification.

        Parameters
        ----------
        xml
            XML element to parse.
        config
            XML parser config.

        Returns
        -------
         class:`colour_clf_io.Range` or :py:data:`None`
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

        super_args = ProcessNode.parse_attributes(xml, config)

        def optional_float(name: str) -> float | None:
            """Convert given name to float."""

            return element_as_float(xml, name, config)

        min_in_value = optional_float("minInValue")
        max_in_value = optional_float("maxInValue")
        min_out_value = optional_float("minOutValue")
        max_out_value = optional_float("maxOutValue")

        style = map_optional(RangeStyle, xml.get("style"))

        return Range(
            min_in_value=min_in_value,
            max_in_value=max_in_value,
            min_out_value=min_out_value,
            max_out_value=max_out_value,
            style=style,
            **super_args,
        )

    def to_xml(self) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Returns
        -------
        :class:`lxml.etree._Element`
        """
        xml = lxml.etree.Element("Range")
        self.write_process_node_attributes(xml)
        set_element_if_not_none(xml, "minInValue", self.min_in_value)
        set_element_if_not_none(xml, "maxInValue", self.max_in_value)
        set_element_if_not_none(xml, "minOutValue", self.min_out_value)
        set_element_if_not_none(xml, "maxOutValue", self.max_out_value)
        if self.style is not None:
            xml.set("style", self.style.value)
        return xml


@dataclass
class Log(ProcessNode):
    """
    Represent a *Log* element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#log
    """

    style: LogStyle
    log_params: list[LogParams]

    @staticmethod
    @register_process_node_xml_constructor("Log")
    def from_xml(xml: lxml.etree._Element | None, config: ParserConfig) -> Log | None:
        """
        Parse and return a :class:`colour_clf_io.Log` class instance from the
        given XML element. Returns `None`` if the given XML element is ``None``.

        Expects the XML element to be a valid element according to the *CLF*
        specification.

        Parameters
        ----------
        xml
            XML element to parse.
        config
            XML parser config.

        Returns
        -------
         class:`colour_clf_io.Log` or :py:data:`None`
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

        super_args = ProcessNode.parse_attributes(xml, config)
        style = LogStyle(xml.get("style"))
        param_elements = child_elements(xml, "LogParams", config)
        params = [
            param
            for param in [
                LogParams.from_xml(param_element, config)
                for param_element in param_elements
            ]
            if param is not None
        ]

        return Log(style=style, log_params=params, **super_args)

    def to_xml(self) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Returns
        -------
        :class:`lxml.etree._Element`
        """
        xml = lxml.etree.Element("Log")
        self.write_process_node_attributes(xml)
        xml.set("style", self.style.value)
        for log_params in self.log_params:
            xml.append(log_params.to_xml())
        return xml


@dataclass
class Exponent(ProcessNode):
    """
    Represent an *Exponent* element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#exponent
    """

    style: ExponentStyle
    exponent_params: list[ExponentParams]

    @staticmethod
    @register_process_node_xml_constructor("Exponent")
    def from_xml(
        xml: lxml.etree._Element | None, config: ParserConfig
    ) -> Exponent | None:
        """
        Parse and return a :class:`colour_clf_io.Exponent` class instance from
        the given XML element. Returns `None`` if the given XML element is ``None``.

        Expects the XML element to be a valid element according to the *CLF*
        specification.

        Parameters
        ----------
        xml
            XML element to parse.
        config
            XML parser config.

        Returns
        -------
         class:`colour_clf_io.Exponent` or :py:data:`None`
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

        super_args = ProcessNode.parse_attributes(xml, config)
        style = map_optional(ExponentStyle, xml.get("style"))

        if style is None:
            exception = "Exponent process node has no `style' value."

            raise ParsingError(exception)

        param_elements = child_elements(xml, "ExponentParams", config)
        params = [
            param
            for param in [
                ExponentParams.from_xml(param_element, config)
                for param_element in param_elements
            ]
            if param is not None
        ]

        if not params:
            exception = "Exponent process node has no `ExponentParams' element."

            raise ParsingError(exception)

        return Exponent(style=style, exponent_params=params, **super_args)

    def to_xml(self) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Returns
        -------
        :class:`lxml.etree._Element`
        """
        xml = lxml.etree.Element("Exponent")
        self.write_process_node_attributes(xml)
        xml.set("style", self.style.value)
        for exponent_params in self.exponent_params:
            xml.append(exponent_params.to_xml())
        return xml


@dataclass
class ASC_CDL(ProcessNode):
    """
    Represent an *ASC_CDL* element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    style: ASC_CDLStyle
    sopnode: SOPNode | None
    sat_node: SatNode | None

    @staticmethod
    @register_process_node_xml_constructor("ASC_CDL")
    def from_xml(
        xml: lxml.etree._Element | None, config: ParserConfig
    ) -> ASC_CDL | None:
        """
        Parse and return a :class:`colour_clf_io.ASC_CDL` class instance from
        the given XML element. Returns `None`` if the given XML element is ``None``.

        Expects the XML element to be a valid element according to the *CLF*
        specification.

        Parameters
        ----------
        xml
            XML element to parse.
        config
            XML parser config.

        Returns
        -------
         class:`colour_clf_io.ASC_CDL` or :py:data:`None`
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

        super_args = ProcessNode.parse_attributes(xml, config)
        style = ASC_CDLStyle(xml.get("style"))
        sop_node = SOPNode.from_xml(child_element(xml, "SOPNode", config), config)
        sat_node = SatNode.from_xml(child_element(xml, "SatNode", config), config)

        return ASC_CDL(style=style, sopnode=sop_node, sat_node=sat_node, **super_args)

    def to_xml(self) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Returns
        -------
        :class:`lxml.etree._Element`
        """
        xml = lxml.etree.Element("ASC_CDL")
        self.write_process_node_attributes(xml)
        xml.set("style", self.style.value)
        if self.sopnode is not None:
            xml.append(self.sopnode.to_xml())
        if self.sat_node is not None:
            xml.append(self.sat_node.to_xml())
        return xml
