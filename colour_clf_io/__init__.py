"""
CLF Parsing
===========

Defines the functionality and data structures to parse *CLF* files.

The main functionality is exposed through the following two methods:
-   :func:`colour.io.clf.read_clf`: Read a file in the *CLF* format and return the
    corresponding :class: ProcessList.
-   :func:`colour.io.clf.parse_clf`: Read a string that contains a *CLF* file and
    return the corresponding :class: ProcessList.

References
----------
-   :cite:`CLFv3` : Common LUT Format (CLF) - A Common File Format for Look-Up Tables.
    Retrieved May 1st, 2024, from https://docs.acescentral.com/specifications/clf
"""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from pathlib import Path

# NOTE: Security issues in lxml should be addressed and no longer be a concern:
# https://discuss.python.org/t/status-of-defusedxml-and-recommendation-in-docs/34762/6
import lxml.etree

from .elements import (
    Array,
    CalibrationInfo,
    ExponentParams,
    ExponentStyle,
    Info,
    LogParams,
    LogStyle,
    RangeStyle,
    SatNode,
    SOPNode,
)
from .process_list import ProcessList
from .process_nodes import (
    ASC_CDL,
    LUT1D,
    LUT3D,
    Exponent,
    Log,
    Matrix,
    ProcessNode,
    Range,
)
from .values import (
    ASC_CDL_Style,
    BitDepth,
    Channel,
    Interpolation1D,
    Interpolation3D,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "Array",
    "CalibrationInfo",
    "ExponentParams",
    "ExponentStyle",
    "Info",
    "LogParams",
    "LogStyle",
    "RangeStyle",
    "SatNode",
    "SOPNode",
]
__all__ += ["ProcessList"]
__all__ += [
    "ASC_CDL",
    "LUT1D",
    "LUT3D",
    "Exponent",
    "Log",
    "Matrix",
    "ProcessNode",
    "Range",
]
__all__ += [
    "ASC_CDL_Style",
    "BitDepth",
    "Channel",
    "Interpolation1D",
    "Interpolation3D",
]

__application_name__ = "Colour - CLF IO"

__major_version__ = "0"
__minor_version__ = "1"
__change_version__ = "0"
__version__ = f"{__major_version__}.{__minor_version__}.{__change_version__}"


def read_clf(path: str | Path) -> ProcessList | None:
    """
    Read given *CLF* file and return a *ProcessList*.

    Parameters
    ----------
    path
        Path to the *CLF* file.

    Returns
    -------
    :class:`colour_clf_io.ProcessList`
        *ProcessList*.

    Raises
    ------
    :class:`colour_clf_io.errors.ParsingError`
        If the given file does not contain a valid *CLF* file.
    """

    xml = lxml.etree.parse(str(path))  # noqa: S320
    xml_process_list = xml.getroot()

    return ProcessList.from_xml(xml_process_list)


def parse_clf(text: str | bytes) -> ProcessList | None:
    """
    Read given string as a *CLF* file and return a *ProcessList*.

    Parameters
    ----------
    text
        String that contains the *CLF* file.

    Returns
    -------
    :class:`colour_clf_io.ProcessList`
        *ProcessList*.

    Raises
    ------
    :class:`colour_clf_io.errors.ParsingError`
        If the given string does not contain a valid *CLF* file.
    """

    xml = lxml.etree.fromstring(text)  # noqa: S320

    return ProcessList.from_xml(xml)
