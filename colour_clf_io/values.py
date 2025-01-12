"""
Values
=======

Defines the enumerations that represent allowed values in some of the
fields contained in a *CLF* file.
"""

from __future__ import annotations

import enum
from enum import Enum

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "BitDepth",
    "Channel",
    "Interpolation1D",
    "Interpolation3D",
    "RangeStyle",
    "LogStyle",
    "ExponentStyle",
    "ASC_CDLStyle",
]


class BitDepth(Enum):
    """
    Represents the valid bit depth values of the *CLF* specification.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.BitDepth.i8`
    -   :attr:`~colour_clf_io.BitDepth.i10`
    -   :attr:`~colour_clf_io.BitDepth.i12`
    -   :attr:`~colour_clf_io.BitDepth.i16`
    -   :attr:`~colour_clf_io.BitDepth.f16`
    -   :attr:`~colour_clf_io.BitDepth.f32`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processNode
    """

    i8 = "8i"
    """8-bit unsigned integer."""

    i10 = "10i"
    """10-bit unsigned integer."""

    i12 = "12i"
    """12-bit unsigned integer."""

    i16 = "16i"
    """16-bit unsigned integer."""

    f16 = "16f"
    """16-bit floating point (half-float)."""

    f32 = "32f"
    """32-bit floating point (single precision)."""

    def scale_factor(self) -> float:
        """
        Return the scale factor that is needed to normalise a value of the given
        bit depth to the range 0..1.

        Examples
        --------
        >>> from colour_clf_io.values import BitDepth
        >>> 255 / BitDepth.i8.scale_factor() == 1.0
        True
        >>> 0.5 * BitDepth.i8.scale_factor()
        127.5
        >>> 1023 / BitDepth.i10.scale_factor() == 1.0
        True
        >>> 1.0 / BitDepth.f16.scale_factor() == 1.0
        True
        """

        if self == BitDepth.i8:
            return 2**8 - 1

        if self == BitDepth.i10:
            return 2**10 - 1

        if self == BitDepth.i12:
            return 2**12 - 1

        if self == BitDepth.i16:
            return 2**16 - 1

        if self in [BitDepth.f16, BitDepth.f32]:
            return 1.0

        raise NotImplementedError

    @classmethod
    def all(cls: type[BitDepth]) -> list:
        """
        Return a list of all valid bit depth values.

        Examples
        --------
        >>> from colour_clf_io.values import BitDepth
        >>> BitDepth.all()
        ['8i', '10i', '12i', '16i', '16f', '32f']
        """

        return [e.value for e in cls]


class Channel(enum.Enum):
    """
    Represents the valid values of the channel attribute in the *Range* element.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.Channel.R`
    -   :attr:`~colour_clf_io.Channel.G`
    -   :attr:`~colour_clf_io.Channel.B`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#ranges
    """

    R = "R"
    G = "G"
    B = "B"


class Interpolation1D(Enum):
    """
    Represents the valid interpolation values of a *LUT1D* element.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.Interpolation1D.LINEAR`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#lut1d
    """

    LINEAR = "linear"


class Interpolation3D(Enum):
    """
    Represents the valid interpolation values of a *LUT3D* element.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.Interpolation3D.TRILINEAR`
    -   :attr:`~colour_clf_io.Interpolation3D.TETRAHEDRAL`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#lut3d
    """

    TRILINEAR = "trilinear"
    TETRAHEDRAL = "tetrahedral"


class RangeStyle(enum.Enum):
    """
    Represent the valid values of the *style* attribute of a
    :class:`colour_clf_io.Range` *Process Node*.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.RangeStyle.CLAMP`
    -   :attr:`~colour_clf_io.RangeStyle.NO_CLAMP`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#range
    """

    CLAMP = "Clamp"
    """
    Clamping is applied upon the result of the scale and offset expressed by
    the result of the non-clamping Range equation."""

    NO_CLAMP = "noClamp"
    """
    Scale and offset is applied without clamping (i.e., values below
    minOutValue or above maxOutValue are preserved).
    """


class LogStyle(enum.Enum):
    """
    Represent the valid values of the *style* attribute of a
    :class:`colour_clf_io.Log` *Process Node*.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.LogStyle.LOG_10`
    -   :attr:`~colour_clf_io.LogStyle.ANTI_LOG_10`
    -   :attr:`~colour_clf_io.LogStyle.LOG_2`
    -   :attr:`~colour_clf_io.LogStyle.ANTI_LOG_2`
    -   :attr:`~colour_clf_io.LogStyle.LIN_TO_LOG`
    -   :attr:`~colour_clf_io.LogStyle.LOG_TO_LIN`
    -   :attr:`~colour_clf_io.LogStyle.CAMERA_LIN_TO_LOG`
    -   :attr:`~colour_clf_io.LogStyle.CAMERA_LOG_TO_LIN`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processList
    """

    LOG_10 = "log10"
    """Apply a base 10 logarithm."""

    ANTI_LOG_10 = "antiLog10"
    """Apply a base 10 anti-logarithm."""

    LOG_2 = "log2"
    """Apply a base 2 logarithm."""

    ANTI_LOG_2 = "antiLog2"
    """Apply a base 2 anti-logarithm."""

    LIN_TO_LOG = "linToLog"
    """Apply a logarithm."""

    LOG_TO_LIN = "logToLin"
    """Apply an anti-logarithm."""

    CAMERA_LIN_TO_LOG = "cameraLinToLog"
    """
    Apply a piecewise function with logarithmic and linear segments on linear
    values, converting them to non-linear values.
    """

    CAMERA_LOG_TO_LIN = "cameraLogToLin"
    """
    Applies a piecewise function with logarithmic and linear segments on
    non-linear values, converting them to linear values.
    """


class ExponentStyle(enum.Enum):
    """
    Represent the valid values of the *style* attribute of a
    :class:`colour_clf_io.Exponent` *Process Node*.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.ExponentStyle.BASIC_FWD`
    -   :attr:`~colour_clf_io.ExponentStyle.BASIC_REV`
    -   :attr:`~colour_clf_io.ExponentStyle.BASIC_MIRROR_FWD`
    -   :attr:`~colour_clf_io.ExponentStyle.BASIC_MIRROR_REV`
    -   :attr:`~colour_clf_io.ExponentStyle.BASIC_PASS_THRU_FWD`
    -   :attr:`~colour_clf_io.ExponentStyle.BASIC_PASS_THRU_REV`
    -   :attr:`~colour_clf_io.ExponentStyle.MON_CURVE_FWD`
    -   :attr:`~colour_clf_io.ExponentStyle.MON_CURVE_REV`
    -   :attr:`~colour_clf_io.ExponentStyle.MON_CURVE_MIRROR_FWD`
    -   :attr:`~colour_clf_io.ExponentStyle.MON_CURVE_MIRROR_REV`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#exponent
    """

    BASIC_FWD = "basicFwd"
    """
    Apply a power law using the exponent value specified in the ExponentParams
    element.
    """

    BASIC_REV = "basicRev"
    """
    Apply a power law using the exponent value specified in the ExponentParams
    element.
    """

    BASIC_MIRROR_FWD = "basicMirrorFwd"
    """
    Apply a basic power law using the exponent value specified in the
    ExponentParams element for values greater than or equal to zero and mirror
    the function for values less than zero (i.e., rotationally symmetric around
    the origin).
    """

    BASIC_MIRROR_REV = "basicMirrorRev"
    """
    Apply a basic power law using the exponent value specified in the
    ExponentParams element for values greater than or equal to zero and mirror
    the function for values less than zero (i.e., rotationally symmetric around
    the origin).
    """

    BASIC_PASS_THRU_FWD = "basicPassThruFwd"  # noqa: S105
    """
    Apply a basic power law using the exponent value specified in the
    ExponentParams element for values greater than or equal to zero and passes
    values less than zero unchanged.
    """

    BASIC_PASS_THRU_REV = "basicPassThruRev"  # noqa: S105
    """
    Apply a basic power law using the exponent value specified in the
    ExponentParams element for values greater than or equal to zero and passes
    values less than zero unchanged.
    """

    MON_CURVE_FWD = "monCurveFwd"
    """
    Apply a power law function with a linear segment near the origin.
    """

    MON_CURVE_REV = "monCurveRev"
    """
    Apply a power law function with a linear segment near the origin.
    """

    MON_CURVE_MIRROR_FWD = "monCurveMirrorFwd"
    """
    Apply a power law function with a linear segment near the origin and
    mirror the function for values less than zero (i.e., rotationally symmetric
    around the origin).
    """

    MON_CURVE_MIRROR_REV = "monCurveMirrorRev"
    """
    Apply a power law function with a linear segment near the origin and mirror
    the function for values less than zero (i.e., rotationally symmetric around
    the origin).
    """


class ASC_CDLStyle(enum.Enum):
    """
    Represents the valid values of the style attribute of an ASC_CDL element.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.ASC_CDLStyle.FWD`
    -   :attr:`~colour_clf_io.ASC_CDLStyle.REV`
    -   :attr:`~colour_clf_io.ASC_CDLStyle.FWD_NO_CLAMP`
    -   :attr:`~colour_clf_io.ASC_CDLStyle.REV_NO_CLAMP`

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    FWD = "Fwd"
    """Implementation of v1.2 ASC CDL equation (default)."""

    REV = "Rev"
    """Inverse equation."""

    FWD_NO_CLAMP = "FwdNoClamp"
    """Similar to the Fwd equation, but without clamping."""

    REV_NO_CLAMP = "RevNoClamp"
    """Inverse equation, without clamping."""
