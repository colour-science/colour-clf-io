"""
Parsing
=======

Defines utilities that are used to parse *CLF* files.
"""

from __future__ import annotations

import collections
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import islice
from typing import TypeGuard, TypeVar

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any

if typing.TYPE_CHECKING:
    import lxml.etree

from colour_clf_io.errors import ParsingError

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "NAMESPACE_NAME",
    "ParserConfig",
    "XMLParsable",
    "map_optional",
    "retrieve_attributes",
    "retrieve_attributes_as_float",
    "check_none",
    "child_element",
    "child_elements",
    "child_element_or_exception",
    "element_as_text",
    "element_as_float",
    "elements_as_text_list",
    "sliding_window",
    "three_floats",
]

NAMESPACE_NAME: str = "urn:AMPAS:CLF:v3.0"


@dataclass
class ParserConfig:
    """
    Additional settings for parsing the *CLF* file.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.ParserConfig.namespace_name`

    Methods
    -------
    -   :meth:`~colour_clf_io.ParserConfig.clf_namespace_prefix_mapping`
    """

    namespace_name: str | None = NAMESPACE_NAME
    """
    The namespace name used for parsing the *CLF* file. Usually this should
    be the `CLF_NAMESPACE`, but it can be omitted."""

    def clf_namespace_prefix_mapping(self) -> dict[str, str] | None:
        """
        Return the namespaces prefix mapping used for *CLF* files.

        Returns
        -------
        :class:`dict[str, str]` or :py:data:`None`
            Dictionary that contain the namespaces prefix mappings.
        """

        if self.namespace_name:
            return {"clf": self.namespace_name}

        return None


class XMLParsable(ABC):
    """
    Define the base class for objects that can be generated from XML files.

    This is an :class:`ABCMeta` abstract class that must be inherited by
    sub-classes.

    Methods
    -------
    -   :meth:`~colour_lf_io.parsing.XMLParsable.from_xml`
    """

    @staticmethod
    @abstractmethod
    def from_xml(
        xml: lxml.etree._Element | None, config: ParserConfig
    ) -> XMLParsable | None:
        """
        Parse an object of this class from the given XML object.

        Parameters
        ----------
        xml
            XML file to read.
        config
            Additional settings for parsing the file.

        Returns
        -------
        :class:`colour_clf_io.parsing.XMLParsable` or :py:data:`None`
            Parsed object or ``None`` if parsing failed.
        """


def map_optional(function: Callable, value: Any | None) -> Any:
    """
    Apply the given function to given ``value`` if ``value`` is not ``None``.

    Parameters
    ----------
    function
        The function to apply.
    value
        The value to apply the function onto.

    Returns
    -------
    :class:`object` or :py:data:`None`
        The result of applying ``function`` to ``value``.
    """

    if value is not None:
        return function(value)

    return None


def retrieve_attributes(
    xml: lxml.etree._Element, attribute_mapping: dict[str, str]
) -> dict[str, str | None]:
    """
    Take a dictionary of keys and attribute names and map the attribute names
    to the corresponding values from the given XML element. Note that the keys
    of the attribute mapping are not used in any way.

    Parameters
    ----------
    xml
        the XML element to retrieve attributes from.
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
    xml: lxml.etree._Element, attribute_mapping: dict[str, str]
) -> dict[str, float | None]:
    """
    Take a dictionary of keys and attribute names and map the attribute names to the
    corresponding values from the given XML element. Also converts all values to
    :class:`float` values, or :py:data:`None`.

    Note that the keys of the attribute mapping are not used in any way.

    Parameters
    ----------
    xml
        the XML element to retrieve attributes from.
    attribute_mapping
        The dictionary containing keys and attribute names.

    Returns
    -------
    :class:`dict[str, float | None]`
        The resulting dictionary of keys and attribute values.
    """

    attributes = retrieve_attributes(xml, attribute_mapping)

    def as_float(value: Any) -> float | None:
        """Convert given value to float."""

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    return {key: as_float(value) for key, value in attributes.items()}


T = TypeVar("T")


def check_none(value: T | None, message: str) -> TypeGuard[T]:
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
    :class:`colour_clf_io.errors.ParsingError` if `value` is :py:data:`None`.

    Returns
    -------
    :class:`TypeGuard`
    """

    if value is None:
        raise ParsingError(message)

    return True


def child_element(
    xml: lxml.etree._Element, name: str, config: ParserConfig, xpath_function: str = ""
) -> lxml.etree._Element | str | None:
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

    elements = child_elements(xml, name, config, xpath_function)
    element_count = len(elements)

    if element_count == 0:
        return None

    if element_count == 1:
        return elements[0]

    exception = (
        f"Found multiple elements of type {name} in "
        f"element {xml}, but only expected exactly one."
    )

    raise ParsingError(exception)


def child_elements(
    xml: lxml.etree._Element, name: str, config: ParserConfig, xpath_function: str = ""
) -> list[lxml.etree._Element] | list[str]:
    """
    Return all child elements with a given name of an XML element.

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
    :class:`xml.etree.ElementTree.Element` or :class`str`
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

    return elements  # pyright: ignore


def child_element_or_exception(
    xml: lxml.etree._Element, name: str, config: ParserConfig
) -> lxml.etree._Element:
    """
    Return a named child element of the given XML element, or raise an exception
    if no such child element is found.

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
    :class:`colour_clf_io.errors.ParsingError` if the child element is not found.

    Returns
    -------
    :class:`xml.etree.ElementTree.Element`
        The found child element.
    """

    element = child_element(xml, name, config)

    if isinstance(element, str):
        exception = f'Element "{element}" cannot be a string!'

        raise TypeError(exception)

    if element is None:
        exception = (
            f"Tried to retrieve child element '{name}' from '{xml}' but child was "
            "not present."
        )

        raise ParsingError(exception)

    return element


def element_as_text(xml: lxml.etree._Element, name: str, config: ParserConfig) -> str:
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
        The text value of the child element. If the child element is not present
        an empty string is returned.
    """

    text = child_element(xml, name, config, xpath_function="/text()")

    if text is None:
        return ""

    return str(text)


def element_as_float(
    xml: lxml.etree._Element, name: str, config: ParserConfig
) -> float | None:
    """
    Convert a named child of the given XML element to its float value.

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
    :class:`float` or :py:data:`None`
        The value of the child element as float. If the child element is not or
        an invalid float representation, ``None`` is returned.
    """

    text = child_element(xml, name, config, xpath_function="/text()")

    if text is None:
        return None

    try:
        return float(str(text))
    except ValueError:
        return None


def elements_as_text_list(
    xml: lxml.etree._Element, name: str, config: ParserConfig
) -> list[str]:
    """
    Return one or more child elements of the given XML element as a list of
    strings.

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
        A list of string, where each string corresponds to the text
        representation of a child element.
    """

    if config.clf_namespace_prefix_mapping():
        return xml.xpath(  # pyright: ignore
            f"clf:{name}/text()", namespaces=config.clf_namespace_prefix_mapping()
        )

    return xml.xpath(f"{name}/text()")  # pyright: ignore


def sliding_window(iterable: Iterable, n: int) -> Iterable:
    """
    Collect data into overlapping fixed-length chunks or blocks.

    Parameters
    ----------
    iterable
        Iterable to collect the data from
    n
        Chunk size

    Returns
    -------
    Generator
        Chunk generator.

    References
    ----------
    -   https://docs.python.org/3/library/itertools.html
    """

    it = iter(iterable)
    window = collections.deque(islice(it, n - 1), maxlen=n)
    for x in it:
        window.append(x)
        yield tuple(window)


def three_floats(text: str | None) -> tuple[float, float, float]:
    """
    Parse the given text as a comma separated list of floating point values.

    Parameters
    ----------
    text
        String to parse.

    Raises
    ------
    :class:`colour_clf_io.errors.ParsingError`
        If `text` is :py:data:`None`, or cannot be parsed as three floats.

    Returns
    -------
    :class:`tuple` of :class:`float`
        Three floating point values.
    """

    if text is None:
        exception = f"Failed to parse three float values from {text}"

        raise ParsingError(exception)

    parts = text.split()

    if len(parts) != 3:
        exception = f"Failed to parse three float values from {text}"

        raise ParsingError(exception)

    return float(parts[0]), float(parts[1]), float(parts[2])
