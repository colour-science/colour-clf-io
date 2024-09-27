"""
Parsing
=======

Defines utilities that are used to parse CLF documents.

"""

from __future__ import annotations

import collections
import xml.etree
import xml.etree.ElementTree
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import islice
from typing import Callable, TypeVar

from typing_extensions import Self, TypeGuard

from colour_clf_io.errors import ParsingError

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__ALL__ = [
    "ParserConfig",
    "XMLParsable",
    "fully_qualified_name",
    "map_optional",
    "retrieve_attributes",
    "retrieve_attributes_as_float",
    "must_have",
    "child_element",
    "child_element_or_exception",
    "element_as_text",
    "elements_as_text_list",
    "sliding_window",
    "three_floats",
]

_T = TypeVar("_T")

NAMESPACE_NAME = "urn:AMPAS:CLF:v3.0"


@dataclass
class ParserConfig:
    """Additional settings for parsing the CLF document.

    Parameters
    ----------
    namespace_name
        The namespace name used for parsing the CLF document. Usually this should be
        the `CLF_NAMESPACE`, but it can be omitted.
    """

    namespace_name: str | None = NAMESPACE_NAME

    def clf_namespace_prefix_mapping(self) -> dict[str, str] | None:
        """Return the namespaces prefix mapping used for CLF documents.

        Returns
        -------
        :class:`dict[str, str]` that contains the namespaces prefix mappings.

        """
        if self.namespace_name:
            return {"clf": self.namespace_name}
        else:
            return None


class XMLParsable(ABC):
    """
    Define the base class for objects that can be generated from XML documents.

    This is an :class:`ABCMeta` abstract class that must be inherited by
    sub-classes.

    Methods
    -------
    -   :meth:`~colour_lf_io.parsing.XMLParsable.from_xml`
    """

    @classmethod
    @abstractmethod
    def from_xml(cls, xml, config: ParserConfig) -> Self | None:
        """
        Parse an object of this class from the given XML object.

        Parameters
        ----------
        xml
            XML document to read.
        config
            Additional settings for parsing the document.

        Returns
        -------
        An instance of the parsed object, or :py:data:`None` if parsing failed.

        """


def map_optional(f: Callable, value):
    """
    Apply `f` to value, if `value` is not :py:data:`None`.

    Parameters
    ----------
    f
        The function to apply.
    value
        The value (that might be :py:data:`None`)

    Returns
    -------
    The result of applying `f` to `value`, or :py:data:`None`.

    """
    if value is not None:
        return f(value)
    return None


def retrieve_attributes(
    xml, attribute_mapping: dict[str, str]
) -> dict[str, str | None]:
    """
    Take a dictionary of keys and attribute names and map the attribute names to the
    corresponding values from the given XML element. Note that the keys of the
    attribute mapping are not used in any way.

    Parameters
    ----------
    xml
        The XML element to retrieve attributes from.
    attribute_mapping
        The dictionary containing keys and attribute names.

    Returns
    -------
    :class:`dict[str, str | None]`
        The resulting dictionary of keys and attribute values.

    """
    return {
        k: xml.get(attribute_name) for k, attribute_name in attribute_mapping.items()
    }


def retrieve_attributes_as_float(
    xml, attribute_mapping: dict[str, str]
) -> dict[str, float | None]:
    """
    Take a dictionary of keys and attribute names and map the attribute names to the
    corresponding values from the given XML element. Also converts all values to
    :class:`float` values, or :py:data:`None`.

    Note that the keys of the attribute mapping are not used in any way.

    Parameters
    ----------
    xml
        The XML element to retrieve attributes from.
    attribute_mapping
        The dictionary containing keys and attribute names.

    Returns
    -------
    :class:`dict[str, float | None]`
        The resulting dictionary of keys and attribute values.

    """
    attributes = retrieve_attributes(xml, attribute_mapping)

    def as_float(value):
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    return {key: as_float(value) for key, value in attributes.items()}


def must_have(value: _T | None, message) -> TypeGuard[_T]:
    """
    Assert that `value` is not :py:data:`None`.

    Parameters
    ----------
    value
        Value to check.
    message
        Error message to raise.

    Raises
    ------
    :class:`ParsingError` if `value` is :py:data:`None`.

    Returns
    -------
    :class:`TypeGuard`

    """
    if value is None:
        raise ParsingError(message)
    return True


def child_element(
    xml, name, config: ParserConfig, xpath_function=""
) -> xml.etree.ElementTree.Element | None | str:
    """
    Return a named child element of the given XML element.

    Parameters
    ----------
    xml
        XML element to operate on.
    name
        Name of the child element to look for.
    config
        Additional parser configuration.
    xpath_function
        Optional XPath function to evaluate on the child element.

    Returns
    -------
    :class:`xml.etree.ElementTree.Element` or :class`str` or :py:data:`None`
        The found child element, or the result of the applied XPath function.
        :py:data:`None` if the child was not found.

    """

    if config.clf_namespace_prefix_mapping():
        elements = xml.xpath(
            f"clf:{name}{xpath_function}",
            namespaces=config.clf_namespace_prefix_mapping(),
        )
    else:
        elements = xml.xpath(f"{name}{xpath_function}")
    element_count = len(elements)
    if element_count == 0:
        return None
    elif element_count == 1:
        return elements[0]
    else:
        raise ParsingError(
            f"Found multiple elements of type {name} in "
            f"element {xml}, but only expected exactly one."
        )


def child_element_or_exception(
    xml, name, config: ParserConfig
) -> xml.etree.ElementTree.Element:
    """
    Return a named child element of the given XML element, or raise an exception if no
    such child element is found.

    Parameters
    ----------
    xml
        XML element to operate on.
    name
        Name of the child element to look for.
    config
        Additional parser configuration.
    xpath_function
        Optional XPath function to evaluate on the child element.

    Raises
    ------
    :class:`ParsingError` if the child element is not found.

    Returns
    -------
    :class:`xml.etree.ElementTree.Element`
        The found child element.
    """
    element = child_element(xml, name, config)
    assert not isinstance(element, str)  # noqa: S101
    if element is None:
        raise ParsingError(
            f"Tried to retrieve child element '{name}' from '{xml}' but child was "
            "not present."
        )
    return element


def element_as_text(xml, name, config: ParserConfig) -> str:
    """
    Convert a named child of the given XML element to its text value.

    Parameters
    ----------
    xml
        XML element to operate on.
    name
        Name of the child element to look for.
    config
        Additional parser configuration.

    Returns
    -------
    :class:`str`
        The text value of the child element. If the child element is not present and
        empty string is returned.

    """
    text = child_element(xml, name, config, xpath_function="/text()")
    if text is None:
        return ""
    else:
        return str(text)


def elements_as_text_list(xml, name, config: ParserConfig):
    """
    Return one or more child elements of the given XML element as a list of strings.

    Parameters
    ----------
    xml
        XML element to operate on.
    name
        Name of the child elements to look for.
    config
        Additional parser configuration.

    Returns
    -------
    :class:`list` of :class:`str`
        A list of string, where each string corresponds to the text representation of
        a child element.

    """
    if config.clf_namespace_prefix_mapping():
        return xml.xpath(
            f"clf:{name}/text()", namespaces=config.clf_namespace_prefix_mapping()
        )
    else:
        return xml.xpath(f"{name}/text()")


def sliding_window(iterable, n):
    """
    Collect data into overlapping fixed-length chunks or blocks.
    Source: https://docs.python.org/3/library/itertools.html
    """
    it = iter(iterable)
    window = collections.deque(islice(it, n - 1), maxlen=n)
    for x in it:
        window.append(x)
        yield tuple(window)


def three_floats(s: str | None) -> tuple[float, float, float]:
    """
    Parse the given value as a comma separated list of floating point values.

    Parameters
    ----------
    s
        String to parse.

    Raises
    ------
    :class:`ParsingError`
        If `s` is :py:data:`None`, or cannot be parsed as three floats.

    Returns
    -------
    :class:`tuple` of :class:`float`
        Three floating point values.

    """
    if s is None:
        raise ParsingError(f"Failed to parse three float values from {s}")
    parts = s.split()
    if len(parts) != 3:
        raise ParsingError(f"Failed to parse three float values from {s}")
    values = tuple(map(float, parts))
    # Repacking here to satisfy type check.
    return values[0], values[1], values[2]
