"""
Elements
========

Defines objects that hold data from elements contained in a CLF document. These
typically are child elements of Process Nodes.

"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from typing_extensions import Self

from colour_clf_io.errors import ParsingError
from colour_clf_io.parsing import (
    ParserConfig,
    XMLParsable,
    child_element,
    child_element_or_exception,
    map_optional,
    retrieve_attributes,
    retrieve_attributes_as_float,
    three_floats,
)
from colour_clf_io.values import Channel

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__ALL__ = [
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
    https://docs.acescentral.com/specifications/clf/#array
    """

    values: list[float]
    dim: tuple[int, ...]

    @classmethod
    def from_xml(cls, xml, config: ParserConfig) -> Self | None:  # noqa: ARG003
        """
        Parse and return the Array from the given XML node. Returns None if the given
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
        dim = tuple(map(int, xml.get("dim").split()))
        values = list(map(float, xml.text.split()))
        return cls(values=values, dim=dim)

    def as_array(self):
        """
        Convert the CLF element into a numpy array.

        Returns
        -------
        :class:`numpy.ndarray`
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
    https://docs.acescentral.com/specifications/clf/#processlist
    """

    display_device_serial_num: str | None
    display_device_host_name: str | None
    operator_name: str | None
    calibration_date_time: str | None
    measurement_probe: str | None
    calibration_software_name: str | None
    calibration_software_version: str | None

    @classmethod
    def from_xml(cls, xml, config: ParserConfig) -> Self | None:  # noqa: ARG003
        """
        Parse and return the Calibration Info from the given XML node. Returns None
        if the given element is None.

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
        return cls(**attributes)


class RangeStyle(enum.Enum):
    """
    Represents the valid values of the style attribute within a Range element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#range
    """

    CLAMP = "Clamp"
    NO_CLAMP = "noClamp"


class LogStyle(enum.Enum):
    """
    Represents the valid values of the style attribute in a Log element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#processList
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
    https://docs.acescentral.com/specifications/clf/#exponent
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
    https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    slope: tuple[float, float, float]
    offset: tuple[float, float, float]
    power: tuple[float, float, float]

    @classmethod
    def from_xml(cls, xml, config: ParserConfig) -> Self | None:
        """
        Parse and return the SOPNode from the given XML node. Returns None if the given
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
        slope = three_floats(child_element_or_exception(xml, "Slope", config).text)
        offset = three_floats(child_element_or_exception(xml, "Offset", config).text)
        power = three_floats(child_element_or_exception(xml, "Power", config).text)
        return cls(slope=slope, offset=offset, power=power)


@dataclass
class SatNode(XMLParsable):
    """
    Represents a SatNode element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    saturation: float

    @classmethod
    def from_xml(cls, xml, config: ParserConfig) -> Self | None:
        """
        Parse and return the SatNode from the given XML node. Returns None if the given
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
        saturation = child_element_or_exception(xml, "Saturation", config).text
        if saturation is None:
            raise ParsingError("Saturation node in SatNode contains no value.")
        saturation = float(saturation)
        return cls(saturation=saturation)


@dataclass
class Info(XMLParsable):
    """
    Represents a Info element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#processList
    """

    app_release: str | None
    copyright: str | None
    revision: str | None
    aces_transform_id: str | None
    aces_user_name: str | None
    calibration_info: CalibrationInfo | None

    @classmethod
    def from_xml(cls, xml, config: ParserConfig) -> Self | None:
        """
        Parse and return the Info from the given XML node. Returns None if the given
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
            child_element(xml, "CalibrationInfo", config), config
        )
        return cls(calibration_info=calibration_info, **attributes)


@dataclass
class LogParams(XMLParsable):
    """
    Represents a Log Param List element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#log
    """

    base: float | None
    log_side_slope: float | None
    log_side_offset: float | None
    lin_side_slope: float | None
    lin_side_offset: float | None
    lin_side_break: float | None
    linear_slope: float | None
    channel: Channel | None

    @classmethod
    def from_xml(cls, xml, config: ParserConfig) -> Self | None:  # noqa: ARG003
        """
        Parse and return the Log Param from the given XML node. Returns None if the
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

        return cls(channel=channel, **attributes)


@dataclass
class ExponentParams(XMLParsable):
    """
    Represents a Exponent Params element.

    References
    ----------
    https://docs.acescentral.com/specifications/clf/#exponent
    """

    exponent: float
    offset: float | None
    channel: Channel | None

    @classmethod
    def from_xml(cls, xml, config: ParserConfig) -> Self | None:  # noqa: ARG003
        """
        Parse and return the Exponent Params from the given XML node. Returns None if
        the given element is None.

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
        attributes = retrieve_attributes_as_float(
            xml,
            {
                "exponent": "exponent",
                "offset": "offset",
            },
        )
        exponent = attributes.pop("exponent")
        if exponent is None:
            raise ParsingError("Exponent process node has no `exponent' value.")
        channel = map_optional(Channel, xml.get("channel"))

        return cls(channel=channel, exponent=exponent, **attributes)
