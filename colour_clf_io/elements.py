"""
Elements
========

Defines objects that hold data from elements contained in a CLF document. These
typically are child elements of Process Nodes.
"""

from __future__ import annotations

import enum
import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    import numpy.typing as npt

if typing.TYPE_CHECKING:
    import lxml.etree

from colour_clf_io.errors import ParsingError
from colour_clf_io.parsing import (
    ParserConfig,
    XMLParsable,
    child_element,
    child_element_or_exception,
    map_optional,
    must_have,
    retrieve_attributes,
    retrieve_attributes_as_float,
    three_floats,
)
from colour_clf_io.values import Channel

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "Array",
    "CalibrationInfo",
    "RangeStyle",
    "LogStyle",
    "ExponentStyle",
    "SOPNode",
    "SatNode",
    "Info",
    "LogParams",
    "ExponentParams",
]


@dataclass
class Array(XMLParsable):
    """
    Represents an Array element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#array
    """

    values: list[float]
    dim: tuple[int, ...]

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None,
        config: ParserConfig,  # noqa: ARG004
    ) -> Array | None:
        """
        Parse and return a :class:`colour_clf_io.Array` class instance from the
        given XML node. Returns `None`` if the given XML node is ``None``.

        Expects the xml element to be a valid element according to the CLF
        specification.

        Returns
        -------
        class:`colour_clf_io.Array` or :py:data:`None`
            Parsed XML node.

        Raises
        ------
        :class:`ParsingError`
            If the node does not conform to the specification, a ``ParsingError``
            exception will be raised. The error message will indicate the
            details of the issue that was encountered.
        """

        if xml is None:
            return None

        dim = xml.get("dim")
        must_have(
            xml,
            'Array must have a "dim" attribute',
        )

        dimensions = tuple(map(int, dim.split()))  # pyright: ignore
        values = list(map(float, xml.text.split()))  # pyright: ignore

        return Array(values=values, dim=dimensions)

    def as_array(self) -> npt.NDArray:
        """
        Convert the CLF element into a numpy array.

        Returns
        -------
        :class:`numpy`ndarray``
            Array of shape `dim` with the data from `values`.
        """

        import numpy as np

        dim = self.dim
        # Strip the dimensions with value 1.
        while dim[-1] == 1:
            dim = dim[:-1]
        return np.array(self.values).reshape(dim)


@dataclass
class CalibrationInfo(XMLParsable):
    """
    Represents a Calibration Info element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processlist
    """

    display_device_serial_num: str | None
    display_device_host_name: str | None
    operator_name: str | None
    calibration_date_time: str | None
    measurement_probe: str | None
    calibration_software_name: str | None
    calibration_software_version: str | None

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None,
        config: ParserConfig,  # noqa: ARG004
    ) -> CalibrationInfo | None:
        """
        Parse and return a :class:`colour_clf_io.CalibrationInfo` class instance
        from the given XML node. Returns `None`` if the given XML node is ``None``.

        Expects the xml element to be a valid element according to the CLF
        specification.

        Returns
        -------
        class:`colour_clf_io.CalibrationInfo` or :py:data:`None`
            Parsed XML node.

        Raises
        ------
        :class:`ParsingError`
            If the node does not conform to the specification, a ``ParsingError``
            exception will be raised. The error message will indicate the
            details of the issue that was encountered.
        """

        if xml is None:
            return None

        attributes = retrieve_attributes(
            xml,
            {
                "display_device_serial_num": "DisplayDeviceSerialNum",
                "display_device_host_name": "DisplayDeviceHostName",
                "operator_name": "OperatorName",
                "calibration_date_time": "CalibrationDateTime",
                "measurement_probe": "MeasurementProbe",
                "calibration_software_name": "CalibrationSoftwareName",
                "calibration_software_version": "CalibrationSoftwareVersion",
            },
        )

        return CalibrationInfo(**attributes)


class RangeStyle(enum.Enum):
    """
    Represents the valid values of the style attribute within a Range element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#range
    """

    CLAMP = "Clamp"
    NO_CLAMP = "noClamp"


class LogStyle(enum.Enum):
    """
    Represents the valid values of the style attribute in a Log element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processList
    """

    LOG_10 = "log10"
    ANTI_LOG_10 = "antiLog10"
    LOG_2 = "log2"
    ANTI_LOG_2 = "antiLog2"
    LIN_TO_LOG = "linToLog"
    LOG_TO_LIN = "logToLin"
    CAMERA_LIN_TO_LOG = "cameraLinToLog"
    CAMERA_LOG_TO_LIN = "cameraLogToLin"


class ExponentStyle(enum.Enum):
    """
    Represents the valid values of the style attribute of an Exponent element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#exponent
    """

    BASIC_FWD = "basicFwd"
    BASIC_REV = "basicRev"
    BASIC_MIRROR_FWD = "basicMirrorFwd"
    BASIC_MIRROR_REV = "basicMirrorRev"
    BASIC_PASS_THRU_FWD = "basicPassThruFwd"  # noqa: S105
    BASIC_PASS_THRU_REV = "basicPassThruRev"  # noqa: S105
    MON_CURVE_FWD = "monCurveFwd"
    MON_CURVE_REV = "monCurveRev"
    MON_CURVE_MIRROR_FWD = "monCurveMirrorFwd"
    MON_CURVE_MIRROR_REV = "monCurveMirrorRev"


@dataclass
class SOPNode(XMLParsable):
    """
    Represents a SOPNode element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    slope: tuple[float, float, float]
    offset: tuple[float, float, float]
    power: tuple[float, float, float]

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None, config: ParserConfig
    ) -> SOPNode | None:
        """
        Parse and return a :class:`colour_clf_io.SOPNode` class instance from the
        given XML node. Returns `None`` if the given XML node is ``None``.

        Expects the xml element to be a valid element according to the CLF
        specification.

        Returns
        -------
        class:`colour_clf_io.SOPNode` or :py:data:`None`
            Parsed XML node.

        Raises
        ------
        :class:`ParsingError`
            If the node does not conform to the specification, a ``ParsingError``
            exception will be raised. The error message will indicate the
            details of the issue that was encountered.
        """

        if xml is None:
            return None

        slope = three_floats(child_element_or_exception(xml, "Slope", config).text)
        offset = three_floats(child_element_or_exception(xml, "Offset", config).text)
        power = three_floats(child_element_or_exception(xml, "Power", config).text)

        return SOPNode(slope=slope, offset=offset, power=power)


@dataclass
class SatNode(XMLParsable):
    """
    Represents a SatNode element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    saturation: float

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None, config: ParserConfig
    ) -> SatNode | None:
        """
        Parse and return a :class:`colour_clf_io.SatNode` class instance from the
        given XML node. Returns `None`` if the given XML node is ``None``.

        Expects the xml element to be a valid element according to the CLF
        specification.

        Returns
        -------
        class:`colour_clf_io.SatNode` or :py:data:`None`
            Parsed XML node.

        Raises
        ------
        :class:`ParsingError`
            If the node does not conform to the specification, a ``ParsingError``
            exception will be raised. The error message will indicate the
            details of the issue that was encountered.
        """

        if xml is None:
            return None

        saturation = child_element_or_exception(xml, "Saturation", config).text
        if saturation is None:
            exception = "Saturation node in SatNode contains no value."

            raise ParsingError(exception)

        saturation = float(saturation)

        return SatNode(saturation=saturation)


@dataclass
class Info(XMLParsable):
    """
    Represents a Info element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processList
    """

    app_release: str | None
    copyright: str | None
    revision: str | None
    aces_transform_id: str | None
    aces_user_name: str | None
    calibration_info: CalibrationInfo | None

    @staticmethod
    def from_xml(xml: lxml.etree._Element | None, config: ParserConfig) -> Info | None:
        """
        Parse and return a :class:`colour_clf_io.Info` class instance from the
        given XML node. Returns `None`` if the given XML node is ``None``.

        Expects the xml element to be a valid element according to the CLF
        specification.

        Returns
        -------
        class:`colour_clf_io.Info` or :py:data:`None`
            Parsed XML node.

        Raises
        ------
        :class:`ParsingError`
            If the node does not conform to the specification, a ``ParsingError``
            exception will be raised. The error message will indicate the
            details of the issue that was encountered.
        """

        if xml is None:
            return None

        attributes = retrieve_attributes(
            xml,
            {
                "app_release": "AppRelease",
                "copyright": "Copyright",
                "revision": "Revision",
                "aces_transform_id": "ACEStransformID",
                "aces_user_name": "ACESuserName",
            },
        )
        calibration_info = CalibrationInfo.from_xml(
            child_element(xml, "CalibrationInfo", config),  # pyright: ignore
            config,
        )

        return Info(calibration_info=calibration_info, **attributes)


@dataclass
class LogParams(XMLParsable):
    """
    Represents a Log Param List element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#log
    """

    base: float | None
    log_side_slope: float | None
    log_side_offset: float | None
    lin_side_slope: float | None
    lin_side_offset: float | None
    lin_side_break: float | None
    linear_slope: float | None
    channel: Channel | None

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None,
        config: ParserConfig,  # noqa: ARG004
    ) -> LogParams | None:
        """
        Parse and return a :class:`colour_clf_io.LogParams` class instance from
        the given XML node. Returns `None`` if the given XML node is ``None``.

        Expects the xml element to be a valid element according to the CLF
        specification.

        Returns
        -------
        class:`colour_clf_io.LogParams` or :py:data:`None`
            Parsed XML node.

        Raises
        ------
        :class:`ParsingError`
            If the node does not conform to the specification, a ``ParsingError``
            exception will be raised. The error message will indicate the
            details of the issue that was encountered.
        """

        if xml is None:
            return None

        attributes = retrieve_attributes_as_float(
            xml,
            {
                "base": "base",
                "log_side_slope": "logSideSlope",
                "log_side_offset": "logSideOffset",
                "lin_side_slope": "linSideSlope",
                "lin_side_offset": "linSideOffset",
                "lin_side_break": "linSideBreak",
                "linear_slope": "linearSlope",
            },
        )

        channel = map_optional(Channel, xml.get("channel"))

        return LogParams(channel=channel, **attributes)


@dataclass
class ExponentParams(XMLParsable):
    """
    Represents a Exponent Params element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#exponent
    """

    exponent: float
    offset: float | None
    channel: Channel | None

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None,
        config: ParserConfig,  # noqa: ARG004
    ) -> ExponentParams | None:
        """
        Parse and return a :class:`colour_clf_io.ExponentParams` class instance
        from the given XML node. Returns `None`` if the given XML node is ``None``.

        Expects the xml element to be a valid element according to the CLF
        specification.

        Returns
        -------
        class:`colour_clf_io.ExponentParams` or :py:data:`None`
            Parsed XML node.

        Raises
        ------
        :class:`ParsingError`
            If the node does not conform to the specification, a ``ParsingError``
            exception will be raised. The error message will indicate the
            details of the issue that was encountered.
        """

        if xml is None:
            return None

        attributes = retrieve_attributes_as_float(
            xml,
            {
                "exponent": "exponent",
                "offset": "offset",
            },
        )
        exponent = attributes.pop("exponent")

        if exponent is None:
            exception = "Exponent process node has no `exponent' value."

            raise ParsingError(exception)

        channel = map_optional(Channel, xml.get("channel"))

        return ExponentParams(channel=channel, exponent=exponent, **attributes)
