"""Parse a docstring to retrieve the sections and sub-sections."""

from __future__ import annotations

import contextlib
import itertools
import re
from typing import Iterable, Iterator, NamedTuple


class _Section(NamedTuple):
    """Represents a docstring section.

    Attrs:
        name: Short description of the section.
        subs: The names of the sub-sections included in the section. None if the section has no
            sub-sections.
    """

    name: str
    subs: tuple[str, ...]


class Docstring(NamedTuple):
    """Represents a docstring.

    Attrs:
        args: The arguments described in the docstring. None if the docstring doesn't have the args
            section.
        args_sections: All the arguments sections.
        attrs: The attributes described in the docstring. None if the docstring doesn't have the
            attrs section.
        returns: Whether the docstring has the returns section.
        returns_sections: All the returns sections.
        yields: Whether the docstring has the yields section.
        raises: The exceptions described in the docstring. None if the docstring doesn't have the
            raises section.
    """

    args: tuple[str, ...] | None = None
    args_sections: tuple[str, ...] = ()
    attrs: tuple[str, ...] | None = None
    returns: bool = False
    returns_sections: tuple[str, ...] = ()
    yields: bool = False
    raises: tuple[str, ...] | None = None


_SECTION_NAMES = {
    "args": {"args", "arguments", "parameters"},
    "attrs": {"attributes", "attrs"},
    "returns": {"return", "returns"},
    "yields": {"yield", "yields"},
    "raises": {
        "raises",
    },
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


def _get_section_by_name(name: str, sections: Iterable[_Section]) -> _Section | None:
    """Get the section by name.

    Args:
        name: The name of the section.
        sections: The sections to retrieve from.

    Returns:
        The section or None if it wasn't found.
    """
    sections = iter(sections)
    return next(
        (section for section in sections if section.name.lower() in _SECTION_NAMES[name]),
        None,
    )


def _get_all_section_names_by_name(name: str, sections: Iterable[_Section]) -> Iterator[str]:
    """Get all the section names in a docstring by name.

    Args:
        name: The name of the section.
        sections: The sections to retrieve from.

    Yields:
        The names of the sections that match the name.
    """
    sections = iter(sections)
    yield from (
        section.name for section in sections if section.name.lower() in _SECTION_NAMES[name]
    )


def parse(value: str) -> Docstring:
    """Parse a docstring.

    Args:
        value: The docstring to parse.

    Returns:
        The parsed docstring.
    """
    sections = list(_get_sections(lines=value.splitlines()))

    args_section = _get_section_by_name("args", sections)
    attrs_section = _get_section_by_name("attrs", sections)
    raises_section = _get_section_by_name("raises", sections)

    return Docstring(
        args=args_section.subs if args_section is not None else None,
        args_sections=tuple(_get_all_section_names_by_name(name="args", sections=sections)),
        attrs=attrs_section.subs if attrs_section is not None else None,
        returns=_get_section_by_name("returns", sections) is not None,
        returns_sections=tuple(_get_all_section_names_by_name(name="returns", sections=sections)),
        yields=_get_section_by_name("yields", sections) is not None,
        raises=raises_section.subs if raises_section is not None else None,
    )
