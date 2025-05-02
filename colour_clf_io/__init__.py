"""
Colour - CLF IO
===============

Defines the functionality and data structures to parse *CLF* files.

The main functionality is exposed through the following two methods:
-   :func:`colour.io.clf.read_clf_from_file`: Read a file in the *CLF* format and
    return the corresponding :class: ProcessList.
-   :func:`colour.io.clf.read_clf`: Read a string that contains a *CLF* file and
    return the corresponding :class: ProcessList.
-   :func:`colour.io.clf.write_clf`: Take a :class: ProcessList and output the
    corresponding CLF document.

References
----------
-   :cite:`CLFv3` : Common LUT Format (CLF) - A Common File Format for Look-Up Tables.
    Retrieved May 1st, 2024, from https://docs.acescentral.com/specifications/clf
"""

from __future__ import annotations

import typing

from .parsing import Namespaces

if typing.TYPE_CHECKING:
    from pathlib import Path

# NOTE: Security issues in lxml should be addressed and no longer be a concern:
# https://discuss.python.org/t/status-of-defusedxml-and-recommendation-in-docs/34762/6
import lxml.etree

from .elements import (
    Array,
    CalibrationInfo,
    ExponentParams,
    Info,
    LogParams,
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
    ASC_CDLStyle,
    BitDepth,
    Channel,
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
    "Array",
    "CalibrationInfo",
    "SOPNode",
    "SatNode",
    "Info",
    "LogParams",
    "ExponentParams",
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
    "BitDepth",
    "Channel",
    "Interpolation1D",
    "Interpolation3D",
    "RangeStyle",
    "LogStyle",
    "ExponentStyle",
    "ASC_CDLStyle",
]

__application_name__ = "Colour - CLF IO"

__major_version__ = "0"
__minor_version__ = "2"
__change_version__ = "0"
__version__ = f"{__major_version__}.{__minor_version__}.{__change_version__}"

try:
    from colour_clf_io.processing import CLFProcessList

    __all__ += ["CLFProcessList"]
except ImportError:
    pass


def read_clf_from_file(path: str | Path) -> ProcessList:
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

    xml = lxml.etree.parse(str(path))
    xml_process_list = xml.getroot()

    process_list = ProcessList.from_xml(xml_process_list)
    if process_list is None:
        err = "Process list could not be parsed."
        raise ValueError(err)
    return process_list


def read_clf(text: str | bytes) -> ProcessList | None:
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

    xml = lxml.etree.fromstring(text)

    return ProcessList.from_xml(xml)


def write_clf(
    process_list: ProcessList,
    path: str | Path | None = None,
    namespace: Namespaces = Namespaces.AMPAS,
) -> None | str:
    """
    Write the given *ProcessList* as a CLF file to the target
    location. If no *path* is given the CLF document will be returned as a string.

    Parameters
    ----------
    process_list
        *ProcessList* that should be written.
    path
        Location of the file, or *None* to return a string representation of the
        CLF document.
    namespace
        :class:`colour_clf_io.Namespaces` instance to be used for the namespace
        of the document.

    Returns
    -------
    :class:`colour_clf_io.ProcessList`
    """
    xml = process_list.to_xml(namespace)
    serialised = lxml.etree.tostring(xml)
    if path is None:
        return serialised.decode("utf-8")
    with open(path, "wb") as f:
        f.write(serialised)
    return None
