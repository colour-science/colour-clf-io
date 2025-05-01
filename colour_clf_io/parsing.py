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
from enum import Enum
from itertools import islice
from typing import TypeGuard, TypeVar

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any

import lxml.etree

from colour_clf_io.errors import ParsingError

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "Namespaces",
    "ParserConfig",
    "XMLParsable",
    "XMLWritable",
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
    "detect_namespace",
]


class Namespaces(Enum):
    """
    Valid namespaces for parsing and serialising CLF documents.
    """

    AMPAS = "urn:AMPAS:CLF:v3.0"
    SMTP = "http://www.smpte-ra.org/ns/2136-1/2024"


@dataclass
class UnknownNamespace:
    namespace: str


@dataclass
class ParserConfig:
    """
    Additional settings for parsing the *CLF* file.

    Attributes
    ----------
    -   :attr:`~colour_clf_io.ParserConfig.name_space`

    Methods
    -------
    -   :meth:`~colour_clf_io.ParserConfig.clf_namespace_prefix_mapping`
    """

    namespace: Namespaces | None
    """
    The namespace name used for parsing the *CLF* file.
    """

    def clf_namespace_prefix_mapping(self) -> dict[str, str] | None:
        """
        Return the namespaces prefix mapping used for *CLF* files.

        Returns
        -------
        :class:`dict[str, str]` or :py:data:`None`
            Dictionary that contain the namespaces prefix mappings.
        """

        if self.namespace:
            return {"clf": self.namespace.value}

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


class XMLWritable(ABC):
    """
    Define the base class for objects that can be serialised to XML.

    This is an :class:`ABCMeta` abstract class that must be inherited by
    sub-classes.

    Methods
    -------
    -   :meth:`~colour_lf_io.parsing.XMLParsable.to_xml`
    """

    @abstractmethod
    def to_xml(self) -> lxml.etree._Element:
        """
        Serialise this object as an XML object.

        Returns
        -------
        :class:`lxml.etree._Element`
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
    xml: lxml.etree._Element, name: str, config: ParserConfig
) -> lxml.etree._Element | None:
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

    Returns
    -------
    :class:`xml.etree.ElementTree.Element` or :class`str` or :py:data:`None`
        The found child element, or the result of the applied XPath function.
        :py:data:`None` if the child was not found.
    """

    elements = child_elements(xml, name, config)
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
    xml: lxml.etree._Element, name: str, config: ParserConfig
) -> list[lxml.etree._Element]:
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

    Returns
    -------
    :class:`xml.etree.ElementTree.Element` or :class`str`
        The found child element, or the result of the applied XPath function.
        :py:data:`None` if the child was not found.
    """

    if config.clf_namespace_prefix_mapping():
        elements = xml.xpath(
            f"clf:{name}",
            namespaces=config.clf_namespace_prefix_mapping(),
        )
    else:
        elements = xml.xpath(f"{name}")

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

    Raises
    ------
    :class:`colour_clf_io.errors.ParsingError` if the child element is not found.

    Returns
    -------
    :class:`xml.etree.ElementTree.Element`
        The found child element.
    """

    element = child_element(xml, name, config)
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

    element = child_element(xml, name, config)

    if element is None:
        return ""

    return str(element.text)


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

    text = element_as_text(xml, name, config)
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

    elements = child_elements(xml, name, config)
    return [element.text for element in elements if element.text is not None]


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
    exception = f"Failed to parse three float values from {text}"

    if text is None:
        raise ParsingError(exception)

    parts = text.split()

    if len(parts) != 3:
        raise ParsingError(exception)
    values = tuple(map(float, parts))
    # Note: Repacking here to satisfy type check.
    return values[0], values[1], values[2]


def set_attr_if_not_none(node: lxml.etree._Element, attr: str, value: Any) -> None:
    if value is not None:
        node.set(attr, str(value))


def set_element_if_not_none(node: lxml.etree._Element, name: str, value: Any) -> None:
    if value is not None and value != "":
        child = lxml.etree.SubElement(node, name)
        child.text = str(value)


def detect_namespace(node: lxml.etree._Element) -> Namespaces | UnknownNamespace | None:
    """
    Detect the namespace of the given CLF document.

    Parameters
    ----------
    node
        XML element to check for namespace.

    Returns
    -------
    :class:`NameSpace` or :class:`UnknownNamespace` or None depending on whether a valid
    namespace was detected, an invalid namespace was detected, or no namespace is
    present.
    """
    document_namespace = node.xpath("namespace-uri(.)")
    if not document_namespace:
        return None
    document_namespace = str(document_namespace)
    match document_namespace:
        case Namespaces.SMTP.value:
            return Namespaces.SMTP
        case Namespaces.AMPAS.value:
            return Namespaces.AMPAS
    return UnknownNamespace(document_namespace)
