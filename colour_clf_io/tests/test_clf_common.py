"""
Defines helper functionality for *CLF* tests.
"""

from __future__ import annotations

import os
import tempfile

import numpy as np
import numpy.typing as npt

import colour_clf_io.parsing
import colour_clf_io.process_list

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "EXAMPLE_WRAPPER",
    "wrap_snippet",
    "snippet_to_process_list",
    "snippet_as_tmp_file",
    "result_as_array",
]


EXAMPLE_WRAPPER: str = """
<?xml version="1.0" ?>
<ProcessList id="Example Wrapper" compCLFversion="3.0" xmlns="urn:AMPAS:CLF:v3.0">
{0}
</ProcessList>
""".strip()


def wrap_snippet(snippet: str | bytes) -> str:
    """
    Take a string that should contain the text representation of a *CLF* node, and
    returns valid *CLF* file. Essentially the given string is pasted into the
    `ProcessList` if a *CLF* file.

    This is useful to quickly convert example snippets of Process Nodes into valid *CLF*
    files for parsing.

    Parameters
    ----------
    snippet
        Snippet to wrap as a *CLF* file.

    Returns
    -------
    :class:`str`
        *CLF* file.
    """

    return EXAMPLE_WRAPPER.format(snippet)


def snippet_to_process_list(
    snippet: str,
) -> colour_clf_io.process_list.ProcessList | None:
    """
    Take a string that should contain a valid body for an XML *ProcessList* and
    returns the parsed :class:`colour_clf_io.process_list.ProcessList` class
    instance.

    Parameters
    ----------
    snippet
        Snippet to parse.

    Returns
    -------
    :class:`colour_clf_io.process_list.ProcessList`
    """

    doc = wrap_snippet(snippet)

    return colour_clf_io.parse_clf(doc)


def snippet_as_tmp_file(snippet: str) -> str:
    """
    Write given snippet to a temporary file.

    Parameters
    ----------
    snippet
        Snippet to write

    Returns
    -------
    :class:`str`
        Temporary filename.
    """

    doc = wrap_snippet(snippet)
    tmp_folder = tempfile.gettempdir()
    file_name = os.path.join(tmp_folder, "colour_snippet.clf")

    with open(file_name, "w") as clf_file:
        clf_file.write(doc)

    return file_name


def result_as_array(result: bytes) -> npt.NDArray:
    """
    Decode given result and convert them to an array.

    Parameters
    ----------
    result
        Result to convert to an array.

    Returns
    -------
    :class:`np.ndarray`
        Converted result array.
    """

    result_parts = result.decode("utf-8").strip().split()
    if len(result_parts) != 3:
        exception = f"Invalid OCIO result: {result}"

        raise RuntimeError(exception)

    result_values = list(map(float, result_parts))

    return np.array(result_values)
