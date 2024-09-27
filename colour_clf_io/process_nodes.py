"""
Process Nodes
============

Defines the available process nodes in a CLF document.

"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

import lxml.etree

from colour_clf_io.elements import (
    Array,
    ExponentParams,
    ExponentStyle,
    LogParams,
    LogStyle,
    RangeStyle,
    SatNode,
    SOPNode,
)
from colour_clf_io.errors import ParsingError, ValidationError
from colour_clf_io.parsing import (
    ParserConfig,
    XMLParsable,
    child_element,
    element_as_text,
    map_optional,
    retrieve_attributes,
    sliding_window,
)
from colour_clf_io.values import (
    ASC_CDL_Style,
    BitDepth,
    Interpolation1D,
    Interpolation3D,
)

__ALL__ = [
    "ProcessNode",
    "LUT1D",
    "LUT3D",
    "Matrix",
    "Range",
    "Log",
    "Exponent",
    "ASC_CDL",
]

processing_node_constructors = {}


def register_process_node_xml_constructor(name):
    """
    Add the constructor method to the `processing_node_constructors` dictionary.
    Adds the wrapped function as value with the given name as key.

    Parameters
    ----------
    name
        Name to use as key for adding.

    """

    def register(constructor):
        processing_node_constructors[name] = constructor
        return constructor

    return register


@dataclass
class ProcessNode(XMLParsable, ABC):
    """
    Represents the common data of all Process Node elements.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#processNode
    """

    id: str | None
    name: str | None
    in_bit_depth: BitDepth
    out_bit_depth: BitDepth
    description: str | None

    @staticmethod
    def parse_attributes(xml, config: ParserConfig) -> dict:
        """
        Parse the default attributes of a *ProcessNode* and return them as a dictionary
        of names and their values.

        Parameters
        ----------
        xml
            Source XML element.
        config
            Additional parser configuration.

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
        description = element_as_text(xml, "Description", config)
        args = {
            "in_bit_depth": in_bit_depth,
            "out_bit_depth": out_bit_depth,
            "description": description,
            **attributes,
        }
        return args


def assert_bit_depth_compatibility(process_nodes: list[ProcessNode]) -> bool:
    """Check that the input and output values of adjacent process nodes are
    compatible. Return true if all nodes are compatible, false otherwise.

    Examples
    --------
    ```
    >>> from colour_clf_io.process_nodes import assert_bit_depth_compatibility, LUT1D
    >>> from colour_clf_io.elements import Array
    >>> lut = Array(values=[0,1], dim=(2,1))
    >>> node_i8 = LUT1D( \
        id=None, \
        name=None, \
        description=None, \
        half_domain=False, \
        raw_halfs=False, \
        interpolation = None, \
        array=lut, \
        in_bit_depth=BitDepth.i8, \
        out_bit_depth=BitDepth.i8 )
    >>> node_f16 = LUT1D( \
        id=None, \
        name=None, \
        description=None, \
        half_domain=False, \
        raw_halfs=False, \
        interpolation = None, \
        array=lut, \
        in_bit_depth=BitDepth.f16, \
        out_bit_depth=BitDepth.f16 )
    >>> assert_bit_depth_compatibility([node_i8, node_i8])
    True
    >>> assert_bit_depth_compatibility(
    ... [node_i8, node_f16]) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValidationError: ...
    ```
    """
    for node_a, node_b in sliding_window(process_nodes, 2):
        is_compatible = node_a.out_bit_depth == node_b.in_bit_depth
        if not is_compatible:
            raise ValidationError(
                f"Encountered incompatible bit depth between two processing nodes: "
                f"{node_a} and {node_b}"
            )
    return True


def parse_process_node(xml, config: ParserConfig):
    """
    Return the correct process node that corresponds to this XML element.

    Returns
    -------
    :class: colour.clf.ProcessNode
        A subclass of `ProcessNode` that represents the given Process Node.

    Raises
    ------
    :class: ParsingError
        If the given element does not match any valid process node, or the node does not
        correctly correspond to the specification..

    """
    tag = lxml.etree.QName(xml).localname
    constructor = processing_node_constructors.get(tag)
    if constructor is not None:
        return processing_node_constructors[tag](xml, config)
    raise ParsingError(f"Encountered invalid processing node with tag '{xml.tag}'")


@dataclass
class LUT1D(ProcessNode):
    """
    Represents a LUT1D element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#lut1d
    """

    array: Array
    half_domain: bool
    raw_halfs: bool
    interpolation: Interpolation1D | None

    @staticmethod
    @register_process_node_xml_constructor("LUT1D")
    def from_xml(xml, config: ParserConfig):
        """
        Parse and return the LUT1D from the given XML node. Returns None if the given
        element is None.

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
        super_args = ProcessNode.parse_attributes(xml, config)
        array = Array.from_xml(child_element(xml, "Array", config), config)
        if array is None:
            raise ParsingError("LUT1D processing node does not have an Array element.")

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


@dataclass
class LUT3D(ProcessNode):
    """
    Represents a LUT3D element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#lut3d
    """

    array: Array
    half_domain: bool
    raw_halfs: bool
    interpolation: Interpolation3D | None

    @staticmethod
    @register_process_node_xml_constructor("LUT3D")
    def from_xml(xml, config: ParserConfig):
        """
        Parse and return the LUT3D from the given XML node. Returns None if the given
        element is None.

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
        super_args = ProcessNode.parse_attributes(xml, config)
        array = Array.from_xml(child_element(xml, "Array", config), config)
        if array is None:
            raise ParsingError("LUT3D processing node does not have an Array element.")
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


@dataclass
class Matrix(ProcessNode):
    """
    Represents a Matrix element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#matrix
    """

    array: Array

    @staticmethod
    @register_process_node_xml_constructor("Matrix")
    def from_xml(xml, config: ParserConfig):
        """
        Parse and return the Matrix from the given XML node. Returns None if the given
        element is None.

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
        super_args = ProcessNode.parse_attributes(xml, config)
        array = Array.from_xml(child_element(xml, "Array", config), config)
        if array is None:
            raise ParsingError("Matrix processing node does not have an Array element.")
        return Matrix(array=array, **super_args)


@dataclass
class Range(ProcessNode):
    """
    Represents a Range element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#range
    """

    min_in_value: float | None
    max_in_value: float | None
    min_out_value: float | None
    max_out_value: float | None

    style: RangeStyle | None

    @staticmethod
    @register_process_node_xml_constructor("Range")
    def from_xml(xml, config: ParserConfig):
        """
        Parse and return the Range from the given XML node. Returns None if the given
        element is None.

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

        super_args = ProcessNode.parse_attributes(xml, config)

        min_in_value = float(element_as_text(xml, "minInValue", config))
        max_in_value = float(element_as_text(xml, "maxInValue", config))
        min_out_value = float(element_as_text(xml, "minOutValue", config))
        max_out_value = float(element_as_text(xml, "maxOutValue", config))

        style = map_optional(RangeStyle, xml.get("style"))

        return Range(
            min_in_value=min_in_value,
            max_in_value=max_in_value,
            min_out_value=min_out_value,
            max_out_value=max_out_value,
            style=style,
            **super_args,
        )


@dataclass
class Log(ProcessNode):
    """
    Represents a Log element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#log
    """

    style: LogStyle
    log_params: LogParams | None

    @staticmethod
    @register_process_node_xml_constructor("Log")
    def from_xml(xml, config: ParserConfig):
        """
        Parse and return the Log from the given XML node. Returns None if the given
        element is None.

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
        super_args = ProcessNode.parse_attributes(xml, config)
        style = LogStyle(xml.get("style"))
        param_element = child_element(xml, "LogParams", config)
        log_params = LogParams.from_xml(param_element, config)

        return Log(style=style, log_params=log_params, **super_args)


@dataclass
class Exponent(ProcessNode):
    """
    Represents a Exponent element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#exponent
    """

    style: ExponentStyle
    exponent_params: ExponentParams | None

    @staticmethod
    @register_process_node_xml_constructor("Exponent")
    def from_xml(xml, config: ParserConfig):
        """
        Parse and return the Exponent from the given XML node. Returns None if the given
        element is None.

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
        super_args = ProcessNode.parse_attributes(xml, config)
        style = map_optional(ExponentStyle, xml.get("style"))
        if style is None:
            raise ParsingError("Exponent process node has no `style' value.")
        param_element = child_element(xml, "ExponentParams", config)
        log_params = ExponentParams.from_xml(param_element, config)
        return Exponent(style=style, exponent_params=log_params, **super_args)


@dataclass
class ASC_CDL(ProcessNode):
    """
    Represents a ASC_CDL element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    style: ASC_CDL_Style
    sopnode: SOPNode | None
    sat_node: SatNode | None

    @staticmethod
    @register_process_node_xml_constructor("ASC_CDL")
    def from_xml(xml, config: ParserConfig):
        """
        Parse and return the ASC_CDL from the given XML node. Returns None if the given
        element is None.

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
        super_args = ProcessNode.parse_attributes(xml, config)
        style = ASC_CDL_Style(xml.get("style"))
        sopnode = SOPNode.from_xml(child_element(xml, "SOPNode", config), config)
        sat_node = SatNode.from_xml(child_element(xml, "SatNode", config), config)
        return ASC_CDL(style=style, sopnode=sopnode, sat_node=sat_node, **super_args)
