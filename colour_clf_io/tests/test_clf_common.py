"""
Defines helper functionality for CLF tests.
"""

import os
import tempfile

import numpy as np

import colour_clf_io.parsing
import colour_clf_io.process_list

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["snippet_to_process_list", "wrap_snippet"]


EXAMPLE_WRAPPER = """<?xml version="1.0" ?>
<ProcessList id="Example Wrapper" compCLFversion="3.0" xmlns="urn:AMPAS:CLF:v3.0">
{0}
</ProcessList>
"""


def wrap_snippet(snippet: str) -> str:
    """# noqa: D401
    Takes a string that should contain the text representation of a CLF node, and
    returns valid CLF document. Essentially the given string is pasted into the
    `ProcessList` if a CLF document.

    This is useful to quickly convert example snippets of Process Nodes into valid CLF
    documents for parsing.
    """
    return EXAMPLE_WRAPPER.format(snippet)


def snippet_to_process_list(snippet: str) -> colour_clf_io.process_list.ProcessList:
    """# noqa: D401
    Takes a string that should contain a valid body for a XML Process List and
    returns the parsed `ProcessList`.
    """
    doc = wrap_snippet(snippet)
    return colour_clf_io.parse_clf(doc)


def snippet_as_tmp_file(snippet):
    doc = wrap_snippet(snippet)
    tmp_folder = tempfile.gettempdir()
    file_name = os.path.join(tmp_folder, "colour_snippet.clf")
    with open(file_name, "w") as f:
        f.write(doc)
    return file_name


def result_as_array(result_text):
    result_parts = result_text.decode("utf-8").strip().split()
    if len(result_parts) != 3:
        raise RuntimeError(f"Invalid OCIO result: {result_text}")
    result_values = list(map(float, result_parts))
    return np.array(result_values)
