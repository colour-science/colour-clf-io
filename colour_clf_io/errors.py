"""
Errors
======

Defines errors that are used as part of the parsing and validation of *CLF* files.
"""

from __future__ import annotations

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "ParsingError",
    "ValidationError",
]


class ParsingError(Exception):
    """
    Indicate an error with parsing a *CLF* file.
    """


class ValidationError(Exception):
    """
    Indicate a semantic error with the data in a *CLF* file.
    """
