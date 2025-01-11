"""
Values
=======

Defines enums that represent allowed values in some of the fields contained in a
CLF document.
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
    "ASC_CDL_Style",
]


class BitDepth(Enum):
    """
    Represents the valid bit depth values of the CLF specification.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#processNode
    """

    i8 = "8i"
    i10 = "10i"
    i12 = "12i"
    i16 = "16i"
    f16 = "16f"
    f32 = "32f"

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
    Represents the valid values of the channel attribute in the Range element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#ranges
    """

    R = "R"
    G = "G"
    B = "B"


class Interpolation1D(Enum):
    """
    Represents the valid interpolation values of a LUT1D element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#lut1d
    """

    LINEAR = "linear"


class Interpolation3D(Enum):
    """
    Represents the valid interpolation values of a LUT3D element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#lut3d
    """

    TRILINEAR = "trilinear"
    TETRAHEDRAL = "tetrahedral"


class ASC_CDL_Style(enum.Enum):
    """
    Represents the valid values of the style attribute of an ASC_CDL element.

    References
    ----------
    -   https://docs.acescentral.com/specifications/clf/#asc_cdl
    """

    FWD = "Fwd"
    REV = "Rev"
    FWD_NO_CLAMP = "FwdNoClamp"
    REV_NO_CLAMP = "RevNoClamp"
