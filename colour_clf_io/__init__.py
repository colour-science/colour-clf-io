"""
CLF Parsing
===========

Defines the functionality and data structures to parse CLF documents.

The main functionality is exposed through the following two methods:
-   :func:`colour.io.clf.read_clf`: Read a file in the CLF format and return the
    corresponding :class: ProcessList.
-   :func:`colour.io.clf.parse_clf`: Read a string that contains a CLF document and
    return the corresponding :class: ProcessList.

References
----------
-   :cite:`CLFv3` : Common LUT Format (CLF) - A Common File Format for Look-Up Tables.
    Retrieved May 1st, 2024, from https://docs.acescentral.com/specifications/clf
"""

from __future__ import annotations

__application_name__ = "Colour - CLF IO"

__major_version__ = "0"
__minor_version__ = "0"
__change_version__ = "0"
__version__ = ".".join((__major_version__, __minor_version__, __change_version__))


# Security issues in lxml should be addressed and no longer be a concern:
# https://discuss.python.org/t/status-of-defusedxml-and-recommendation-in-docs/34762/6

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["read_clf", "parse_clf"]

import lxml.etree

from colour_clf_io.process_list import ProcessList


def read_clf(path) -> ProcessList:
    """
    Read given *CLF* file and return the resulting `ProcessList`.

    Parameters
    ----------
    path
        Path to the *CLF* file.

    Returns
    -------
    :class: colour.clf.ProcessList

    Raises
    ------
    :class: ParsingError
        If the given file does not contain a valid CLF document.

    """
    xml = lxml.etree.parse(path)  # noqa: S320
    xml_process_list = xml.getroot()
    root = ProcessList.from_xml(xml_process_list)
    return root


def parse_clf(text):
    """
    Read given string as a *CLF* document and return the resulting `ProcessList`.

    Parameters
    ----------
    text
        String that contains the *CLF* document.

    Returns
    -------
    :class: colour.clf.ProcessList.

    Raises
    ------
    :class: ParsingError
        If the given string does not contain a valid CLF document.

    """
    xml = lxml.etree.fromstring(text)  # noqa: S320
    root = ProcessList.from_xml(xml)
    return root
