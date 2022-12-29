"""Parse a docstring to retrieve the sections and sub-sections."""

import contextlib
import itertools
import re
from typing import NamedTuple, Iterator, Iterable


class _Section(NamedTuple):
    """Represents a docstring section.

    Attrs:
        name: Short description of the section.
        subs: The names of the sub-sections included in the section. None if the section has no
            sub-sections.
    """

    name: str
    subs: tuple[()] | tuple[str, ...]


class Docstring(NamedTuple):
    """Represents a docstring.

    Attrs:
        args: The arguments described in the docstring. None if the docstring doesn't have the args
            section.
        attrs: The attributes described in the docstring. None if the docstring doesn't have the
            attrs section.
        returns: Whether the docstring has the returns section.
        yields: Whether the docstring has the yields section.
        raises: The exceptions described in the docstring. None if the docstring doesn't have the
            raises section.
    """

    args: tuple[()] | tuple[str, ...] | None
    attrs: tuple[()] | tuple[str, ...] | None
    returns: bool
    yields: bool
    raises: tuple[()] | tuple[str] | None


_SECTION_NAMES = {
    "args": ("args", "arguments", "parameters"),
    "attrs": ("attributes", "attrs"),
    "returns": ("return", "returns"),
    "yields": ("yield", "yields"),
    "raises": ("raises",),
}
_WHITESPACE_REGEX = r"\s*"
_SECTION_START_PATTERN = re.compile(rf"{_WHITESPACE_REGEX}(\w+):")
_SUB_SECTION_PATTERN = re.compile(rf"{_WHITESPACE_REGEX}(\w+)( \(.*\))?:")
_SECTION_END_PATTERN = re.compile(rf"{_WHITESPACE_REGEX}$")


def _get_sections(lines: Iterable[str]) -> Iterator[_Section]:
    """Retrieve all the sectiond from the docstring.

    A section start is indicated by a line that starts with zero or more whitespace followed by a
    word and then a colon.
    A section end is indicated by a line with just whitespace or that there a no more lines in the
    docstring.
    A sub-section is indicated by a line with zero or more whitespace characters, followed by a
    word, optionally followed by arbitrary characters enclosed in brackets followed by a colon.

    Args:
        lines: The lines of the docstring.

    Yields:
        All the sections in the docstring.
    """
    lines = iter(lines)

    with contextlib.suppress(StopIteration):
        while True:
            section_name = next(
                filter(None, (_SECTION_START_PATTERN.match(line) for line in lines))
            ).group(1)
            section_lines = itertools.takewhile(
                lambda line: _SECTION_END_PATTERN.match(line) is None, lines
            )
            sub_section_matches = (_SUB_SECTION_PATTERN.match(line) for line in section_lines)
            sub_sections = (match.group(1) for match in sub_section_matches if match is not None)
            yield _Section(name=section_name, subs=tuple(sub_sections))


def parse(value: str) -> Docstring:
    """Parse a docstring.

    Args:
        value: The docstring to parse.

    Returns:
        The parsed docstring.
    """
