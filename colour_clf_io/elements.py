"""
Elements
========

Defines objects that hold data from elements contained in a *CLF* file. These
typically are child elements of *Process* Nodes.
"""

from __future__ import annotations

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
    check_none,
    child_element,
    child_element_or_exception,
    map_optional,
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
    "SOPNode",
    "SatNode",
    "Info",
    "LogParams",
    "ExponentParams",
]


@dataclass
class Array(XMLParsable):
    """
    Represent an *Array* element.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.Array.values`
    -   :attr:`~colour_clf_io.Array.dim`

    Methods
    -------
    -   :meth:`~colour_clf_io.Array.from_xml`
    -   :meth:`~colour_clf_io.Array.as_array`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#array
    """

    values: list[float]
    """Values contained by the element."""

    dim: tuple[int, ...]
    """
    Specifies the dimension of the LUT or the matrix and the number of
    colour components.
    """

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None,
        config: ParserConfig,  # noqa: ARG004
    ) -> Array | None:
        """
        Parse and return a :class:`colour_clf_io.Array` class instance from the
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
        class:`colour_clf_io.Array` or :py:data:`None`
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

        dim = xml.get("dim")
        check_none(
            xml,
            'Array must have a "dim" attribute',
        )

        dimensions = tuple(map(int, dim.split()))  # pyright: ignore
        values = list(map(float, xml.text.split()))  # pyright: ignore

        return Array(values=values, dim=dimensions)

    def as_array(self) -> npt.NDArray:
        """
        Convert the *CLF* element into a numpy array.

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
    Represent a *CalibrationInfo* container element for a
    :class:`colour_clf_io.ProcessList` class instance.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.CalibrationInfo.display_device_serial_num`
    -   :attr:`~colour_clf_io.CalibrationInfo.display_device_host_name`
    -   :attr:`~colour_clf_io.CalibrationInfo.operator_name`
    -   :attr:`~colour_clf_io.CalibrationInfo.calibration_date_time`
    -   :attr:`~colour_clf_io.CalibrationInfo.measurement_probe`
    -   :attr:`~colour_clf_io.CalibrationInfo.calibration_software_name`
    -   :attr:`~colour_clf_io.CalibrationInfo.calibration_software_version`

    Methods
    -------
    -   :meth:`~colour_clf_io.CalibrationInfo.from_xml`

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
        from the given XML element. Returns `None`` if the given XML element is
        ``None``.

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
        class:`colour_clf_io.CalibrationInfo` or :py:data:`None`
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


@dataclass
class SOPNode(XMLParsable):
    """
    Represent a *SOPNode* element for a :class:`colour_clf_io.ASC_CDL`
    *Process Node*.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.SOPNode.slope`
    -   :attr:`~colour_clf_io.SOPNode.offset`
    -   :attr:`~colour_clf_io.SOPNode.power`

    Methods
    -------
    -   :meth:`~colour_clf_io.SOPNode.from_xml`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    slope: tuple[float, float, float]
    """
    Three decimal values representing the R, G, and B slope values, which is
    similar to gain, but changes the slope of the transfer function without
    shifting the black level established by offset. Valid values for slope must
    be greater than or equal to zero. The nominal value is 1.0 for all channels.
    """

    offset: tuple[float, float, float]
    """
    Three decimal values representing the R, G, and B offset values, which
    raise or lower overall brightness of a color component by shifting the
    transfer function up or down while holding the slope constant. The nominal
    value is 0.0 for all channels.
    """

    power: tuple[float, float, float]
    """
    Three decimal values representing the R, G, and B power values, which
    change the intermediate shape of the transfer function. Valid values for
    power must be greater than zero. The nominal value is 1.0 for all channels.
    """

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None, config: ParserConfig
    ) -> SOPNode | None:
        """
        Parse and return a :class:`colour_clf_io.SOPNode` class instance from the
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
        class:`colour_clf_io.SOPNode` or :py:data:`None`
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

        slope = three_floats(child_element_or_exception(xml, "Slope", config).text)
        offset = three_floats(child_element_or_exception(xml, "Offset", config).text)
        power = three_floats(child_element_or_exception(xml, "Power", config).text)

        return SOPNode(slope=slope, offset=offset, power=power)

    @classmethod
    def default(cls) -> SOPNode:
        """
        Return the default SOPNode instance. Contains the default values that
        should be used per specification in case the actual value is not provided.
        """
        return cls(
            slope=(1.0, 1.0, 1.0),
            offset=(0.0, 0.0, 0.0),
            power=(1.0, 1.0, 1.0),
        )


@dataclass
class SatNode(XMLParsable):
    """
    Represent a *SatNode* element for a :class:`colour_clf_io.ASC_CDL`
    *Process Node*.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.SatNode.saturation`

    Methods
    -------
    -   :meth:`~colour_clf_io.SatNode.from_xml`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    saturation: float
    """
    A single decimal value applied to all color channels. Valid values for
    saturation must be greater than or equal to zero. The nominal value is 1.0.
    """

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None, config: ParserConfig
    ) -> SatNode | None:
        """
        Parse and return a :class:`colour_clf_io.SatNode` class instance from the
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
        class:`colour_clf_io.SatNode` or :py:data:`None`
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

        saturation = child_element_or_exception(xml, "Saturation", config).text
        if saturation is None:
            exception = "Saturation node in SatNode contains no value."

            raise ParsingError(exception)

        saturation = float(saturation)

        return SatNode(saturation=saturation)

    @classmethod
    def default(cls) -> SatNode:
        """
        Return the default SatNode instance. Contains the default values that
        should be used per specification in case the actual value is not provided.
        """
        return cls(saturation=1.0)


@dataclass
class Info(XMLParsable):
    """
    Represent an *Info* element.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.Info.app_release`
    -   :attr:`~colour_clf_io.Info.copyright`
    -   :attr:`~colour_clf_io.Info.revision`
    -   :attr:`~colour_clf_io.Info.aces_transform_id`
    -   :attr:`~colour_clf_io.Info.aces_user_name`
    -   :attr:`~colour_clf_io.Info.calibration_info`
    -   :attr:`~colour_clf_io.Info.saturation`

    Methods
    -------
    -   :meth:`~colour_clf_io.Info.from_xml`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processList
    """

    app_release: str | None
    """A string used for indicating application software release level."""

    copyright: str | None
    """A string containing a copyright notice for authorship of the *CLF* file."""

    revision: str | None
    """
    A string used to track the version of the LUT itself (e.g., an increased
    resolution from a previous version of the LUT).
    """

    aces_transform_id: str | None
    """
    A string containing an ACES transform identifier as described in
    Academy S-2014-002. If the transform described by the ProcessList is the
    concatenation of several ACES transforms, this element may contain several
    ACES Transform IDs, separated by white space or line separators. This
    element is mandatory for ACES transforms and may be referenced from ACES
    Metadata Files.
    """

    aces_user_name: str | None
    """
    A string containing the user-friendly name recommended for use in product
    user interfaces as described in Academy TB-2014-002.
    """

    calibration_info: CalibrationInfo | None
    """
    Container element for calibration metadata used when making a LUT for a
    specific device.
    """

    @staticmethod
    def from_xml(xml: lxml.etree._Element | None, config: ParserConfig) -> Info | None:
        """
        Parse and return a :class:`colour_clf_io.Info` class instance from the
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
        class:`colour_clf_io.Info` or :py:data:`None`
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
            child_element(xml, "CalibrationInfo", config),
            config,
        )

        return Info(calibration_info=calibration_info, **attributes)


@dataclass
class LogParams(XMLParsable):
    """
    Represent a *LogParams* element for a :class:`colour_clf_io.Log`
    *Process Node*.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.LogParams.base`
    -   :attr:`~colour_clf_io.LogParams.log_side_slope`
    -   :attr:`~colour_clf_io.LogParams.log_side_offset`
    -   :attr:`~colour_clf_io.LogParams.lin_side_slope`
    -   :attr:`~colour_clf_io.LogParams.lin_side_offset`
    -   :attr:`~colour_clf_io.LogParams.lin_side_break`
    -   :attr:`~colour_clf_io.LogParams.linear_slope`
    -   :attr:`~colour_clf_io.LogParams.channel`

    Methods
    -------
    -   :meth:`~colour_clf_io.LogParams.from_xml`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#log
    """

    base: float | None
    """The base of the logarithmic function. Default is 2."""

    log_side_slope: float | None
    """
    Slope" (or gain) applied to the log side of the logarithmic segment. Default is 1.
    """

    log_side_offset: float | None
    """
    Offset applied to the log side of the logarithmic segment. Default is 0.
    """

    lin_side_slope: float | None
    """
    Slope of the linear side of the logarithmic segment. Default is 1.
    """

    lin_side_offset: float | None
    """
    Offset applied to the linear side of the logarithmic segment. Default is 0.
    """

    lin_side_break: float | None
    """
    The break-point, defined in linear space, at which the piece-wise function
    transitions between the logarithmic and linear segments. This is required
    if style="cameraLinToLog" or "cameraLogToLin".
    """

    linear_slope: float | None
    """
    The slope of the linear segment of the piecewise function. This attribute
    does not need to be provided unless the formula being implemented requires
    it. The default is to calculate using linSideBreak such that the linear
    portion is continuous in value with the logarithmic portion of the curve,
    by using the value of the logarithmic portion of the curve at the break-point.
    """

    channel: Channel | None
    """
    The colour channel to which the exponential function is applied. Possible
    values are "R", "G", "B". If this attribute is utilized to target different
    adjustments per channel, then up to three *LogParams* elements may be used,
    provided that "channel" is set differently in each. However, the same value
    of base must be used for all channels. If this attribute is not otherwise
    specified, the logarithmic function is applied identically to all three
    colour channels.
    """

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None,
        config: ParserConfig,  # noqa: ARG004
    ) -> LogParams | None:
        """
        Parse and return a :class:`colour_clf_io.LogParams` class instance from
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
        class:`colour_clf_io.LogParams` or :py:data:`None`
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

    @classmethod
    def default(cls) -> LogParams:
        """
        Return the default LogParams instance. Contains the default values that
        should be used per specification in case the actual value is not provided.
        """
        return cls(
            base=2.0,
            log_side_slope=1.0,
            log_side_offset=0.0,
            lin_side_slope=1.0,
            lin_side_offset=0.0,
            lin_side_break=None,
            linear_slope=None,
            channel=None,
        )


@dataclass
class ExponentParams(XMLParsable):
    """
    Represent a *ExponentParams* element for a :class:`colour_clf_io.Exponent`
    *Process Node*.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.ExponentParams.exponent`
    -   :attr:`~colour_clf_io.ExponentParams.offset`
    -   :attr:`~colour_clf_io.ExponentParams.channel`

    Methods
    -------
    -   :meth:`~colour_clf_io.ExponentParams.from_xml`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#exponent
    """

    exponent: float
    """
    The power to which the value is to be raised. If style is any of the
    "monCurve" types, the valid range is [1.0, 10.0]. The nominal value is 1.0.
    """

    offset: float | None
    """
    The offset value to use. If offset is used, the enclosing Exponent
    element's style attribute must be set to one of the "monCurve" types.
    Offset is not allowed when style is any of the "basic" types. The valid
    range is [0.0, 0.9]. The nominal value is 0.0.
    """

    channel: Channel | None
    """
    The colour channel to which the exponential function is applied. Possible
    values are "R", "G", "B". If this attribute is utilized to target different
    adjustments per channel, then up to three *ExponentParams* elements may be used,
    provided that "channel" is set differently in each. However, the same value
    of base must be used for all channels. If this attribute is not otherwise
    specified, the logarithmic function is applied identically to all three
    colour channels.
    """

    @staticmethod
    def from_xml(
        xml: lxml.etree._Element | None,
        config: ParserConfig,  # noqa: ARG004
    ) -> ExponentParams | None:
        """
        Parse and return a :class:`colour_clf_io.ExponentParams` class instance
        from the given XML element. Returns `None`` if the given XML element is
        ``None``.

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
        class:`colour_clf_io.ExponentParams` or :py:data:`None`
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

    @classmethod
    def default(cls) -> ExponentParams:
        """
        Return the default ExponentParams instance. Contains the default values that
        should be used per specification in case the actual value is not provided.
        """
        return cls(
            exponent=1.0,
            offset=0.0,
            channel=None,
        )
